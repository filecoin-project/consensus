import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

qs=[k/100.0 for k in range(2, 54, 2)]
# nh=48
# na=52
ntot=10000
sim=10000
heights = range(5,105,10)
blocks_back = range(5,105, 10)
d={}
height_max=95
success_ec_tot=[]
success_ec_without_tot=[]
success_praos_tot=[]
for q in qs:
	nh=round((1-q)*ntot)
	na=round(q*ntot)
	p=1./float(1*ntot)
	success_ec = [0]*len(heights)
	success_ec_without = [0]*len(heights)
	success_praos = [0]*len(heights)
	for i in range(sim):
		ch = np.random.binomial(nh, p, height_max)
		ca = np.random.binomial(na, p, height_max)
		praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		for idx ,height in enumerate(heights):
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
			w_a = sum(ca[:height])+ch[0]
			w_h = sum(ch[:height])
			wpraos_h = sum(praosh[:height])
			wpraos_a = sum(praosa[:height])
			w_without_headstart_a = sum(ca[:height])
			w_without_headstart_h = sum(ch[:height])
			if w_a>=w_h: success_ec[idx] += 1
			if wpraos_a>=wpraos_h: success_praos[idx] += 1
			if w_without_headstart_a>w_without_headstart_h: success_ec_without[idx] += 1

	success_ec_tot.append([i/float(sim) for i in success_ec])
	success_praos_tot.append([i/float(sim) for i in success_praos])
	success_ec_without_tot.append([i/float(sim) for i in success_ec_without])
# print "EC: {suc};".format(suc=[i/float(sim) for i in success_ec])
# print "Praos: {suc};".format(suc=[i/float(sim) for i in success_praos])
# print "EC without tipset: {suc};".format(suc=[i/float(sim) for i in success_ec_without])


print "EC"
df = pd.DataFrame(success_ec_tot, columns=blocks_back, index=qs)
print df

print "EC without HeadStart"
df = pd.DataFrame(success_ec_without_tot, columns=blocks_back, index=qs)
print df

print "EC without TipSets"
df = pd.DataFrame(success_praos_tot, columns=blocks_back, index=qs)
print df
