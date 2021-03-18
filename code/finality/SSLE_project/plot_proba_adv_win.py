import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import decimal
from math import sqrt,pow,floor

''' plot of probability that the gap, starting from 0 ever
reaches a value M
''' 

alpha = 0.332
k= pow(10,4)
n = range(100,101)
pa = (np.exp(alpha-1)-np.exp(-1))
ph = (np.exp(-alpha)-np.exp(-1))
def mu_SSLE(n):
	return (2*alpha-1)*n
def mu_PLE(n):
	return (np.exp(alpha-1)-np.exp(-alpha))*n
def sigma_SSLE(n):
	beta = 2*alpha-1
	return sqrt((1-beta*beta)*n)
def sigma_PLE(n):
	b = (np.exp(alpha-1)-np.exp(-alpha))
	return sqrt((pa+ph-b*b)*n)

def M_SSLE(k,n):
	return floor(-mu_SSLE(n)-k*sigma_SSLE(n))

def M_PLE(k,n):
	return floor(-mu_PLE(n)-k*sigma_PLE(n))

def r_SSLE(M):
	return pow((alpha/(1-alpha)),float(M))

def r_PLE(M):
	return pow((np.exp(alpha)-1)/(np.exp(-alpha+1)-1),float(M))



def p_SSLE(k,n):
	return r_SSLE(M_SSLE(k,n))+1/(k*k)-r_SSLE(M_SSLE(k,n))*1/(k*k)

def p_PLE(k,n):
	return r_PLE(M_PLE(k,n))+1/(k*k)-r_PLE(M_PLE(k,n))*1/(k*k)

k=10
n = 1500
print(M_PLE(k,n),M_SSLE(k,n))
print(r_PLE(M_PLE(k,n)))
print(r_SSLE(M_SSLE(k,n)))
print(p_PLE(k,n),p_SSLE(k,n))
# sle = [p_SSLE(k,n1) for n1 in n]
# ple = [p_PLE(k,n1) for n1 in n]
# print('PLE',[p_PLE(k) for n1 in n])
# print('SSLE',[p_SSLE(k) for n1 in n])
#print(SSLE(alpha,10,k),PLE(alpha,10,k))

if 0:
	plt.plot(n,sle , 'r--', label = 'SSLE')
	plt.plot(n, ple , 'bs', label = 'PLE')
	plt.legend(loc="upper right",prop={'size': 30})
	# # plt.yscale('log')
	plt.xlabel('fork length',size=30)
	#plt.ylabel('Gap maximum length for a 33% adversary',size=30)
	plt.xticks(size=25 )
	plt.yticks(size=25)
	plt.title('Probability that the adversary gap increases by M')
	plt.subplots_adjust(bottom=0.15, left = 0.2)
	plt.show()
	# plt.savefig('pred-int.png')
