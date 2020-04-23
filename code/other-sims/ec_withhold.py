import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pdb
import math
import json
import calendar
import time
from scipy.stats import binom
import operator as op
from functools import reduce


print "Takes around 25 mins..."
# only set to True if running for a single expected_blocks_per_round
store_output = True
#####
## System level params
#####
lookbacks = [0] # [k for k in range(0, 11)] + [k for k in range(15, 105, 5)]
alphas = [.1, .33]
# alphas = [k/100.0 for k in range(2, 52, 2)]
rounds_back = []
# rounds_back = range(5, 105, 10)
total_qual_ec = []
total_qual_nohs = []
total_qual_nots = []
miners = 1000
sim_rounds = 5000
e_blocks_per_round = [1, 5]
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
wBlocksFactorTransitionConst = 350
wStartPunish = 5
wBlocksFactor = "wBlocksFactorTransitionCost*(log2((1-alpha)*networkSize(r))/(1-alpha))"
wForkFactor = "1 for k > E[X] - stddev[X]; CDF(X, k) otherwise"

#####
## Helper fns
#####

def cdf(k, n, p):
    _sum = 0
    for i in range(k + 1):
        _sum += ncr(n, i)*(p**i)*((1-p)**(n-i))
    return _sum

def ncr(n, r):
    r = min(r, n-r)
    numer = reduce(op.mul, range(n, n-r, -1), 1)
    denom = reduce(op.mul, range(1, r+1), 1)
    return numer / denom

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
        return advCount > 0 and advCount >= honCount
    else:
        # for EC, makes sense
        # for NOTS, no need to check either: you'll be tied at worst, just launch attack anyways
        return advCount > 0



def get_settings():
    params = {}
    params["lookbacks"] = lookbacks
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
            "wForkFactor": wForkFactor,
            "wStartPunish": wStartPunish,
            "wBlocksFactor": wBlocksFactor
            }
    return params

def store_output(succ_atk, succ_targ, total_qual, e, lb):
    params = get_settings()
    params["current_e"] = e
    params["current_lb"] = lb
    output = {}
    for el in sim_to_run:
        output[Sim.rev[el]] = {
                "conv": [{"alpha": alpha, "result": [{"rounds_back": k, "prob": prob} for k, prob in zip(rounds_back, succ_atk[el][idx])]} for idx, alpha in enumerate(alphas)],
                "target": [{"alpha": alpha, "result": [{"target": targ, "rounds": res} for targ, res in zip(target_conf, succ_targ[el][idx])]} for idx, alpha in enumerate(alphas)],
                "qual": [{"alpha": alpha, "qual": qual} for alpha, qual in zip(alphas, total_qual[el])]
                }

    outputDoc = "./monte/sim_results_{ts}.json".format(ts=calendar.timegm(time.gmtime()))
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
        # How often will adversarial attack succeed across rounds_back?
        self.succ_atk = {k: [] for k in sim_to_run}
        # and for specific target
        self.succ_targ = {k: [] for k in sim_to_run}

    def reset_sim(self):
        # type -> int
        self.nostart = {k: 0 for k in sim_to_run}
        self.noend = {k: 0 for k in sim_to_run}
        # type -> array -> int
        self.lengths = {k: [] for k in sim_to_run}
        self.launched = {k: [] for k in sim_to_run}
        self.quality = {k: [] for k in sim_to_run}
        blocksStdDev = math.sqrt(self.e*(1-self.p))
        self.forkFactorCutoff = self.e - blocksStdDev
        self.CDFMemoization = {}

    def wForkFactor(self, blocksR):
        if blocksR > self.forkFactorCutoff:
            return 1
        # super inefficient
        # return binom.cdf(blocksR, self.e*miners, self.p)
        if blocksR not in self.CDFMemoization.keys():
            self.CDFMemoization[blocksR] = cdf(blocksR, self.e*miners, self.p)
        return self.CDFMemoization[blocksR]

    def wBlocksFactor(self, power):
        return  wBlocksFactorTransitionConst*(math.log((1.0-self.alpha)*power, 2)/(1.0-self.alpha))
    
    def wPowerFactor(self, power):
        return math.log(power, 2)

    def new_wt(self, old_wt, numBlocks, power, nulls, supp=0):
        # supp will be added weight for eg headstart
        if wt_fn:
            return old_wt + self.wForkFactor(numBlocks)*(self.wPowerFactor(power) + self.wBlocksFactor(power)*(numBlocks + supp))
        else:
            return old_wt + numBlocks + supp


    def run(self):
        # state gets too funky if doing both. Only test one set of top level vars at a time
        assert(len(e_blocks_per_round) == 1 or len(lookbacks) == 1)
        for e in e_blocks_per_round:
            self.reset_top_level()

            # equal sized miners: worst case
            self.p = e/float(1*miners)
            self.e = e

            for lb in lookbacks:
                # below reset would break if both e and lh are multiple values
                self.reset_top_level()
                self.lb = lb
                
                for alpha in alphas:
                    self.alpha = alpha
                    self.reset_sim()
                    for i in range(num_sims): 
                        for sim in sim_to_run:
                            self.run_sim(sim)

                    self.aggr_alpha_stats()
                self.output_full_stats()
        
        # print params to make results reproducible
        params = get_settings()
        print json.dumps(params, indent=4)
        
    def output_full_stats(self):
        ### Prettify for output
        print "\nConvergence"
        for el in sim_to_run:
            assert(len(self.succ_atk[el]) == len(alphas))
            assert(len(self.succ_targ[el]) == len(alphas))
        
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
            store_output(self.succ_atk, self.succ_targ, self.total_qual, self.e, self.lb)

    def aggr_alpha_stats(self):

        print "\nAttacker power alpha: {alpha}%, num of rounds: {sim_rounds}, num of sims: {sims}, lookahead: {la}, expected blocks per round: {e}".format(alpha=self.alpha*100, sims=num_sims, sim_rounds=sim_rounds, la=self.lb, e=self.e)
        
        # statement: the median is the distance such that an attacker creates a fork 50% of the time.
        # Q1: how often can the attacker create a fork from the average?
        
        succ_atk_alpha = {k: [] for k in sim_to_run}
        succ_targ_alpha = {k: [] for k in sim_to_run}
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
                succ_targ_alpha[el].append(rounds)
            # what is confidence at various ranges?
            for lookback in rounds_back:
        	likelihood = confidence_of_k(lookback, self.lengths[el])
       	        print "{_type}:              k {avg} will succeed {num}".format(_type=_type, avg=lookback, num=likelihood)
        	succ_atk_alpha[el].append(likelihood)
        
        # store across alphas
        for el in sim_to_run:
            assert(len(succ_atk_alpha[el]) == len(rounds_back))
            self.succ_atk[el].append(succ_atk_alpha[el])
            assert(len(succ_targ_alpha[el]) == len(target_conf))
            self.succ_targ[el].append(succ_targ_alpha[el])
            # Quality is not dependent on lookback, any successful attack will do it so we take avg
            self.total_qual[el].append(np.average(self.quality[el]))
            # plot for a given alpha
            # plt.plot(rounds_back, succ_atk_alpha[el])
        # plt.xlabel("blocks behind")
        # plt.ylabel("chance of success")
        # plt.title("Confirmation time for alpha={alpha}".format(alpha=self.alpha))
        # fig1 = plt.gcf()
        # fig1.savefig("{alpha}-confirmationTime.png".format(alpha=self.alpha), format="png")
        # plt.clf()
        
    def run_sim(self, _type):
    	# result of flipping a coin honest_miners/adv_miners times, tested 1000 times.
    	# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
    	# put another way, it represents choice between longest honest and longest adv, and not between longest honests
        hon_miners = round((1-self.alpha)*miners)
        adv_miners = round(self.alpha*miners)
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
        weight_adv = 0
        weight_hon = 0
        # for quality, we are not looking at chains together but rather which has its blocks counted
        tot_blocks_adv = 0
        tot_blocks_hon = 0
        pot_blocks_adv = 0
        pot_blocks_hon = 0
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
                power *= (1 + powerIncreasePerRound)
            
            # start attack
    	    if start < 0 and should_launch_attack(_type, start, j, chain_hon[idx]):
                # reset since atkr will compare to this to time end
                weight_adv = self.new_wt(weight_hon, j, power, adv_nulls, chain_hon[idx])
                weight_hon = self.new_wt(weight_hon, chain_hon[idx], power, hon_nulls)
                pot_blocks_adv = tot_blocks_adv + j
                pot_blocks_hon = tot_blocks_hon + chain_hon[idx]
                
    		start = idx
                num_atks += 1

    	    # ongoing attack
            elif start >= 0:
            
                # update weights
                weight_hon = self.new_wt(weight_hon, chain_hon[idx], power, hon_nulls)
    	        weight_adv = self.new_wt(weight_adv, j, power, adv_nulls)
                pot_blocks_adv = pot_blocks_adv + j
                pot_blocks_hon = pot_blocks_hon + chain_hon[idx]
            
                # should it be ended?
                if should_end_attack(weight_hon, weight_adv, chain_hon[idx+1:], chain_adv[idx+1:], self.lb):
                    end = idx
               
                    # check to see who won
                    # in case not equal, then attacker took too much risk and failed
                    if weight_hon != weight_adv:
                        assert(weight_hon > weight_adv)
                        tot_blocks_hon = pot_blocks_hon
                    else:
                        # else, atk pays off (we assume atker has better connectivity and wins ties)
                        tot_blocks_adv = pot_blocks_adv
                        # successful fork
                        weight_hon = weight_adv
                        if _type == Sim.EC:
                            # in case of loss, EC still gets first block will be counted
                            tot_blocks_hon += chain_hon[start]

                    # compare to current longest successful attack in this sim.
                    if end - start > max_len:
                        max_len = end - start
    	            # reset to run attack again
                    start = -1
                    end = -1

                # attack didn't end and sim ends
    	        elif end < 0 and idx == sim_rounds - 1:
                    self.noend[_type] += 1
	    	    # stop attack here successfully (conservative). account for max (could have gone on)
                    tot_blocks_adv = pot_blocks_adv
                    weight_hon = weight_adv
                    if _type == Sim.EC:
                        # in case of loss, EC still gets first block will be counted
                        tot_blocks_hon += chain_hon[start]
                    if sim_rounds - start > max_len:
                        max_len = sim_rounds - start

            else:
                # this is the case we end while not in attack
                assert(start < 0)

                # attack never started and sim ends
                if start == -2 and idx == sim_rounds - 1:
                    self.nostart[_type] += 1
                
                # update all counts
                tot_blocks_adv += j
                tot_blocks_hon += chain_hon[idx]
                weight_hon = self.new_wt(weight_hon, chain_hon[idx], power, hon_nulls)
                # adv weight doesn't matter here since it kicks off as weight_hon
        
        # at end of sim, retain stats
        # longest atk, num launched, adv earnings (qual)
        self.lengths[_type].append(max_len)
        self.launched[_type].append(num_atks)
        self.quality[_type].append(float(tot_blocks_adv)/(tot_blocks_hon + tot_blocks_adv))

mc = MonteCarlo()
mc.run()
