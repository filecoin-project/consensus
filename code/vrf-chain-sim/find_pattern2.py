import numpy as np 
import time
from math import floor
import multiprocessing as mp
import scipy.special
#Initialize parameters
Num_of_sim_per_proc = 1
start_time = time.time()
e = 5.
alpha = 0.33
ntot = 100
na = int(ntot*alpha)
nh = ntot - na
height = 5 #height of the attack
p=float(e)/float(1*ntot)
unrealistic = 0 #do we want to compute the worst case or just the synchronous case?
def multinomial(lst):
    res, i = 1, sum(lst)
    i0 = lst.index(max(lst))
    for a in lst[:i0] + lst[i0+1:]:
        for j in range(1,a+1):
            res *= i
            res //= j
            i -= 1
    return res
## use multinomial coefficient
def new_node(slot,weight):
    return {
        'slot': slot,
        'weight':weight
    }


def print_weight(vec):#given a vector of number of election won at each slot, how many
# "situations" gives a chain weight (i.e. sum of blocks) higher than some number
	list_of_nodes  = [[new_node(-1,0,)]]
	for ind,v in enumerate(vec):
		list_of_nodes_at_slot_ind = []
		for i in range(v+1):
			for node in list_of_nodes[ind]: #take all the nodes from slot before i.e. ind-1
				weight = node['weight'] + i
				nnode = new_node(ind,weight)
				list_of_nodes_at_slot_ind.append(nnode)
		list_of_nodes.append(list_of_nodes_at_slot_ind)
	dict_of_weight = {i: 0 for i in range(sum(vec)+1)}
	for elt in list_of_nodes[-1]:
		w = elt['weight']
		dict_of_weight[w]+=1
	return dict_of_weight


def count(ca):
	#create first list with (s=sum(ca_i), s-1, s-2, ..., s-ca_n)
	s=sum(ca)
	ca = [x for x in ca if x != 0]
	n=len(ca)
	l1 = [s-i for i in range(ca[-1]+1)]
	l = np.array(l1.copy())
	for j in range(1,n):
		for i in range(1,ca[-1-j]+1):
			ll = np.array(l1)-i
			l=np.concatenate((l,ll),axis =0)
		l1 = l.copy()
	dict_of_weight = {i: 0 for i in range(sum(ca)+1)}
	for elt in l:
		dict_of_weight[elt]+=1
	return dict_of_weight

def simu(sim): 
	np.random.seed()#initialise random seed for different processors
	wa = []
	for i in range(sim):
		ca = np.random.binomial(na, p, height)
		winners = print_weight(ca)
		wa.append(winners)
		#ca = np.array(ca)+1
		#tot = np.prod(ca)
		cc = count(ca)
	return  wa[0], cc, wa[0] == cc


pool = mp.Pool(1)
#print(mp.cpu_count())
results = pool.map(simu, [Num_of_sim_per_proc])
pool.close()

print(results)
print("--- %s seconds ---" % (time.time() - start_time))