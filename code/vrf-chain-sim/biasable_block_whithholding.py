import numpy as np 
import time
from math import floor
import multiprocessing as mp
import random
#Initialize parameters
Num_of_sim_per_proc = 10
start_time = time.time()
e = 5.
alpha = 0.33
ntot = 1000
na = int(ntot*alpha)
nh = ntot - na
height = 10 #height of the attack
p=float(e)/float(1*ntot)
unrealistic = 0 #do we want to compute the worst case or just the synchronous case?


def new_node(n,slot,weight,parent=0):
    return {
        'n': n,
        'slot': slot,
        'weight':weight,
        'parent':parent
    }


def count_possibilities(vec,num):#given a vector of number of election won at each slot, how many
# "situations" gives a chain weight (i.e. sum of blocks) higher than some number
	if num<sum(vec):
		return 0
	else:
		idx = random.randrange(2**30)
		list_of_nodes  = [[new_node(idx,-1,0,-1)]]
		for ind,v in enumerate(vec):
			list_of_nodes_at_slot_ind = []
			for i in range(v+1):
				for node in list_of_nodes[ind]: #take all the nodes from slot before i.e. ind-1
					weight = node['weight'] + i
					parent = node['n']
					idx = random.randrange(2**30)
					nnode = new_node(idx,ind,weight,parent)
					list_of_nodes_at_slot_ind.append(nnode)
			list_of_nodes.append(list_of_nodes_at_slot_ind)
		ct = 0
		for node in list_of_nodes[-1]:
			if node['weight']>=num:
				ct+=1

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
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		ca = np.array(ca)+1 # we add one to consider the option of "null blocks" 
		h_sync = sum(ch)
		a_max = sum(ca) #heaviest chain that adversary can create
		if unrealistic: h_unrealistic = sum([1 if ch[i]>0 else 0 for i in range(len(ch))])
		#diff = a_max-h_sync
		winners = count_possibilities(ca,h_sync)
		wa.append(winners)
	return max(wa)



pool = mp.Pool(mp.cpu_count())
print(mp.cpu_count())
results = pool.map(simu, [Num_of_sim_per_proc]*mp.cpu_count())
pool.close()

print(results, max(results))
print("--- %s seconds ---" % (time.time() - start_time))