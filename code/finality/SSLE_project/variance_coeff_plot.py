import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import decimal


# Data for plotting
alpha = np.arange(0., 0.5, 0.01)
n=100


plt.plot(alpha, (1-(2*alpha-1)**2), 'r--', label = 'SSLE')
plt.plot(alpha, ((np.exp(alpha-1)-np.exp(-1))+(np.exp(-alpha)-np.exp(-1))-(np.exp(alpha-1)-np.exp(-alpha))**2), 'bs', label = 'PLE')
plt.legend(loc="lower right",prop={'size': 30})
# plt.yscale('log')
plt.xlabel('Adversary power',size=30)
plt.ylabel('Gap-variance coefficient',size=30)
plt.xticks(size=25 )
plt.yticks(size=25)
# plt.title('Probability of success of a 33% adversary')
plt.subplots_adjust(bottom=0.15, left = 0.2)
#plt.show()
plt.savefig('variance-coeff.png')
