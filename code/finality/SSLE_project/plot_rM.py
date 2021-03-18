import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import decimal
from math import sqrt,pow

''' plot of probability that the gap, starting from 0 ever
reaches a value M
''' 

alpha = 0.332
n = range(100,500,100)
# pa = (np.exp(alpha-1)-np.exp(-1))
# ph = (np.exp(-alpha)-np.exp(-1))

def r_SSLE(alpha,M):
	return pow((alpha/(1-alpha)),float(M))
def r_PLE(alpha,M):
	return pow((np.exp(alpha)-1)/(np.exp(-alpha+1)-1),float(M))

sle = [r_SSLE(alpha,n1) for n1 in n]
ple = [r_PLE(alpha,n1) for n1 in n]
print('PLE',[r_PLE(alpha,n1) for n1 in n])
print('SSLE',[r_SSLE(alpha,n1) for n1 in n])
#print(SSLE(alpha,10,k),PLE(alpha,10,k))

if 1:
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
