import scipy.special
import numpy as np 
import time,random
from math import floor,ceil
import multiprocessing as mp
from scipy.stats import binom, poisson

''' This script calculates the probability that the adversary can suceed in
creating a selfish chain of length exactly height using normal selfish mining
attack.
Note: the adversary could potentially succeed in creating a private chain of length
>height but fail in creating a chain of length height (for example if they get
really lucky at the next epoch after height).
This is why we also have the script strongSM_greaterorequal.py
'''

start_time = time.time()
e = 4.
alpha = 0.33
ntot = 100
na = int(ntot*alpha)
p = float(e)/float(ntot)
w = na
nh = ntot - na
height = 10
print "height = ", height

def Poi(w,k,p):
	#return scipy.special.binom(w,k)*p**k*(1-p)**(w-k)
	#return binom.pmf(w, k, p)
	return poisson.pmf(k,p*float(w))


#for i in range(height*na):
	# for j in range(i,height*na):
	# 	s += Poi((height-1)*nh,i,p)*Poi(height*na,j,p)

def sum_nums(args):
	low = int(args[0])
	high = int(args[1])
	s = 0
   #      print low,high
   #  for i in range(low,high+1):
   #  	for j in range(i,height*na):
			# s += Poi((height-1)*nh,i,p)*Poi(height*na,j,p)
	# return s
	return sum([Poi((height-1)*nh,i,p)*Poi(height*na,j,p) for i in range(low,high+1) for j in range(i,height*na)  ])

if __name__ == "__main__":
	n = height*na 
	procs = mp.cpu_count()
	print procs
	sizeSegment = n/procs

	# Create size segments list
	jobs = []
	for i in range(procs):
		jobs.append((i*sizeSegment, (i+1)*sizeSegment-1))
	print jobs

	pool = mp.Pool(procs).map(sum_nums, jobs)
	print pool
	result = sum(pool)
	print result