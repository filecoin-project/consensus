import numpy as np 
import time

nh=66667
na=33333
ntot=na+nh
heights=range(20000,100001,1000)
p=5./float(1*ntot)

sim=10000 

ec =[]
praos = []

start_time = time.time()

for height in heights:
	win_ec = 0
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		# praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		# praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		evench = [ch[i] if i%2 == 0 else 0 for i in range(len(ch))]
		oddch = [ch[i] if i%2 == 1 else 0 for i in range(len(ch))]
		chain_A = [sum(ca[:-1])+ sum(oddch)]
		chain_B = [sum(ca[1:])+ sum(evench) + ch[1]]

		if chain_A==chain_B: win_ec+=1
	print win_ec
	ec.append(float(win_ec)/float(sim))


print ec

print("--- %s seconds ---" % (time.time() - start_time))