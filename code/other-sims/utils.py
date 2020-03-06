import math
import numpy as np

def binomial(k,n,p):
    return math.comb(n,k) * np.power(p,k) * np.power((1-p),(n-k))

# Pr[ X < k]
def binomial_cdf(upto,n,p):
    return sum([binomial(k,n,p) for k in range(upto)])

def poisson(k,rate):
    return rate**k * np.exp(-rate) / math.factorial(k)

# Pr[ X < upto]
def poisson_cdf(upto,rate):
    return sum([poisson(k,rate) for k in range(upto)])



