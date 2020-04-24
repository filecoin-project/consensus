import numpy as np 
import time
from math import floor

nh=67
na=33
ntot=na+nh
heights=range(100,101,50)
p=15./float(1*ntot)

sim=100000

ec =[]
praos = []

start_time = time.time()


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
		if ind <height:
			#win = 1
			longestfork.append(ind)

		if win ==1:
			win_ec+=1
			longestfork.append(j)
	#print np.average(longestfork)
	ec.append(float(win_ec)/float(sim))
longestfork.sort()

print ec, np.average(longestfork), np.median(longestfork), np.average(longestfork[-21:]),max(longestfork)



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