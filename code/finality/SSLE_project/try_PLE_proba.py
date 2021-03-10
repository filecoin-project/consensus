import multiprocessing as mp
import numpy as np 
import time

nh=6668
na=3332
ntot=na+nh
height=10
e=1.
p=e/float(1*ntot)
print "height = ", height

ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 10000
print "Num of sim per proc = ", Num_of_sim_per_proc

start_time = time.time()

alpha = 0.3332


def simu(sim):
	win_ec = 0
	win_praos = 0
	np.random.seed()
	pa = []
	ph = 0
	p0 = []
	for i in range(sim):
		ch = np.random.poisson(1-alpha, height)
		ca = np.random.poisson(alpha, height)
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		newveca = 0
		newvech = 0
		newnull = 0
		for j in range(height):
			if praosa[i]>0 and praosh[i]==0:
				newveca+=1
			elif praosh[i]>0 and praosa[i]==0:
				newvech+=1
			else:
				newnull +=1
		if height>newnull:
			pa.append(float(newveca)/float(height-newnull))
		p0.append(float(newnull)/float(height))
		#print(newnull)
		#pa.append(float(newveca)/float(height))

		


	#print win_ec, win_praos
	return np.average(p0)
	#praos.append(float(win_praos)/float(sim))


#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()


print results, np.average(results)
print("--- %s seconds ---" % (time.time() - start_time))