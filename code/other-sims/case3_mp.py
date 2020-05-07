import numpy as np 
import time
from math import floor
import multiprocessing as mp


#sim=10000

ec =[]
num=1
e=1
print "e = ", e

start_time = time.time()

# Step 1: Init multiprocessing.Pool()



def simu(sim): #the adversary tries to keep maintaining two chain of same weight and
#length "height", we try different heights and see the probability of succeeding. Ig this probability is
#small enough, we consider this height a good finality candidate.
	nh=67
	na=33
	ntot=na+nh
	#heights=range(250,251,10)
	height = 250
	p=float(e)/float(1*ntot)
	if e==1: num=77
	if e==5: num=54
	win_ec = 0
	longestfork =[]
	np.random.seed()
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# print ch
		# print ca
		j=0
		win =1
		sumh = ch[0]+ch[1]
		suma = ch[0]+ca[0]+ca[1]
		ind = 1  
		while sumh>suma and ind<height:
			sumh+=ch[ind]
			suma+=ca[ind]
			ind+=1
			if ind == height:
				win =0
				break
		j=1
		if ind <height:
			win = 1
			longestfork.append(ind)

		if win ==1:
			win_ec+=1
			longestfork.append(j)
	#print np.average(longestfork)
	#return float(win_ec)/float(sim)
	stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num
	groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]
	return max(groupedfork)

# longestfork.sort()
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [100000000]*mp.cpu_count())
pool.close()

# print ec,np.average(longestfork), np.median(longestfork),max(longestfork), sum(longestfork[-54:])

# #before sorting, we group them by groups of num
# stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num

# groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]


# print ec, np.average(groupedfork), np.median(groupedfork), max(groupedfork), len(groupedfork)

print results, max(results)
print("--- %s seconds ---" % (time.time() - start_time))