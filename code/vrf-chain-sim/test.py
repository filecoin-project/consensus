import numpy as np 

# def new_node(n,slot,weight,parent=0):
#     return {
#         'n': n,
#         'slot': slot,
#         'weight':weight,
#         'parent':parent
#     }

# nnode = new_node (1,2,3,4)

# print(nnode['weight'])

# list_oh_weight = {i: 0 for i in range(10)}

# print(list_oh_weight)

# l =[0,1,2,3,4]
# print(l[-1],l[-2],l[-5])

k = 3
ca =[1,2,4,2,13,4,5,1,2,52,1,3]
height = len(ca)
newca = [ca[r] for r in range(0,height,k)]
restofca = [ca[r] for r in range(height) if r not in range(0,height,k)]
print(newca)
print(restofca)