import numpy as np 
import time
from math import floor
import multiprocessing as mp


#sim=10000

ec =[]
num=1
e = 1
print "e = ", e
Num_of_sim_per_proc = 100000

start_time = time.time()

#This simulation computes at is the worst length of n successives attack 4 (adversary split the honest power
#as much as possible and selfish mine in parallel)

def simu(sim): 
	nh=67
	na=33
	ntot=na+nh
	height = 250#the height is chosen to avoid infinite loop, in practice a selfish mining
	#attack will not last 250 except with negligible probabilities
	p=float(e)/float(1*ntot)
	if e==1: num=17
	if e==5: num=100
	#num corresponds to the number of iterations of the attack that the adversary can perform
	#(calculated previously)
	win_ec = 0
	longestfork =[]
	np.random.seed()#initialise random seed for different processors
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested height times. (i.e. number of leaders
	# at ach slot for both adversary and honest players)
		j=0
		w_h = 0
		w_a = 0
		j=0
		while ca[j]>0 and j<height: 
			w_h+=1#worse case scenario, only one block is added to the honest chain
			w_a+=ca[j]#adv adds all blocks possible to its chain
			j+=1
		if w_a>=w_h and w_a>0:
			win_ec+=1
			longestfork.append(j)#length of the attack
	stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num
	groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]  #we grouped the num
	#successive attacks together and sums them up to get the length of num successives attacks
	return max(groupedfork)

pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()

print results, max(results)
print("--- %s seconds ---" % (time.time() - start_time))