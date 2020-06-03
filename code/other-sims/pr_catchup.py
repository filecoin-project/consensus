import numpy as np
import time
from math import floor, log
import multiprocessing as mp


## TO DO: rewrite the groupedfork thing

def calculate_pr_catchup(nh, na, height, e, sim, min_length):
    # ntot - total number of players
    ntot = na + nh
    # p - probability of one player to win
    p = float(e) / float(1 * ntot)



    # win_ec - probability of catching up
    win_ec = 0
    # forkwin - list of whether the adversary can succeed an attack of length
    # i for each i in eight ( 1 if not 0 if yes)
    forkwin = [0.]*height
    # Run simulations
    forks = []
    for i in range(sim):
        # Simulate leaders of a chain of specific height
        # ch - list of number of honest leaders per slot
        ch = np.random.binomial(nh, p, height)
        # ca - list of number of honest leaders per slot
        ca = np.random.binomial(na, p, height)

        # First attack: Normal catchup
        # Run through the chain until the attacker's chain is heavier
        # or when we run out of time

        # ind - current height of the simulation
        ind = 1
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
        ch_before = np.random.binomial(nh, p, height)
        # ca_before - list of number of adversarial leaders per slot before attack starts
        ca_before = np.random.binomial(na, p, height)

        # the slot 0 for ca_before and ch_before corresponds to the case before the
        # catch up starts, so by definition a slot where the adversary is not elected leader
        # (as the catch up starts after the epoch boundary has finished)
        # so we assume ca[0] = 0 by definition (or simply ignore ca[0])
        adv = 0
        if ca_before[1] > 1: # the attack works only if the adversary has at
        # least two blocks in slot 1
            adv_start =   ca[1] # this is what the adversary gains by doing HS
            h_start =     1     + ch_before[0]/2 # this is what the honest gains
            # the one stands for the block that the adversary used for the epoch boundary
            # and ch_before[0]/2 corresponds to the fact that the honest power is split in two
            # (for now we consider the case of two forks only)

            if adv_start > h_start: #if this is negative, there is no point doing this attack
            # the attack above is trictly better
                # the adver
                adv = adv_start - h_start #this is the advantage that the adversary gains by
                #doing headstart compared to simply doing the attack

            # to do the attack one step before we need to check whether it's worth it:
            adv_start = ca_before[2] 
            h_start = 1 + ch_before[1]/2 + 1 + ch_before[0]/2 # we add to the honest advantage
            # the blocks from slot -1 and -2 that the adversary had to ignore
            if adv_start - h_start > adv:
                #do attack
                adv = adv_start - h_start #this is the advantage of doing headstart from two blocks before
        suma += adv # we add the advantage gained by HS to the adversarial weight
        # for each slot, we check if the adversary can succeeds its attack,
        # i.e., if the adversary has a chain with more blocks
        for ind in range(height):
        #while sumh > suma and ind < height:
            sumh += ch[ind]
            suma += ca[ind]
            if suma >= sumh: #if the adversary wins
                forkwin[ind] += 1. #add one to forkwin at height ind
                #if ind>=min_length:

                ### need to "separate different simu here"
                longestfork.append(ind+1) #this will give us the
                    #list of consecutive successful attacks of length at least min_length
        forks.append(longestfork)
    return  np.array(forkwin)/float(sim),forks

# sim - number of simulations
# num_cycles - number of repeated attacks
def calculate_max_total_catchup(sim, num_cycles, forks, min_length):
    # need to filter longest fork with min_length
    longestfork = []

    for fork in forks:
        if fork[-1]>= min_length: #check if there exists a fork of length at least min_length
            #take the first value greater or equal than min_length
            value = next(val for  val in fork if val >= min_length) 
            longestfork.append(value)
    # f - variable used to make sure we don't count the "same" fork twice
    # need to stop before the end of the longest fork
    # if it is not a multiple of num
    stop = int(floor(sim/num_cycles)*num_cycles)

    # Calculate the max consecutive catchup, by looking at num_cycles consecutive forks
    groupedfork = [sum(longestfork[x : x+num_cycles]) for x in range(0, stop, num_cycles)]
    return max(groupedfork)

if __name__ == '__main__':
    nh = 67
    na = 33
    height = 150
    e = 5
    sim = 10
    min_length = 10

    # Function to execute on multiple threads
    def single_cpu (sim):
        pr_catchup, forks = calculate_pr_catchup(nh, na, height, e, sim, min_length)
        num_cycles = int(log(2**-30) / log(pr_catchup))
        num_cycles = [int(log(2**-30) / log(pr)) for pr in pr_catchup]
        max_total_catchup = []
        for num_cycle in num_cycles:
            max_total_catchup.append(calculate_max_total_catchup(sim, num_cycle, forks,min_length))
        return max_total_catchup, num_cycles, pr_catchup, forks

    # start_time - useful for debugging
    start_time = time.time()

    pool = mp.Pool(mp.cpu_count())
    print("CPUs", mp.cpu_count())
    results = pool.map(single_cpu, [sim] * mp.cpu_count())
    pool.close()

    # Find best simulation and return values
    best_sim_index = np.argmax([result[0] for result in results])
    max_total_catchup, num_cycles, pr_catchup, longestfork = results[best_sim_index]

    print("PrCatchup", pr_catchup)
    print("Num Cycles", num_cycles)
    print("Max number of num cycles catchup", max_total_catchup)

    print(
        "Average:", np.average(longestfork),
        "Median:", np.median(longestfork),
        "Worst length:", max(longestfork))

    print("--- %s seconds ---" % (time.time() - start_time))
