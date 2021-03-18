import multiprocessing as mp
import numpy as np 
import time
from math import sqrt

''' We are looking for the probability that the gap ever reaches a certain
value M>0
'''

height=1000
e=1.
print "height = ", height

ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 10000
print "Num of sim per proc = ", Num_of_sim_per_proc

start_time = time.time()

alpha = 0.33332
M = 6

def simu(sim):
	win = 0
	np.random.seed()
	for i in range(sim):
		ch = np.random.poisson(1-alpha, height)
		ca = np.random.poisson(alpha, height)
		
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		praosh=[1 if ch[j]>0 else 0 for j in range(len(ch))]
		praosa=[1 if ca[j]>0 else 0 for j in range(len(ca))]
		Xi = [praosa[j]-praosh[j] for j in range(height)]
		s = 0
		for j in range(height):
			s+=Xi[j]
			if s>=M:
				win+=1
				break

	return (float(win)/float(sim))


#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()
pa = (np.exp(alpha-1)-np.exp(-1))
ph = (np.exp(-alpha)-np.exp(-1))
def r_PLE(alpha,M):
	#return pow(pa/ph,float(M))
	return pow((np.exp(alpha)-1)/(np.exp(-alpha+1)-1),float(M))

print('Simulaions result: ',np.average(results))
print('Theoretical result: ',r_PLE(alpha,M))
print("--- %s seconds ---" % (time.time() - start_time))