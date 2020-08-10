import numpy as np 
import time
from math import floor
import multiprocessing as mp
import scipy.special
#Initialize parameters
Num_of_sim_per_proc = 10000
height = 20 #height of the attack

start_time = time.time()
e = 5.
alpha = 0.33
ntot = 1000
na = int(ntot*alpha)
nh = ntot - na
p=float(e)/float(1*ntot)
honestsplit  = 1



def count_possibilities_1(ca,num):
	#create first list with (s=sum(ca_i), s-1, s-2, ..., s-ca_n)
	if num>sum(ca):
		return 0
	else:
		s=sum(ca)
		ca = [x for x in ca if x != 0]
		n=len(ca)
		l1 = [s-i for i in range(ca[-1]+1) if s-i>num]
		l = np.array(l1.copy())
		for j in range(1,n):
			for i in range(1,ca[-1-j]+1):
				ll = np.array(l1)-i
				ll = [x for x in ll if x>num]
				l=np.concatenate((l,ll),axis =0)
			l1 = l.copy()
		# dict_of_weight = {i: 0 for i in range(sum(ca)+1)}
		# for elt in l:
		# 	dict_of_weight[elt]+=1
		# return dict_of_weight
		#assert len(l) == np.prod(np.array(ca)+1)
		ct = len(l)
		# if ct>10:
		# 	print(ca,num,l,len(l))
		return ct


def simu(sim): 
	np.random.seed()#initialise random seed for different processors
	# we consider two variant of the attack:
	# 1. the unrealistic "worst case" scenario where the honest chain is completely split due to synchrony errors
	wh_unrealistic = []
	# 2. the synchronous case where the honest chain is never split (+ our adversary does not perform an epoch boundary)
	wh_sync = [0]
	# we could take the average of both depending on our threat model
	wa = []
	proba = 0
	for i in range(sim):
		ch = np.random.binomial(nh, p, height) #[2,3,3,2]
		ca = np.random.binomial(na, p, height) 
		
		#a_max = sum(ca) #heaviest chain that adversary can create
		if honestsplit: 
			h_sync = sum([1.67 if ch[i]>0 else 0 for i in range(len(ch))])
		else:
			h_sync = sum(ch)
		#diff = a_max-h_sync
		winners = count_possibilities_1(ca,h_sync)
		if winners > 0:
			proba +=1 
		wa.append(winners)
		#print([x for x in wa if x >500])
	return np.average(wa)
	#return float(proba)/float(sim)



pool = mp.Pool(mp.cpu_count())
#print(mp.cpu_count())
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()

print(results, np.average(results))
print("--- %s seconds ---" % (time.time() - start_time))