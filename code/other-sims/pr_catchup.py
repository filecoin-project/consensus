import numpy as np
import time
from math import floor, log
import multiprocessing as mp

def calculate_pr_catchup(nh, na, height, e, sim, min_length):

    # ntot - total number of players
    ntot = na + nh
    # p - probability of one player to win
    p = float(e) / float(1 * ntot)

    # longestfork - list of all the lengths of the minimum catchup
    # lenghts of the forks as soon as they are successful
    longestfork =[]

    # win_ec - probability of catching up
    win_ec = 0
    # forkwin - list of whether the adversary can succeed an attack of length
    # i for each i in eight ( 1 if not 0 if yes)
    forkwin = [0]*height
    # Run simulations
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
       

        # for each slot, we check if the adversary can succeeds its attack,
        # i.e., if the adversary has a chain with more blocks
        for ind in range(height)
        #while sumh > suma and ind < height:
            sumh += ch[ind]
            suma += ca[ind]
            if suma>=sumh: #if the adversary wins
                forkwin[height]=1
                if ind >= min_length:
                    longestfork.append(ind)


        # Second attack: Headstart catchup (if attacker didn't win so far)
        # The attack starts if
        # TODO: perform headstart attack a block earlier

        ## to do: check if there is an advantage in doing
        ## headstart from before and if yes add it to sum_a
        if win == 0 and ca[0] > 1 :
            # ch_before - list of number of honest leaders per slot before attack starts
            ch_before = np.random.binomial(nh, p, height)
            # ca_before - list of number of honest leaders per slot before attack starts
            ca_before = np.random.binomial(na, p, height)


            #the slot 0 for ca_before and ch_before corresponds to the case before the
            # catch up starts, so by definition a slot where the adversary is not elected leader
            # so we assume ca[0] = 0 by definition (or simply ignore ca[0])
            if ca[1] > 1: # the attack works only if the adversary has at
            # least two blocks in slot 1
                adv_start =   ca[1] 
                h_start =     1     + ch_before[0]/2
                if adv_start > h_start: #if this is negative, there is no point doing this attack
                # the attack above is trictly better
                    # the adver

                # to do the attack one step before we need to check whether it's wprth it:
                adv_start = ca_before[2] 
                h_start = 1 + ch_before[1]/2 + 1 + ch_before[0]/2
                if adv_start >h_start:
                    #do attack

            #at round 0 the power of honest miners is still split between two chains
            #after that it goes all back to one chain
            #the adversary used all the blocks it withheld in period j-1
            #(all of them minus 1 that it used to maintain the forks)

            ind = 3
            while sumh > suma and ind < height:
                #as soon as adversary catches up with honest chain, assume
                #it can create a fork again
                sumh += ch[ind]
                suma += ca[ind]
                ind += 1
                if ind == height and sumh > suma:
                    #we have reach the end of the attack
                    #and adversary has not catch up
                    win =0
                    break

        # ind < height means that the attacker has won
        # the probability of winning ind > height is very low
        # if ind < height:
        #     # ensure that the miners' fork is at least of min_length
        #     # TODO: this won't cover the actual request from @nicola
        #     win_ec+=1
        #     # Keep track of the fork as soon as it's successful
        #     longestfork.append(ind)


    return float(win_ec)/float(sim), longestfork

# sim - number of simulations
# num_cycles - number of repeated attacks
def calculate_max_total_catchup(sim, num_cycles, longestfork):
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
    sim = 10000
    min_length = 10

    # Function to execute on multiple threads
    def single_cpu (sim):
        pr_catchup, longestfork = calculate_pr_catchup(nh, na, height, e, sim, min_length)
        num_cycles = int(log(2**-30) / log(pr_catchup))
        max_total_catchup = calculate_max_total_catchup(sim, num_cycles, longestfork)
        return max_total_catchup, num_cycles, pr_catchup, longestfork

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
