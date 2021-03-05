import multiprocessing as mp
import numpy as np 
import time

nh=668
na=332
ntot=na+nh
height_min=30
height_max=100
e=4.
p=e/float(1*ntot)
print "height min = ", height_min

ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 100000

start_time = time.time()



def simu(sim):
	win_ec = 0
	#win_praos = 0
	np.random.seed()
	for i in range(sim):
		ch = np.random.binomial(nh, p, height_max)
		ca = np.random.binomial(na, p, height_max)
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		#praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		#praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		w_a = ch[0]+sum(ca[:height_min])#number of blocks created by adversary + headstart
		w_h = sum(ch[:height_min])#adversary starts epoch boundary here with sending one different block
		# to different players so they all mine on a different chain
		if w_a>=w_h: 
			win_ec+=1
		else:
			for i in range(height_min,height_max):
				w_h += ch[i]
				w_a += ca[i]
				if w_a>=w_h:
					win_ec += 1
					break


	return float(win_ec)/float(sim)
	#praos.append(float(win_praos)/float(sim))


#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()


print results, np.average(results)
print("--- %s seconds ---" % (time.time() - start_time))


