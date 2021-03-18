import multiprocessing as mp
import numpy as np 
import time

height=50
e=1.
print "height = ", height

ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 1000
print "Num of sim per proc = ", Num_of_sim_per_proc

start_time = time.time()

alpha = 0.33332


def simu(sim):
	gaps = []
	np.random.seed()
	for i in range(sim):
		ch = np.random.poisson(1-alpha, height)
		ca = np.random.poisson(alpha, height)
		
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		
		# w_a = ch[0]+sum(ca)#num,ber of blocks created by adversary + headstart
		# w_h = sum(ch)
		wpraos_h = sum(praosh)
		wpraos_a = sum(praosa)

		gaps.append(wpraos_a - wpraos_h)
	#print win_ec, win_praos
	return np.average(gaps)
	#praos.append(float(win_praos)/float(sim))


#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()
pa = (np.exp(alpha-1)-np.exp(-1))
ph = (np.exp(-alpha)-np.exp(-1))

print('Simulaions result: ',np.average(results))
print('Theoretical result: ',(pa-ph)*height)
print("--- %s seconds ---" % (time.time() - start_time))