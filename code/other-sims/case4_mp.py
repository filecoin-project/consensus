import numpy as np 
import time
from math import floor
import multiprocessing as mp


#sim=10000

ec =[]
num=1
e = 5
print "e = ", e
Num_of_sim_per_proc = 100

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
	if e==1: num=77
	if e==5: num=54
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
		while ca[j]>0 and j<height: #while adversary is elected it performs epoch boundary
			#flip a coin to determine if adversarial or honest block is winning is winning
			pprime=float(ca[j])/float(ca[j]+ch[j])
			coin = np.random.binomial(1, pprime, 1)
			if ch[j]==0 or coin:
			#adversary is winning
			#it can create many different blocks with the "winning"
			#ticket (to check with henri) so each chain is increased by one only
				w_h+=1
			else:	#if honest is winning 
			#then each honest chain has a weight +2
			#(assuming  the honest power is completely spread) 
				w_h+=2
			w_a+=ca[j]#adv adds all blocks possible to its chain
			j+=1
		if w_a>=w_h and w_a>0:
			win_ec+=1
			longestfork.append(j)#length of the attack
	stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num
	groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]  #we grouped the num
	#successive attacks toigether and sums them up to get the length of num successives attacks
	return max(groupedfork)

pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [100]*mp.cpu_count())
pool.close()

print results, max(results)
print("--- %s seconds ---" % (time.time() - start_time))