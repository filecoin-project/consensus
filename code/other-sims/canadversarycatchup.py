import numpy as np 
import time
from math import floor

nh=67
na=33
ntot=na+nh
heights=range(150,160,10)
p=5./float(1*ntot)

epoch_boundary_param = 0.5
sim=10000000

ec =[]
praos = []

start_time = time.time()


for height in heights:
	win_ec = 0
	longestfork =[]
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# print ch
		# print ca
		j=0
		win =1
		while j<height-1 and win:
			if ca[j]==0:#the adversary is not elected leader in round j this means that in round
			#j+1 all the honest parties will mine on the same chain
				sumh = ch[j+1] #weight of honest chain "after forks" (assuming forks were of same length before)
				suma = ca[j+1] #weight of adversarial chain "after forks"
				ind = j+2 
				while sumh>suma and ind<height: #as soon as adversary catches up with honest chain, assume
				#it can create a fork again
					sumh+=ch[ind]
					suma+=ca[ind]
					ind+=1
				if ind == height and sumh>suma: #we have reach the end of the attack
				#and adversary has not catch up
					win =0
					break
				else: #adversary has catch up and can continue the forks until
				#it is not elected leader again
					j= ind
			else:
				j+=1
		if win ==1:
			win_ec+=1
		#longestfork.append(j)
	#print np.average(longestfork)
	ec.append(float(win_ec)/float(sim))

print ec

print("--- %s seconds ---" % (time.time() - start_time))