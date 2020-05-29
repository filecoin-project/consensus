import numpy as np 

def new_node(n,slot,weight,parent=0):
    return {
        'n': n,
        'slot': slot,
        'weight':weight,
        'parent':parent
    }

nnode = new_node (1,2,3,4)

print(nnode['weight'])

list_oh_weight = {i: 0 for i in range(10)}

print(list_oh_weight)

l =[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]
frozen = 5
vrf_ca = [l[i] for i in range(len(l)) if i%frozen == 0]
print(l==[l[0]]+l[1:])
print(2%1)
print(vrf_ca)