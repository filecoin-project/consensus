import numpy as np 
import time
from math import floor
import multiprocessing as mp

nh=67
na=33
ntot=na+nh
heights=range(250,251,10)
e=1
p=float(e)/float(1*ntot)

sim=1000000

ec =[]
num=1
if e==1: num=77
if e==5: num=54

start_time = time.time()

# Step 1: Init multiprocessing.Pool()
pool = mp.Pool(mp.cpu_count())


for height in heights: #the adversary tries to keep maintaining two chain of same weight and
#length "height", we try different heights and see the probability of succeeding. Ig this probability is
#small enough, we consider this height a good finality candidate.
	win_ec = 0
	longestfork =[]
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested height times. (i.e. number of leaders
	# at ach slot for both adversary and honest players)
		j=0
		w_h = 0
		w_a = 0
		praos_h=0
		praos_a=0
		j=0
		while ca[j]>0 and j<height:
			#determine if adversary or honest is winning
			w_h+=1
			w_a+=ca[j]#adv adds all blocks possible to its chain
			praos_a
			j+=1
		if w_a>=w_h and w_a>0:
			win_ec+=1
			longestfork.append(j)
	#print np.average(longestfork)
	ec.append(float(win_ec)/float(sim))
# longestfork.sort()

# print ec,np.average(longestfork), np.median(longestfork),max(longestfork), sum(longestfork[-54:])

#before sorting, we group them by groups of num
stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
#if it is not a multiple of num

groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]


print ec, np.average(groupedfork), np.median(groupedfork), max(groupedfork), len(groupedfork)

print("--- %s seconds ---" % (time.time() - start_time))