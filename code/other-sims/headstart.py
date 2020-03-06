#!/usr/bin/env python3
#
# This scripts computes the maximum probability that an attacker can pull off a
# successfull headstart attacks.
# Intuition: For the attack to work, the sum of (1) its blocks Bj at round J and
# (2) its block B_j+1 at round j+1  needs to be greater than the honest number
# of blocks at round J+1. Since both honests and attacker are the same honest
# blocks at round J, they don’t make a difference in the chain weight.
# **Analysis**: 
# Describes number of blocks found in a block by using Poisson dist.
# Hj = #  of honest blocks at round j
# Xj = # of malicious blocks at round j
# We want to find the maximum probability as follow:
# SUM: For all k1, k2: Pr[ Hj+1 < k1 + k2 | Xj = k1, Xj+1 = k2 ] * Pr[ Xj = k1 ] * Pr[ Xj+1 = k2]
# Inner loop: Pr[ Hj+1 < k1 + k2] = CDF_Poisson(k1+k2-1)

import numpy as np
import math


s=100000
att=2/10
honest=1-att
e=10
def poisson(successes, fraction,e):
    rate = fraction * e
    return rate**successes * np.exp(-rate) / math.factorial(successes)

def cdf_poisson(successes, fraction,e):
    # go from k:0 -> successes-1: SUM(Pr[X < k])
    return sum([poisson(k,fraction,e) for k in range(successes)])

max_pr = 0
sum_pr = 0
max_k = 20
for k1 in range(1,max_k):
    for k2 in range(1, max_k):
        ## pr. honest finds less blocks
        honest = cdf_poisson(k1 + k2,honest,e)
        ## attacker number of blocks at first round
        malicious_1 = poisson(k1,att,e)
        ## attacker number of blocks at second round
        malicious_2 = poisson(k2,att,e)

        total = honest * malicious_1 * malicious_2
        if total > max_pr:
            max_pr = total
        sum_pr += total

print("max probability: {}".format(max_pr))
print("sum probability: {}".format(sum_pr))
#max probability: 0.07897737740253372
