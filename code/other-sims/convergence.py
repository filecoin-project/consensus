import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pdb
import math
import json
import calendar
import time

print "Takes around 25 mins..."
# only set to True if running for a single expected_blocks_per_round
store_output = False
#####
## System level params
#####
lookahead = 0
# alphas = [k/100.0 for k in range(2, 52, 2)]
alphas=[.3]
rounds_back = []
# rounds_back = range(5, 105, 10)
total_qual_ec = []
total_qual_nohs = []
total_qual_nots = []
miners = 10000
sim_rounds = 5000
e_blocks_per_round = [x for x in range(10)]
num_sims = 10000
# conf denom needs to be no bigger than number of sims (otherwise can't get that precision)
target_conf = [.0001]

## Model complex weighting fn? Based on observable wt fn params
wt_fn = False
# wt_fn = True
powerAtStart = 5000 # in PBs
powerIncreasePerDay = .025 # 2.5% per day for double power in 28 days (1,250 TB a day)
# assuming a 30 sec block time and uniform increase
RDS_PER_DAY = 86400./30
powerIncreasePerRound = powerIncreasePerDay/RDS_PER_DAY
wPunishFactor = .896
wStartPunish = 4
wBlocksFactor = 1.4281

#####
## Helper fns
#####

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    # hack to enumerate the elements
    enums['ks'] = range(len(sequential))
    enums['rev'] = reverse
    return type('Enum', (), enums)

Sim = enum('EC', 'NOHS', 'NOTS')
## What to run
sim_to_run = [Sim.EC]
# sim_to_run = [Sim.EC, Sim.NOHS, Sim.NOTS]

def confidence_of_k(target, array):
    _sum = 0.0
    for idx, i in enumerate(array):
        # attack will fail
    	if i < target:
            _sum += 1
    # attack succeeds
    return float(len(array) - _sum) / len(array) 

# because of EC's lookback param, adversary can effectively look ahead that many blocks to decide whether to release
# when honest party catches up: is this a real "catch up" or a temporary one?
def should_end_attack(honest_weight, adversarial_weight, honest_chain, adversarial_chain, lookahead):
    assert(len(honest_chain) == len(adversarial_chain))
    # no need to lookahead then, let's just compare the weights.
    if lookahead == 0:
        return adversarial_weight <= honest_weight

    if adversarial_weight > honest_weight:
        return False

    # if we're getting to end of sim, let's not look beyond the end.
    if len(honest_chain) < lookahead:
        lookahead = len(honest_chain)

    # If we are not, let's look ahead to make a choice
    for i in range(lookahead):
        honest_weight += honest_chain[i]
        adversarial_weight += adversarial_chain[i]
        # if at some point in the next lookahead blocks adversary takes over again, cancel the release and wait it out
        if adversarial_weight > honest_weight:
            return False
    # adversary can't take the risk of never getting back on top. Stop the attack.
    return True

def should_launch_attack(_type, start, advCount, honCount):
    if _type == Sim.NOHS:
        return advCount > 0 and start < 0 and advCount >= honCount
    else:
        # for EC, makes sense
        # for NOTS, no need to check either: you'll be tied at worst, just launch attack anyways
        return advCount > 0 and start < 0

def new_wt(old_wt, numBlocks, power, nulls, supp=0):
    # supp will be added weight for eg headstart
    if wt_fn:
        # edge cases at beg of chain + actual condition, skip last one
        if nulls >= wStartPunish:
            wNullFactor = wPunishFactor ** nulls
        else:
            wNullFactor = 1.
        return old_wt + wNullFactor*(math.log10(power) + wBlocksFactor*(numBlocks + supp))
    else:
        return old_wt + numBlocks + supp

def get_settings():
    params = {}
    params["lookahead"] = lookahead
    params["alphas"] = alphas
    params["rounds_back"] = rounds_back
    params["miners"] = miners
    params["sim_rounds"] = sim_rounds
    params["e_blocks_per_round"] = e_blocks_per_round
    params["num_sims"] = num_sims
    params["wt_fn"] = {
            "enabled": wt_fn,
            "powerAtStart": powerAtStart,
            "powerIncreasePerRound": powerIncreasePerRound,
            "wPunishFactor": wPunishFactor,
            "wStartPunish": wStartPunish,
            "wBlocksFactor": wBlocksFactor
            }
    return params

def store_output(succ_atk, total_qual):
    params = get_settings()
    output = {}
    for el in sim_to_run:
        output[Sim.rev[el]] = {
                "conv": [{"alpha": alpha, "result": [{"rounds_back": k, "prob": prob} for k, prob in zip(rounds_back, succ_atk[el][idx])]} for idx, alpha in enumerate(alphas)],
                "qual": [{"alpha": alpha, "qual": qual} for alpha, qual in zip(alphas, total_qual[el])]
                }

    outputDoc = "./monte/sim_results_{wt}_{lookahead}_{ts}.json".format(wt=wt_fn, lookahead=lookahead, ts=calendar.timegm(time.gmtime()))
    _json = {"params": params, "output": output}
    with open(outputDoc, 'w') as f:
        json.dump(_json, f, indent=4)

#####
## Sim runner
#####

class MonteCarlo:
    def __init__(self):
        self.reset_top_level()

    def reset_top_level(self):
        # What portion of block will adversary publish?
        self.total_qual = {k: [] for k in sim_to_run}
        # type -> alpha -> blocksback -> int
        # How often will adversarial attack succeed?
        self.succ_atk = {k: [] for k in sim_to_run}

    def reset_sim(self):
        # type -> int
        self.nostart = {k: 0 for k in sim_to_run}
        self.noend = {k: 0 for k in sim_to_run}
        # type -> array -> int
        self.lengths = {k: [] for k in sim_to_run}
        self.launched = {k: [] for k in sim_to_run}
        self.quality = {k: [] for k in sim_to_run}


    def run(self):
        for e in e_blocks_per_round:
            self.reset_top_level()

            # equal sized miners: worst case
            self.p = e/float(1*miners)

            for alpha in alphas:
                self.reset_sim()
                for i in range(num_sims): 
                    for sim in sim_to_run:
                        self.run_sim(sim, alpha)

                self.aggr_alpha_stats(alpha, e)
            self.output_full_stats()
        
        # print params to make results reproducible
        params = get_settings()
        print json.dumps(dic, indent=4)
        
    def output_full_stats(self):
        ### Prettify for output
        print "\nConvergence"
        for el in sim_to_run:
            assert(len(self.succ_atk[el]) == len(alphas))
        
            print Sim.rev[el]
            df = pd.DataFrame(self.succ_atk[el], columns=rounds_back, index=alphas)
            print df
        
        print "\nQuality"
        for el in sim_to_run:
            assert(len(self.total_qual[el]) == len(alphas))
        
            print Sim.rev[el]
            df = pd.DataFrame(self.total_qual[el], index=alphas)
            print df

        if store_output:
            store_output(self.succ_atk, self.total_qual)

    def aggr_alpha_stats(self, alpha, e):

        print "\nAttacker power alpha: {alpha}%, num of rounds: {sim_rounds}, num of sims: {sims}, lookahead: {la}, expected blocks per round: {e}".format(alpha=alpha*100, sims=num_sims, sim_rounds=sim_rounds, la=lookahead, e=e)
        
        # statement: the median is the distance such that an attacker creates a fork 50% of the time.
        # Q1: how often can the attacker create a fork from the average?
        
        succ_atk_alpha = {k: [] for k in sim_to_run}
        for el in sim_to_run:
            _type = Sim.rev[el]
            avg = np.average(self.lengths[el])
            med = np.median(self.lengths[el])
            num = len(self.lengths[el])
            nostart = self.nostart[el]
            noend = self.noend[el]
            launch = np.average(self.launched[el])
            avg_qual = np.average(self.quality[el])
            med_qual = np.median(self.quality[el])
            print "{_type}: num of attacks {num}; num didn't start {nostart}, didn't end {noend}, launched on avg: {launch}\n\tconv: avg {avg}; med {med}; \n\tqual: avg {avg_qual}; med {med_qual}".format(_type=_type, avg=avg, med = med, num = num, nostart = nostart, noend = noend, launch = launch, avg_qual = avg_qual, med_qual = med_qual)
           
            # how far back in order for us to reach target confidence?
            for conf in target_conf:
                rounds = np.percentile(self.lengths[el], (1-conf)*100)
                print "{_type}:            {rounds_back} rounds back, atk success is {targ}".format(_type=_type, rounds_back=rounds, targ=conf)
            # what is confidence at various ranges?
            for lookback in rounds_back:
        	likelihood = confidence_of_k(lookback, self.lengths[el])
       	        print "{_type}:              k {avg} will succeed {num}".format(_type=_type, avg=lookback, num=likelihood)
        	succ_atk_alpha[el].append(likelihood)
        
        # store across alphas
        for el in sim_to_run:
            assert(len(succ_atk_alpha[el]) == len(rounds_back))
            self.succ_atk[el].append(succ_atk_alpha[el])
            # Quality is not dependent on lookback, any successful attack will do it so we take avg
            self.total_qual[el].append(np.average(self.quality[el]))
            # plot for a given alpha
            # plt.plot(rounds_back, succ_atk_alpha[el])
        # plt.xlabel("blocks behind")
        # plt.ylabel("chance of success")
        # plt.title("Confirmation time for alpha={alpha}".format(alpha=alpha))
        # fig1 = plt.gcf()
        # fig1.savefig("{alpha}-confirmationTime.png".format(alpha=alpha), format="png")
        # plt.clf()
        
    def run_sim(self, _type, alpha):
    	# result of flipping a coin honest_miners/adv_miners times, tested 1000 times.
    	# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
    	# put another way, it represents choice between longest honest and longest adv, and not between longest honests
        hon_miners = round((1-alpha)*miners)
        adv_miners = round(alpha*miners)
        ch = np.random.binomial(hon_miners, self.p, sim_rounds)
    	ca = np.random.binomial(adv_miners, self.p, sim_rounds)
        if _type == Sim.NOTS:
    	    chain_hon = [1 if ch[i]>0 else 0 for i in range(len(ch))]
    	    chain_adv = [1 if ca[i]>0 else 0 for i in range(len(ca))]
        else:
            chain_hon = ch
            chain_adv = ca

        ####
        ## set Params
        ####
        atk_weight_adv = 0
        atk_weight_hon = 0
        # for quality, we are not looking at chains together but rather which has its blocks counted
        tot_weight_adv = 0
        tot_weight_hon = 0
        # flags to detect whether attack is running
        start = -2
        end = -1
        weight_at_start = -1
        # stats
        max_len = -1
        num_atks = 0
        # wt_fn
        power = powerAtStart
        adv_nulls = 0
        hon_nulls = 0

        ####
        ## Actual sim
        ####
    	for idx, j in enumerate(chain_adv):
            
            # track nulls across chains
            if wt_fn:
                hon_nulls = hon_nulls + 1 if chain_hon[idx] == 0 else  0
                adv_nulls = adv_nulls + 1 if j == 0 else 0
                power += powerIncreasePerRound
            
            # start attack
    	    if should_launch_attack(_type, start, j, chain_hon[idx]):
                # reset since atkr will compare to this to time end
                atk_weight_hon = new_wt(0, chain_hon[idx], power, hon_nulls)
                if _type == Sim.EC:
                    # both will be counted
                    atk_weight_adv = new_wt(0, j, power, adv_nulls, chain_hon[idx])
                    tot_weight_hon = new_wt(tot_weight_hon, chain_hon[idx], power, hon_nulls)
                else:
                    # no headstart
                    atk_weight_adv = new_wt(0, j, power, adv_nulls)
                
                tot_weight_adv = new_wt(tot_weight_adv, j, power, adv_nulls)
                
    		start = idx
                num_atks += 1
                # flag edge case which occurs for no hs
                # prevents attack from ending in the next round when both win at start
                if _type != Sim.EC:
                    weight_at_start = atk_weight_hon

    	    # end attack
            elif start >= 0 and should_end_attack(atk_weight_hon, atk_weight_adv, chain_hon[idx+1:], chain_adv[idx+1:], lookahead) and (weight_at_start < 0 or weight_at_start != atk_weight_hon):
                end = idx
                # attacker is sole winner (note that we assume attacker has better connectivity,
                # ie will always win in case of equal weighted chains -- this is a worst case)
                tot_weight_adv = new_wt(tot_weight_adv, j, power, adv_nulls)
                # compare to current longest successful attack in this sim.
                if end - start > max_len:
                    max_len = end - start
    	        # reset to run attack again
                start = -1
                end = -1

            # attack didn't start and sim ends
            elif start < -1 and idx == sim_rounds - 1:
                self.nostart[_type] += 1
                tot_weight_adv = new_wt(tot_weight_adv, j, power, adv_nulls)
                tot_weight_hon = new_wt(tot_weight_hon, chain_hon[idx], power, hon_nulls)

            # attack didn't end and sim ends
    	    elif start >= 0 and end < 0 and idx == sim_rounds - 1:
                self.noend[_type] += 1
	    	# stop attack here successfully. account for max (could have gone on)
                tot_weight_adv = new_wt(tot_weight_adv, j, power, adv_nulls)
                if sim_rounds - start > max_len:
                    max_len = sim_rounds - start

    	    # move forward each step
            else:
                atk_weight_hon = new_wt(atk_weight_hon, chain_hon[idx], power, hon_nulls)
    		atk_weight_adv = new_wt(atk_weight_adv, j, power, adv_nulls)
                # only add to honest weight if not under attack, otherwise honest party's blocks will be invalidated
                if start < 0:
                    tot_weight_hon = new_wt(tot_weight_hon, chain_hon[idx], power, hon_nulls) 
                tot_weight_adv = new_wt(tot_weight_adv, j, power, adv_nulls) 
        
        # at end of sim, retain stats
        # longest atk, num launched, adv earnings (qual)
        self.lengths[_type].append(max_len)
        self.launched[_type].append(num_atks)
        self.quality[_type].append(float(tot_weight_adv)/(tot_weight_hon + tot_weight_adv))

mc = MonteCarlo()
mc.run()
