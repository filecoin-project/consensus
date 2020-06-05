import numpy as np
import time
from math import floor, log
import multiprocessing as mp
from operator import add


def find_proba(sim, nh,na,height,e):
    # win - count number of times the adversary wins the attack
    win = 0 
    longestfork =[]

    # ntot - total number of players
    ntot = na + nh
    p = float(e) / float(1 * ntot)
    np.random.seed()
    for i in range(sim):
        # Simulate leaders of a chain of specific height
        # ch - list of number of honest leaders per slot
        ch = np.random.binomial(nh, p, height)
        # ca - list of number of honest leaders per slot
        ca = np.random.binomial(na, p, height)

        w_h = 0
        w_a = 0
        j=0
        while j<height and ca[j]>0  : # the adversary maintains the eopoch boundary attack
        # as long as it is elected leader (j<height to avoid infinite loop)

            # for simplicity (and worst case scenario) we assume that every honest forks
            # is increasing by one at every block
            w_h+=1

            w_a+=ca[j]#adv adds all blocks possible to its private chain
            j+=1

        # once the epoch boundary has stop, we look at whether the selfish chain is 
        #heavier than the other chain and if so, the adversary wins
        if w_a>w_h:
            win+=1

            #if the attack is successful, add it to longest chain
            longestfork.append(j)
    return float(win)/float(sim), longestfork

def longest_fork(sim, longestfork,num): 
    stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num
    groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]  #we grouped the num
    #successive attacks together and sums them up to get the length of num successives attacks
    return max(groupedfork)


if __name__ == '__main__':
    nh = 67
    na = 33
    height = 60
    e = 5
    sim = 100000000
    #min_length = 10
    start_time = time.time()
    # Function to execute on multiple threads
    def single_cpu (sim):
        proba_success, longestfork = find_proba(sim, nh,na,height,e)
        num_cycles = int(log(2**-30) / log(np.average(proba_success)))
        tot_attack = longest_fork(sim, longestfork, num_cycles)
        return proba_success, num_cycles, tot_attack

    pool = mp.Pool(mp.cpu_count())
    print("CPUs", mp.cpu_count())
    results = pool.map(single_cpu, [sim] * mp.cpu_count())
    #results = single_cpu(sim)
    print results
    pool.close()
    

    print("--- %s seconds ---" % (time.time() - start_time))
