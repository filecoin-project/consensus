import multiprocessing as mp
import numpy as np 
import time
from math import sqrt,pow #,comb
from scipy.stats import binom, poisson

''' verify if the probability wins the game of length >=n
'''
alpha = 0.33332

# def P_SSLE(n):
# 	s = 0.
# 	for v in range(n+1):
		
# 		if (n+v)%2 ==0:
# 			#print(v)
# 			#print((n+v)/2)
# 			s+= float(comb(n,(n+v)//2))*pow(alpha,(n+v)/2)*pow(1-alpha,(n-v)//2)
# 			print(s)
# 	for v in range(1,n+1):
		
# 		if (n-v)%2 ==0:
# 			#print(v)
# 			s+= float(comb(n,(n-v)//2))*pow(alpha,(n-v)//2)*pow(1-alpha,(n+v)//2)
# 			#pass
# 			print(float(comb(n,(n-v)//2))*pow(alpha,float((n-v))//2.)*pow(1-alpha,float((n+v))//2.))
# 	return s
def Bin(x,n,p):
	return binom.pmf(x, n, p)
def P_SSLE(n):
	s = 0.
	for v in range(n+1):	
		if (n+v)%2 ==0:
			#print(v)
			#print((n+v)/2)
			#s+= float(comb(n,(n+v)//2))*pow(alpha,(n+v)/2)*pow(1-alpha,(n-v)//2)
			s+= Bin((n+v)//2,n,alpha)
	for v in range(1,n+1):		
		if (n-v)%2 ==0:
			#print(v)
			#s+= float(comb(n,(n-v)//2))*pow(alpha,(n-v)//2)*pow(1-alpha,(n+v)//2)
			s+= Bin((n-v)//2,n,alpha)*pow((alpha/(1-alpha)),v)
			#print(float(comb(n,(n-v)//2))*pow(alpha,float((n-v))//2.)*pow(1-alpha,float((n+v))//2.))
	return s
def P_SSLE_2(n):
	s = 0.
	for v in range(n+1):	
		if (n+v)%2 ==0:
			s+= Bin((n+v)//2,n,alpha)
	for v in range(1,n+1):		
		if (n-v)%2 ==0:
			s+= Bin((n-v)//2,n,1.-alpha)
	return s

#print(comb(10,3))

print(P_SSLE(150),P_SSLE_2(150))
