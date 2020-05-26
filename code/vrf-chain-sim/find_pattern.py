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


def count_n2(ca):
	num = len([x for x in ca if x > 1]) #count number of slot with more than 2 slots
	n1 = len([x for x in ca if x != 0])
	if n1>1:
		num += scipy.special.binom(n1, 2)
	return num
def count_n3(ca):
	num = 0
	n3 = len([x for x in ca if x > 2]) #count number of slot 3 blocks
	n2 = len([x for x in ca if x > 1])
	num += n3
	n1 = len([x for x in ca if x != 0])
	if n1>2:
		num += scipy.special.binom(n1, 3) # 1 1 1
	# 2 1 
	if n1>0:
		#num += scipy.special.binom(n2, 3)
		num +=n2*(n1-1)
	return num
def count_n5(ca):
	num = 0
	n5 = len([x for x in ca if x > 4])
	n4 = len([x for x in ca if x > 3])
	n3 = len([x for x in ca if x > 2]) #count number of slot 3 blocks
	n2 = len([x for x in ca if x > 1])
	n1 = len([x for x in ca if x != 0])
	num += n5 # 5
	if n1>4:
		num += scipy.special.binom(n1, 5) # 1 1 1 1 1
	# 2 3
	if n2>1:
		num += n3*(n2-1)
	# 4 1
	if n1>0:
		#num += scipy.special.binom(n2, 3)
		num +=n4*(n1-1)
	# 2 1 1 1
		num+=n2*(scipy.special.binom(n1-1, 3))
		# 2 2 1
	if n1>1 and n2>1:
		num += (n1-2)*scipy.special.binom(n2, 2)
		#1 1 3
	if n3>0:
		num+=n3*scipy.special.binom(n1-1,2)
	return num

def count_k(k,ca):


def count_n4(ca):
	num = 0
	n4 = len([x for x in ca if x > 3])
	n3 = len([x for x in ca if x > 2]) #count number of slot 3 blocks
	n2 = len([x for x in ca if x > 1])
	n1 = len([x for x in ca if x != 0])
	num += n4 # 4
	if n1>3:
		num += scipy.special.binom(n1, 4) # 1 1 1 1
	# 2 2
	if n2>1:
		num += scipy.special.binom(n2, 2)
	# 3 1
	if n1>0:
		#num += scipy.special.binom(n2, 3)
		num +=n3*(n1-1)
	# 2 1 1
		num+=n2*(scipy.special.binom(n1-1, 2))
	return num
def  count_n1(ca):
	return len([x for x in ca if x != 0])

def simu(sim): 
	np.random.seed()#initialise random seed for different processors
	wa = []
	for i in range(sim):
		ca = np.random.binomial(na, p, height)
		winners = print_weight(ca)
		wa.append(winners)
		#ca = np.array(ca)+1
		#tot = np.prod(ca)
	return wa, count_n4(ca), count_n5(ca)



pool = mp.Pool(1)
#print(mp.cpu_count())
results = pool.map(simu, [Num_of_sim_per_proc])
pool.close()

print(results)
print("--- %s seconds ---" % (time.time() - start_time))