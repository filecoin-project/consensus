import numpy as np 
import time
from math import floor, log

nh=67
na=33
ntot=na+nh
heights=range(100,101,50)
p=5./float(1*ntot)

sim=10000
min_length=10

ec =[]
praos = []

start_time = time.time()

hs=1
longestfork =[]
for height in heights:
	win_ec = 0
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# print ch
		# print ca
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
		j=1
		if win == 0 and hs and ca[j-1]>1 :
			sumh =  ch[j]/2+ch[j+1]#at round j the power of honest miners is still split between two chains
						#at round j+1 it goes all back to one chain
			
			suma = ca[j-1]-1 +ca[j+1]#the adversary used all the blocks it withheld in period j-1
			#(all of them minus 1 that it used to maintain the forks)
			
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
		if ind <height:
			if ind>=min_length: win = 1
			longestfork.append(ind)

		if win ==1:
			if ind>= min_length: win_ec+=1
			longestfork.append(j)
	#print np.average(longestfork)
	ec.append(float(win_ec)/float(sim))
longestfork.sort()

print ec, np.average(longestfork), np.median(longestfork), np.average(longestfork[-33:]),max(longestfork)

n = log(2**-30)/log(ec[0])
print(n)
print("--- %s seconds ---" % (time.time() - start_time))



# longestfork =[]
# for height in heights:
# 	win_ec = 0
# 	for i in range(sim):
# 		ch = np.random.binomial(nh, p, height)
# 		ca = np.random.binomial(na, p, height)
# 		# result of flipping a coin nha times, tested 1000 times.
# 		# print ch
# 		# print ca
# 		j=0
# 		win =1
# 		sumh = ch[0]
# 		suma = ca[0]
# 		if ch[0]>ca[0] and ca[0]+ca[1]>=ch[0]+ch[1]:
# 			win_ec+=1

# 	#print np.average(longestfork)
# 	ec.append(float(win_ec)/float(sim))
# print ec