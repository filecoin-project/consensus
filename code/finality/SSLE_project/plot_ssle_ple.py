import matplotlib
import matplotlib.pyplot as plt
import numpy as np

''' Plot of probability of adversary winning the game
based on simulations
'''

# Data for plotting
length = [30,60,80,100,150, 200, 300]
ple = [0.1,0.02,0.007,0.002,0.0002,0.00001,0.0000001]
ssle = [0.056,0.007,0.002,0.0005,0.00001,0.0000001,0.000000001]

plt.plot(length, ssle)
plt.plot(length, ple)
plt.yscale('log')
plt.xlabel('Length of the attack')
#plt.ylabel('Probability of succ')
plt.title('Probability of success of a 33% adversary')
#plt.show()
plt.savefig('ssle_vs_ple_33.png')
