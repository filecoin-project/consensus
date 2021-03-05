import multiprocessing as mp
import numpy as np 
import time, random

''' outputs the probability of a private chain of length  greater or equal 
than height_min
-> Longest chain only (no tipset)
'''

nh=668
na=332
ntot=na+nh
height_max=600
e=1.
p=e/float(1*ntot)
advfrac = 1./3.

ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 100
print "Num of sim per proc = ", Num_of_sim_per_proc

start_time = time.time()

height_min_range = [150,200,300,400]

for height_min in height_min_range:
	print "height = ", height_min
	def simu(sim):
		win_praos = 0
		np.random.seed()
		for i in range(sim):
			# instead of having each player toss a private coin to determine
			# their eligibility we choose, at random, exactly one leader
			# that is adversarial wioth probability na/ntot and honest
			# with probability nh/ntot
			wpraos_h = 0
			wpraos_a = 0
			for j in range(height_min):
				coin = random.uniform(0, 1) # coin determines winner
				if coin<advfrac:
					wpraos_a += 1
				else:
					wpraos_h +=1
			if wpraos_a>=wpraos_h: 
				win_praos+=1

			else:
				for j in range(height_min,height_max):
					coin = random.uniform(0, 1) # coin determines winner
					if coin<advfrac:
						wpraos_a += 1
					else:
						wpraos_h +=1
					if wpraos_a>=wpraos_h:
						win_praos += 1
						break
		#print win_ec, win_praos
		return float(win_praos)/float(sim)
		#praos.append(float(win_praos)/float(sim))


	#we rune the simulations in parallel:
	pool = mp.Pool(mp.cpu_count())
	#print mp.cpu_count()
	results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
	pool.close()


	print  np.average(results)
print("--- %s seconds ---" % (time.time() - start_time))