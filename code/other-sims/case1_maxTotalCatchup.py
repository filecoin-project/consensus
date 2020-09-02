import numpy as np 
import time
from math import floor
import multiprocessing as mp


##  In this sumlation, we compute what is the length of n consecutive
## selfish mining attacks to get the value of maxTotalCatchUp

nh=67
na=33
ntot=na+nh
e=5
print "e = ", e
Num_of_sim_per_proc = 10000
p=float(e)/float(ntot)
min_length=0



ec =[]
praos = []
### Put NumCycle here
if e==5: num=43
if e==1: num=81 #number of allowed consecutive attacks computed previously
start_time = time.time()
height=150#the height is chosen to avoid infinite loop, in practice a selfish mining
	#attack will not last 150 except with negligible probabilities

def simu(sim):
	longestfork =[]
	win_ec = 0
	np.random.seed()#initialise random seed for different processors
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested height times.

		j=0
		win =1
		sumh = ch[0]#this is the begining of the selfish mining 
		suma = ca[0]
		ind = 1  
		while sumh>suma and ind<height: #do attack until adversary catches up
			sumh+=ch[ind]
			suma+=ca[ind]
			ind+=1
			if ind == height:#if adversary hasn't catch up in time, it loses
				win =0
				break
		if ind <height and ind>=min_length:
			#win = 1
			longestfork.append(ind)
	stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num
	groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]# we grouped the num
	#successive attacks together and sums them up to get the length of num successives attacks
	return max(groupedfork)

pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()

print results, max(results)



print("--- %s seconds ---" % (time.time() - start_time))


