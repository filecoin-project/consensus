import numpy as np 
import time
from math import floor
import multiprocessing as mp


#sim=10000

ec =[]
num=1
e=5
print "e = ", e
Num_of_sim_per_proc = 100

start_time = time.time()

# This script simulates the worst length of n consecutive "small headstart" attacks (case 3)


def simu(sim):
	na = 33
	nh = 67
	ntot=na+nh
	height = 250 #the height is chosen to avoid infinite loop, in practice a selfish mining
	#attack will not last 250 except with negligible probabilities
	p=float(e)/float(1*ntot)
	#num corresponds to the number of iterations of the attack that the adversary can perform
	#(calculated previously)
	if e==1: num = 77
	if e==5: num = 43

	win_ec = 0
	longestfork =[]
	np.random.seed()#initialise random seed for different processors
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested height times.
		j=0
		win =1
		sumh = ch[0]+ch[1] #this is the beginning weight of the honest chain
		suma = ch[0]+ca[0]+ca[1] #this is the beginning weight of the adversarial chain using headstart
		ind = 1  
		while sumh>suma and ind<height: #keep selfish mining until adversarial weight is higher than honest
			sumh+=ch[ind]
			suma+=ca[ind]#at each round players extend their chain, separetely
			ind+=1
			if ind == height: #reach the end of the attack without ever "catching up" -> loosing
				win =0
				break
		j=1
		if ind <height: #selfish mining was successful (i.e. stopped)
			win = 1
			longestfork.append(ind) #this is the length of the selfish mining attack

		if win ==1:
			win_ec+=1
	#return float(win_ec)/float(sim)
	stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
#if it is not a multiple of num
	groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]# we grouped the num
	#successive attacks toigether and sums them up to get the length of num successives attacks
	return max(groupedfork)#we take the worst case

#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()


print results, max(results)
print("--- %s seconds ---" % (time.time() - start_time))