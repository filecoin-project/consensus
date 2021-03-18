import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import decimal
from math import sqrt

''' Plotting mu + k sigma for PLE and SSLE for a fixed k,alpha
and n varying
'''

# Data for plotting
#alpha = np.arange(0., 0.5, 0.01)
alpha = 0.48
n = range(5000,80000,1000)
k=7
pa = (np.exp(alpha-1)-np.exp(-1))
ph = (np.exp(-alpha)-np.exp(-1))

def SSLE(alpha,n,k):
	return (2*alpha-1)*n+k*sqrt((1-(2*alpha-1)**2)*float(n))
def PLE(alpha,n,k):
	beta = pa-ph
	return beta*n+k*sqrt((pa+ph-beta*beta)*float(n))

sle = [SSLE(alpha,n1,k) for n1 in n]
ple = [PLE(alpha,n1,k) for n1 in n]
# print([PLE(alpha,n1,k) for n1 in [528]])
# print([SSLE(alpha,n1,k) for n1 in [385]])
#print(SSLE(alpha,10,k),PLE(alpha,10,k))
plt.plot(n,sle , 'r--', label = 'SSLE')
plt.plot(n, ple , 'bs', label = 'PLE')
plt.legend(loc="lower left",prop={'size': 30})
# # plt.yscale('log')
plt.xlabel('fork length',size=30)
#plt.ylabel('Gap maximum length for a 33% adversary',size=30)
plt.xticks(size=25 )
plt.yticks(size=25)
plt.title('Gap maximum length for a 49% adversary')
plt.subplots_adjust(bottom=0.15, left = 0.2)
plt.show()
# plt.savefig('pred-int.png')
