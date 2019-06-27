import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd
import pdb

print "Takes around 25 mins..."

#####
## System level params
#####

lookahead = 0
alphas = [k/100.0 for k in range(2, 54, 2)]
# alphas=[k/100.0 for k in range(36, 54, 2)]
# alphas = [.49]
# rounds_back = range(5, 5250, 250)
rounds_back = range(5, 105, 10)
total_qual_ec = []
total_qual_nohs = []
total_qual_nots = []
miners = 10000
sim_rounds = 5000
e_blocks_per_round = 1.
# equal power for all miners
p = e_blocks_per_round/float(1*miners)
num_sims = 1000

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
# sim_to_run = [Sim.EC]
sim_to_run = [Sim.EC, Sim.NOHS, Sim.NOTS]

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

#####
## Sim runner
#####

class MonteCarlo:
    def __init__(self):
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
        for alpha in alphas:
            self.reset_sim()
            for i in range(num_sims): 
                for sim in sim_to_run:
                    self.run_sim(sim, alpha)
            
            self.aggr_alpha_stats(alpha)
        self.output_full_stats()

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

    def aggr_alpha_stats(self, alpha):

        print "\nAttacker power alpha: {alpha}%, num of rounds: {sim_rounds}, num of sims: {sims}, lookahead: {la}".format(alpha=alpha*100, sims=num_sims, sim_rounds=sim_rounds, la=lookahead)
        
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
            
            # how far back before we can be confident there is no ongoing attack?
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
        ch = np.random.binomial(hon_miners, p, sim_rounds)
    	ca = np.random.binomial(adv_miners, p, sim_rounds)
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
        qual_adv = 0
        qual_hon = 0
        # flags to detect whether attack is running
        start = -2
        end = -1
        weight_at_start = -1
        # stats
        max_len = -1
        num_atks = 0
       
        ####
        ## Actual sim
        ####
    	for idx, j in enumerate(chain_adv):
            
            # start attack
    	    if should_launch_attack(_type, start, j, chain_hon[idx]):
                # reset since atkr will compare to this to time end
                weight_hon = chain_hon[idx]
                if _type == Sim.EC:
                    # both will be counted
                    weight_adv = j + weight_hon
                    qual_hon += weight_hon
                else:
                    # no headstart
                    weight_adv = j
                
                qual_adv += j
                
    		start = idx
                num_atks += 1
                # flag edge case which occurs for no hs
                # prevents attack from ending in the next round when both win at start
                if _type != Sim.EC:
                    weight_at_start = weight_hon

    	    # end attack
            elif start >= 0 and should_end_attack(weight_hon, weight_adv, chain_hon[idx+1:], chain_adv[idx+1:], lookahead) and (weight_at_start < 0 or weight_at_start != weight_hon):
                end = idx
                # attacker is sole winner (note that we assume attacker has better connectivity,
                # ie will always win in case of equal weighted chains -- this is a worst case)
                qual_adv += j
                # compare to current longest successful attack in this sim.
                if end - start > max_len:
                    max_len = end - start
    	        # reset to run attack again
                start = -1
                end = -1

            # attack didn't start and sim ends
            elif start < -1 and idx == sim_rounds - 1:
                self.nostart[_type] += 1
                qual_adv += j
                qual_hon += chain_hon[idx]

            # attack didn't end and sim ends
    	    elif start >= 0 and end < 0 and idx == sim_rounds - 1:
                self.noend[_type] += 1
	    	# stop attack here successfully. account for max (could have gone on)
                qual_adv += j
                if sim_rounds - start > max_len:
                    max_len = sim_rounds - start

    	    # move forward each step
            else:
                weight_hon += chain_hon[idx]
    		weight_adv += j
                qual_hon += chain_hon[idx]
                qual_adv += j
        
        # at end of sim, retain stats
        # longest atk, num launched, adv earnings (qual)
        self.lengths[_type].append(max_len)
        self.launched[_type].append(num_atks)
        self.quality[_type].append(float(qual_adv)/(qual_hon + qual_adv))

mc = MonteCarlo()
mc.run()
