import numpy as np 
import time
from math import floor
import multiprocessing as mp


nh=67
na=33
ntot=na+nh
#heights=range(100,101,50)
e=1
p=float(e)/float(ntot)

#sim=100000

ec =[]
praos = []

start_time = time.time()
height=150

def simu(sim):
	longestfork =[]
	win_ec = 0
	np.random.seed()
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# print ch
		# print ca
		if e==5: num=30
		if e==1: num=81
		j=0
		win =1
		sumh = ch[0]
		suma = ca[0]
		ind = 1  
		while sumh>suma and ind<height:
			sumh+=ch[ind]
			suma+=ca[ind]
			ind+=1
			if ind == height:
				win =0
				break
		if ind <height:
			#win = 1
			longestfork.append(ind)
	#print np.average(longestfork)
	#ec.append(float(win_ec)/float(sim))
	stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
# #if it is not a multiple of num
	groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]
	return max(groupedfork)

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


