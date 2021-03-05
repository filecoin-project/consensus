import multiprocessing as mp
import numpy as np 
import time

nh=668
na=332
ntot=na+nh
height=30
e=5.
p=e/float(1*ntot)
print "height = ", height

''' This script calculates the probability that the adversary can suceed in
creating a selfish chain of length exactly height using strong selfish mining
attack.
Note: the adversary could potentially succeed in creating a private chain of length
>height but fail in creating a chain of length height (for example if they get
really lucky at the next epoch after height).
This is why we also have the script strongSM_greaterorequal.py
'''
ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 100000
print "Num of sim per proc = ", Num_of_sim_per_proc

start_time = time.time()



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
		w_a = ch[0]+sum(ca)#number of blocks created by adversary + headstart
		w_h = ch[0]+1#adversary starts epoch boundary here with sending one different block
		# to different players so they all mine on a different chain

		fork_finished = 0
		for i in range(1,height):
			# ca[i] adversarial block
			# ch[i] honest block
			# proba min ticket: pi= ca[i]/(ca[i]+ch[i])
			# toss a biased coin with proba pi

			## In the following code, we build the honest chain by
			# splitting its power over at leat two chains
			# in the best adversarial conditions, only one block
			# is added to the honest chain. Otherwise 2 blocks or
			# all of the honest block if the adversary was not able to maintain
			# the split for too long
			if ca[i]>0 and fork_finished == 0 :
				## to do: what happened when ch[i] == 0?
				pi = float(ca[i])/float(ca[i]+ch[i])
				c = np.random.binomial(1,pi,1)[0]
				if c == 1:
					w_h +=1
				else:
					w_h +=2
			if ca[i]>0 and fork_finished == 1 :
				fork_finished = 0
				w_h +=1+ch[i]
			if ca[i]==0 and fork_finished ==0 :
				w_h +=1
				fork_finished = 1
			if ca[i] ==0 and fork_finished == 1:
				w_h += ch[i]


		if w_a>=w_h: win_ec+=1

	return float(win_ec)/float(sim)
	#praos.append(float(win_praos)/float(sim))


#we rune the simulations in parallel:
pool = mp.Pool(mp.cpu_count())
print mp.cpu_count()
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()


print results, np.average(results)
print("--- %s seconds ---" % (time.time() - start_time))


