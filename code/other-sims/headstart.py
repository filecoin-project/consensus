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
import utils


s=100000
att=.3
honest=1-att
e=5

def poisson(k1,k2):
    ## pr. honest finds less blocks
    honest_pr = utils.poisson_cdf(k1 + k2,honest* e)
    ## attacker number of blocks at first round
    malicious_1 = utils.poisson(k1,att*e)
    ## attacker number of blocks at second round
    malicious_2 = utils.poisson(k2,att*e)
    return honest_pr,malicious_1,malicious_2

def binomial(k1,k2):
    ## pr. honest finds less blocks
    honest_pr = utils.binomial_cdf(k1 + k2,honest*s,e/s)
    ## attacker number of blocks at first round
    malicious_1 = utils.binomial(k1,att*s,e/s)
    ## attacker number of blocks at second round
    malicious_2 = utils.binomial(k2,att*s,e/s)
    return honest_pr,malicious_1,malicious_2


def compute(prob_function):
    max_pr = 0
    sum_pr = 0
    max_k = 20
    for k1 in range(1,max_k):
        for k2 in range(0, max_k):
            (honest_pr,malicious_1,malicious_2) = prob_function(k1,k2)
            if k1 + k2 < honest*e:
                continue
            total = honest_pr * malicious_1 * malicious_2
            if total > max_pr:
                max_pr = total
            sum_pr += total
    print("max probability: {}".format(max_pr))
    print("sum probability: {}".format(sum_pr))
    print("chain quality reduction: {}".format(sum_pr*0.5))

print(" --- using poisson approximation ---")
compute(poisson)
print(" --- using binomial approximation ---")
compute(binomial)
