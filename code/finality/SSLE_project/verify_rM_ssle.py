import multiprocessing as mp
import numpy as np 
import time, random

''' outputs the probability of a private chain of length  greater or equal 
than height_min
-> Longest chain only (no tipset)
'''
M=10
height_min=1000
e=1.
advfrac = 1./3.
alpha = 0.33332
# advfrac = (np.exp(alpha-1)-np.exp(-1))/(1-p0)

ec =[]
praos = []
print("e = ", e)
Num_of_sim_per_proc = 10000
print("Num of sim per proc = ", Num_of_sim_per_proc)

start_time = time.time()

#height_min_range = [150,200,300,400]
height_min_range = [50]#,60,80]


print("height = ", height_min)
def simu(sim):
	win = 0
	np.random.seed()
	for i in range(sim):
		gap = 0
		# instead of having each player toss a private coin to determine
		# their eligibility we choose, at random, exactly one leader
		# that is adversarial wioth probability na/ntot and honest
		# with probability nh/ntot
		wpraos_h = 0
		wpraos_a = 0
		for j in range(height_min):
			coin = random.uniform(0, 1) # coin determines winner
			if coin<advfrac:
				gap += 1
			else:
				gap -=1
			if gap == M:
				win+=1
				break
		
	#print win_ec, win_praos
	return (float(win)/float(sim))


pool = mp.Pool(mp.cpu_count())
#pool = mp.Pool(1)
#print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()

def r_SSLE(alpha,M):
	return pow((alpha/(1-alpha)),float(M))
print('Simulaions result: ',np.average(results))
print('Theoretical result: ',r_SSLE(alpha,M))
print("--- %s seconds ---" % (time.time() - start_time))