import numpy as np 
import scipy.special as spe
from scipy.stats import binom

# User Params
k = 10000 # number of epochs
alpha = .3
e = 5.0
negl = 2**-50

# Modeling Params
miners = 10000
hon = miners * (1-alpha)
adv = miners * alpha
p = e/miners

def advWinsLTE(x):
    return binom.cdf(x, adv*k, p)

def advWinsGT(x):
    return 1 - advWinsLTE(x)

def advWinsAtMost():
    for i in range(0, int(k*e+1)):
        if advWinsGT(i) <= negl:
            return i

def chainQual(adv):
    advRatio = adv/(k*e)
    mu = 1 - advRatio
    return mu

i = advWinsAtMost()
print "With e = {e} -- over {ep} epochs, adv with power {pow_} wins more than {num} blocks with proba {proba}".format(e=e, ep=k, pow_=alpha, num=i, proba=negl)
print "Chain qual mu = {mu}".format(mu=chainQual(i))
