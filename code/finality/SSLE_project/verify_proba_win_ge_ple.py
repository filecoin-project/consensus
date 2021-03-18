import multiprocessing as mp
import numpy as np 
import time
from math import sqrt,pow #,comb
from scipy.stats import binom, poisson

''' verify if the probability wins the game of length >=n
'''
alpha = 0.32
pa = (np.exp(alpha-1)-np.exp(-1))
ph = (np.exp(-alpha)-np.exp(-1))
p0 = 1 -pa - ph

def Bin(x,n,p):
	return binom.pmf(x, n, p)

def P_SSLE(p,n):
	s = 0.
	for v in range(n+1):	
		if (n+v)%2 ==0:
			s+= Bin((n+v)//2,n,p)
	for v in range(1,n+1):		
		if (n-v)%2 ==0:
			s+= Bin((n-v)//2,n,1.-p)
	return s
def P_ssle_v(p,n,v):
	if (n+v)%2 ==0:
		return Bin((n+v)//2,n,p)
	else:
		return 0

def r_PLE(alpha,M):
	#return pow(pa/ph,float(M))
	return pow((np.exp(alpha)-1)/(np.exp(-alpha+1)-1),float(M))
def P_PLE(n):
	s = 0.
	for v in range(n+1):	
		for l in range(n-v):
			s+= Bin(l,n,p0)*P_ssle_v(pa/(1-p0),n-l,v)
	for v in range(1,n+1):		
		for l in range(n-v):
			s+= Bin(l,n,p0)*P_ssle_v(pa/(1-p0),n-l,-v)*r_PLE(alpha,v)
	return s

print(P_PLE(150))