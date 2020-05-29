import numpy as np
import time
from math import floor, log


nh=67
na=33
sim=10000
min_length=10
def pr_catchup(nh, na, height, e, sim, min_length):
    # start_time - useful for debugging
    start_time = time.time()

    # ntot - total number of players
    ntot = na + nh
    # p - probability of one player to win
    p = float(e) / float(1 * ntot)

    # longestfork - list of all the lengths of the minimum catchup
    longestfork =[]

    # win_ec - probability of catching up
	win_ec = 0

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
		sumh = ch[0]
        # sumh - weight of dishonest chain
		suma = ca[0]
		while sumh > suma and ind < height:
			sumh+=ch[ind]
			suma+=ca[ind]
			ind+=1
			if ind == height:
				win =0
				break

        # Second attack: Headstart catchup (if attacker didn't win so far)
        # The attack starts if
        # TODO: perform headstart attack a block earlier
		if win == 0 and ca[0]>1 :
			sumh =  ch[1]/2+ch[2]#at round j the power of honest miners is still split between two chains
						#at round j+1 it goes all back to one chain

			suma = ca[0]-1 +ca[2]#the adversary used all the blocks it withheld in period j-1
			#(all of them minus 1 that it used to maintain the forks)

			ind = 3
			while sumh>suma and ind<height: #as soon as adversary catches up with honest chain, assume
			#it can create a fork again
				sumh+=ch[ind]
				suma+=ca[ind]
				ind+=1
				if ind == height and sumh>suma: #we have reach the end of the attack
			#and adversary has not catch up
					win =0
					break

		if ind <height:
			if ind>=min_length: win = 1
			longestfork.append(ind)

		if win ==1:
			if ind>= min_length: win_ec+=1
			longestfork.append(ind)
	#print np.average(longestfork)
	return float(win_ec)/float(sim)
longestfork.sort()

print np.average(longestfork), np.median(longestfork), np.average(longestfork[-33:]),max(longestfork)

n = log(2**-30)/log(ec[0])
print(n)
print("--- %s seconds ---" % (time.time() - start_time))
