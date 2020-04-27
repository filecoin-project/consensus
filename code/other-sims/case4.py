import numpy as np 
import time
from math import floor

nh=67
na=33
ntot=na+nh
heights=range(250,251,10)
p=5./float(1*ntot)

sim=1000000

ec =[]


start_time = time.time()


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

			pprime=float(ca[j])/float(ca[j]+ch[j])
			coin = np.random.binomial(1, pprime, 1)
			if coin: #adversary is winning
			#it can create many different blocks with the "winning"
			#ticket (to check with henri) 
				w_h+=1
			else:	#if honest is winning 
			#then its honest chain has a weight +2
			#(assuming  the honest power is completely spread) 
				w_h+=2
			w_a+=ca[j]#adv adds all blocks possible to its chain
			praos_a
			j+=1
		if w_a>=w_h and w_a>0:
			win_ec+=1
			longestfork.append(j)
	#print np.average(longestfork)
	ec.append(float(win_ec)/float(sim))
longestfork.sort()

print ec,np.average(longestfork), np.median(longestfork),max(longestfork), sum(longestfork[-54:])

print("--- %s seconds ---" % (time.time() - start_time))