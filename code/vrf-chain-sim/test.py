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

l =[0,1,2,3,4]
print(l[-1],l[-2],l[-5])