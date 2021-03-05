import multiprocessing as mp
import numpy as np 
import time
print "Longest SSM greater or equal than"
nh=668
na=332
ntot=na+nh
height_min=30
height_max=100
e=5.
p=e/float(1*ntot)
print "height min = ", height_min

''' This script calculates the probability that the adversary can suceed in
creating a selfish chain of length between height_min and height_max using strong selfish mining
attack.
'''
ec =[]
praos = []
print "e = ", e
Num_of_sim_per_proc = 10000

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
		w_h = ch[0]+1#adversary starts epoch boundary here with sending one different block
		# to different players so they all mine on a different chain

		fork_finished = 0
		for i in range(1,height_min):
			# ca[i] adversarial block
			# ch[i] honest block
			# proba min ticket: pi= ca[i]/(ca[i]+ch[i])
			# toss a biased coin with proba pi
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


		if w_a>=w_h: 
			win_ec+=1
		else: # If the attack hasn't succeded, we try to see if the adversary
		# gets more lucky in the next step and manage to suceed in the attack
			for i in range(height_min,height_max):
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
				w_a+=ca[i]
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


