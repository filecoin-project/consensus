#!/usr/bin/env python3
import utils as u

# This scripts computes the advantage of running the lookfwd attack according to
# the paper formula (lookfwd.pdf)
e=5
att=1/3

def ratio(e,att):
    honest=1-att
    p0 = u.poisson(0,honest*e)
    b = u.poisson(1, att*e)
    ratio = 1 / (1 - b * p0 * e)
    return ratio

print("e = {}, attacker fraction = {}".format(e,att))
print("-> ratio is {}".format(ratio(e,att)))
