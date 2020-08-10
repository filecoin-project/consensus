import multiprocessing as mp
import numpy as np 
import time
from math import log

nh=66667
na=33333
ntot=na+nh
height=15
e=5.
p=e/float(1*ntot)


ec =[]
print "e = ", e
Num_of_sim_per_proc = 10000

start_time = time.time()


pow1 = 10*2**50
print(pow1)

def simu(sim):
	win_ec = 0
	#win_praos = 0
	np.random.seed()
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		#praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		#praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		w_a = ch[0]+sum(ca)#num,ber of blocks created by adversary + headstart
		w_h = sum(ch)
		#wpraos_h = sum(praosh)
		#wpraos_a = sum(praosa)

		if log(pow1,2)*(height+0.5*w_a)>=log(pow1*0.66,2)*(height+0.5*w_h): win_ec+=1
		#if wpraos_a>=wpraos_h: win_praos+=1
	#print win_ec, win_praos
	return float(win_ec)/float(sim)
	#praos.append(float(win_praos)/float(sim))


#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()


print results, np.average(results)
print("--- %s seconds ---" % (time.time() - start_time))