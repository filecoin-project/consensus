#!/usr/bin/env python3
import math
import numpy as np
import utils as u


# probability that if attacker chooses a time t \in T, it falls on 50% of the
# population node, or right before:
# Pr[node_i chooses t ] = d / T for a delay d
# Pr[attacker targets 50%] = binomial(h/2,h,d/T)
# Pr[ 50% < target < 60% ] = binomialCDF(60%) - binomialCDF(50%)

n=100
att=n*(1.0/3.0)
hon=n - att
T = 80
delay = 10
pr_node = delay / T
target = int(0.5 * hon)
pr50 = u.binomial(target,hon,pr_node)
upto = int(0.60 * hon)
# Pr[ 50% < target < 60% ]
pr_to60 = u.binomial_cdf(upto,hon,pr_node) - u.binomial_cdf(target,hon,pr_node)
print("pr50: {}".format(pr50))
print("pr[50->60]: {}".format(pr_to60))


