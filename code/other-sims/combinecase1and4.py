import numpy as np
import time
from math import floor, log
import multiprocessing as mp
from operator import add
from scipy.stats import binom as bi
import math

## TO DO I feel we should also to the headstart (i.e. case 4) in the same attack



## Improvement:
# compute the Pr_catch up on all processors, then take the average
# and compute num_cycles and max_tot_catchup after this

# two chain - variable that captures if we assume the adversary can only maintains
# two chains or potentially more (thus splitting the honest power even more)
twochains = 0

# epochboundarylength - capture length of epoch boundary 
# (needed for "headstart" catchup)
epochboundarylength = 20 #gross approximation we are more or less guaranteed of having one null blocks

def calculate_pr_catchup(nh, na, height, e, sim):
    # ntot - total number of players
    ntot = na + nh
    # p - probability of one player to win
    p = float(e) / float(1 * ntot)

    # win_ec - probability of catching up
    win_ec = 0

    # forkwin - list of whether the adversary can succeed an attack of length
    # i for each i in eight ( 1 if not 0 if yes)
    forkwin = [0.]*height
    
    # forks - list of list of all forks iin each simulation
    forks = []

    np.random.seed()
    # Run simulations
    for i in range(sim):
        # Simulate leaders of a chain of specific height
        # ch - list of number of honest leaders per slot
        ch = np.random.binomial(nh, p, height)
        # ca - list of number of honest leaders per slot
        ca = np.random.binomial(na, p, height)

        # forks_in_that_sim - list of fork in that simulation
        forks_in_that_sim = []

        # win : Boolean - keeps track of whether the attacker succeeds
        # it has value 1 if it's attack succeeds, 0 if it does not
        win = 1

        # sumh - weight of honest chain
        sumh = 0
        # sumh - weight of dishonest chain
        suma = 0

        ## We start by determining what is the best strategy for the adversary:
        # to start the attack at round 0 when the fork starts or to start the attack 'before'
        # the fork by doing a headstart at round -1 or -2 etc...


        # ch_before - list of number of honest leaders per slot before attack starts
        # I am not sure how far back we should go in time (this depends of the
        # length of epoch boundary)
        ch_before = np.random.binomial(nh, p, epochboundarylength)
        # ca_before - list of number of adversarial leaders per slot before attack starts
        ca_before = np.random.binomial(na, p, epochboundarylength)

        # the slot 0 for ca_before and ch_before corresponds to the case before the
        # catch up starts, so by definition a slot where the adversary is not elected leader
        # (as the catch up starts after the epoch boundary has finished)
        # so we assume ca[0] = 0 by definition (or simply ignore ca[0])

        # adv - captures the advantage of the adversary when starting it's catchup before slot zero
        adv = 0 

        for j in range(1,epochboundarylength):
            #we can only do the headstart if there was more than one block
            #created by the adversary at that height
            # adv_start - advantage in adverssrial chain
            adv_start = 0
            # h_start - advantage in honest chain
            h_start = 0

            # if the adversary has more than one block at this epoch,
            # do the attack (this is a bit weird bc we assume we are in the epoch boundary so the
            # adversary should have one block otherwise the epoch boundary stops)
            if ca_before[j]>0:
            	# in its chain the adversary uses all of its block
                adv_start = ca_before[j]

                # the honest chain uses only one of the adversarial block
                # that was created to do the epoch boundary
                h_start = 1 
                # at each height eight less than j, adv uses all its blocks in its alternative chain
                # if you want to do the HS + EB you need to use one block at each height (EB) and save the others
                # for HS
                # so for every height where you have>1 more than one block you actually win
                # an advantage
                for k in range(1,j):
                    if ca_before[k]>0:
                        adv_start+=ca_before[k]
                        if twochains:
                            h_start += 1 + ch_before[k]/2 #divide by two because we assume chain split in two for now
                        else:
                            h_start += 1+ min(1,ch_before[k]) # assume two blocks at each height
                            # or one if honest don't have leaders
            if adv_start - h_start > adv:# start HS  where you have the more adv
                adv = adv_start - h_start
        ## try to start from "start"
        # not completely sure about this method (precisely the removing zeros)
        ca_before_notnull = [c for c in ca_before if c>0 ]
        
        ch_before_notnull = [1 + min(1,ch_before[k]) for k in range(len(ca_before_notnull))]
        #ch_before_notnull = [1.67 for k in range(len(ca_before_notnull))]

        adv_start = sum(ca_before_notnull) + 1
        h_start = sum(ch_before_notnull)
        if adv_start - h_start > adv:# start HS  where you have the more adv
            adv = adv_start - h_start
        # wither use HS to gain an advantage or not and start
        if adv >0:
        	suma += adv # we add the advantage gained by HS to the adversarial weight
        	sumh += 1 # number of block in honest chain at height zero

        # for each slot, we check if the adversary can succeeds its attack,
        # i.e., if the adversary has a chain with more blocks


        # maxfork - tracks the longest fork the adversary can do
        maxfork = 0
        for ind in range(height):
            sumh += ch[ind]
            suma += ca[ind]
            if suma >= sumh: #if the adversary wins
                #the adversary was able to create a fork of length ind +1 (because ind starts at zero)
                maxfork = ind+1 #

                ### if forks succeed, add it to forks_in_that_sim
                # we add +1 because the index starts at zero (the length
                # of the fork in that case is one not zero)
                forks_in_that_sim.append(ind+1) #this will give us the
                #list of consecutive successful attacks of length at least min_length
            # update forkwin with ones up to maxfork

        # forkwin - list of whether the adversary can succeed an attack of length
        # i for each i in eight ( 1 if not 0 if yes)
        # add +1 for every successulf attacks
        #forkwin += [1]*maxfork + [0]*(height-maxfork)
        forkwin = list( map(add, forkwin, [1]*maxfork + [0]*(height-maxfork)) )
        
        forks.append(forks_in_that_sim)
    # return an array of probability of doing a catch up of length j for each j
    # and the list of the length of all the fork created in each simulation
    return  np.array(forkwin)/float(sim),forks

# sim - number of simulations
# num_cycles - number of repeated attacks
def calculate_max_total_catchup(sim, num_cycles, forks):
    # need to filter longest fork with min_length
    height = len(num_cycles)

    longestfork = {k : [] for k in range(1,height)}

    for fork in forks:
        for min_length in range(1,height):
            if fork:
                if fork[-1]>= min_length: #check if there exists a fork of length at least min_length
                #take the first value greater or equal than min_length
                    value = next(val for  val in fork if val >= min_length) 
                    longestfork[min_length].append(value)

    # totcatchup - keep track of total catch up length for each min_length
    totcatchup =[]
    for key,value in longestfork.items():
        num_cycle = num_cycles[key]
        if num_cycle >0:
        	# stop - need to stop before the end of the longest fork
 			# if it is not a multiple of num
            stop = int(floor(sim/num_cycle)*num_cycle)
            ll = [sum(value[x : x+num_cycle]) for x in range(0, stop, num_cycle)]
        # Calculate the max consecutive catchup, by looking at num_cycles consecutive forks
            if ll: maxgroupedfork = max(ll)
            else: maxgroupedfork = 0
            totcatchup.append(maxgroupedfork)
        else:
            totcatchup.append(0)
    return totcatchup


def MaxTotalBeforeNull(sim,num_cycles ,nullProb = .188): # 0.18 is the proba of having one slot null
    maxtotBN= []
    for targetNulls in num_cycles:
    # This is a simple CDF of a binomial (sum of binom probas up to x).
    # each round has a proba p = advNullRound() of being null for the adversary
    # We are looking for n such that n trials will yield at least targ successes with high proba
    # which is to say n s.t. 1 - CDF(targ, n, p) > 1 - s => CDF(targ, n, p) < s
        totalRounds = targetNulls - 1
        sumToTargN = 1
        while sumToTargN >= s:
            totalRounds += 1
            sumToTargN = bi.cdf(targetNulls - 1, totalRounds, nullProb) 
        maxtotBN.append(totalRounds)
    return maxtotBN

if __name__ == '__main__':
    nh = 67
    na = 33
    height = 50
    e = 5
    sim = 10000
    #min_length = 10
    s = 2**-30

    # Function to execute on multiple threads
    def single_cpu (sim):
        pr_catchup, forks = calculate_pr_catchup(nh, na, height, e, sim)
        #num_cycles = int(log(2**-30) / log(pr_catchup))
        #print(pr_catchup)
        num_cycles = [int(log(2**-30) / log(pr)) if pr>0 else 0 for pr in pr_catchup ]
        max_total_catchup=calculate_max_total_catchup(sim, num_cycles, forks)
        return max_total_catchup, num_cycles, pr_catchup
    # start_time - useful for debugging
    start_time = time.time()

    pool = mp.Pool(mp.cpu_count())
    print("CPUs", mp.cpu_count())
    results = pool.map(single_cpu, [sim] * mp.cpu_count())
    #results = single_cpu(sim)
    pool.close()
    # for each length we want to get the worst (max) longest fork
    max_total_catchup_overallsims = [0]*height
    for i in range(height-1):
        for result in results:
            if result[0][i]>max_total_catchup_overallsims[i]:
                max_total_catchup_overallsims[i] = result[0][i]
    # Find best simulation and return values
    #best_sim_index = np.argmax([result[0] for result in results])
    
    pr_catchup = results[0][2]
    num_cycles = results[0][1]

    #max_total_catchup, num_cycles, pr_catchup, longestfork = results[best_sim_index]
    
    print("PrCatchup", pr_catchup)
    print("Num Cycles", num_cycles)
    print("Max number of num cycles catchup", max_total_catchup_overallsims)
    maxtotBN = MaxTotalBeforeNull(sim,num_cycles)
    attack_total = list( map(add, max_total_catchup_overallsims, maxtotBN) )
    print("Max Before Null", maxtotBN)
    # print(
    #     "Average:", np.average(longestfork),
    #     "Median:", np.median(longestfork),
    #     "Worst length:", max(longestfork))
    print("Total attack", attack_total)
    print("--- %s seconds ---" % (time.time() - start_time))
