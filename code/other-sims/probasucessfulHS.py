import numpy as np 
import time
from math import floor

nh=67
na=33
ntot=na+nh
heights=range(100,101,50)
e=1
p=float(e)/float(1*ntot)

sim=100000

ec =[]
praos = []

start_time = time.time()

num=1
if e==1: num=77
if e==5: num=43

hs=1
longestfork =[]
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
# 		sumh = ch[0]+ch[1]
# 		suma = ch[0]+ca[0]+ca[1]
# 		ind = 1  
# 		while sumh>suma and ind<height:
# 			sumh+=ch[ind]
# 			suma+=ca[ind]
# 			ind+=1
# 			if ind == height:
# 				win =0
# 				break
# 		j=1
# 		if ind <height:
# 			win = 1
# 			longestfork.append(ind)

# 		if win ==1:
# 			win_ec+=1
# 			longestfork.append(j)
# 	#print np.average(longestfork)
# 	ec.append(float(win_ec)/float(sim))
# longestfork.sort()

# print ec, np.average(longestfork), np.median(longestfork), np.average(longestfork[-num:]),max(longestfork)



# print("--- %s seconds ---" % (time.time() - start_time))

## alternative method:


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
	ec.append(float(win_ec)/float(sim))
#before sorting, we group them by groups of num
stop = int(floor(sim/num)*num) #need to stop before the end of the longest fork
#if it is not a multiple of num

groupedfork=[ sum(longestfork[x:x+num]) for x in range(0, stop, num)]


print ec, np.average(groupedfork), np.median(groupedfork), max(groupedfork), len(groupedfork)
