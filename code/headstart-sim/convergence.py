import numpy as np 
import matplotlib.pyplot as plt

nh=67000
na=33000
ntot=na+nh
height=2000
p=1./float(1*ntot)
sim=10000
nostart = 0
noend = 0
lengths = []
nostart_praos = 0
noend_praos = 0
lengths_praos = []

for i in range(sim):
	ch = np.random.binomial(nh, p, height)
	ca = np.random.binomial(na, p, height)
	# result of flipping a coin nha times, tested 1000 times.
	# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
	# put another way, it represents choice between longest honest and longest adv, and not between longest honests
	praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
	praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
	# print ch
	# print ca 
	w_a = 0
	w_h = 0
	wpraos_h = 0
	wpraos_a = 0
	start = -1
	end = -1
	wt_at_start = -1
	for idx, j in enumerate(ca):
		# start attack	
		if j>0 and start < 0:
			w_h = ch[idx]
			# headstart
			w_a = j + w_h
			# no headstart
			# w_a = j
			start = idx
			# only occurs without headstart
			if w_h == w_a:
				wt_at_start = wpraos_h
		# end attack
		elif start >= 0 and w_h >= w_a and (wt_at_start < 0 or wt_at_start != w_h):
			end = idx
			lengths.append(end-start)
			break
		# attack didn't start and sim ends
		elif start < 0 and idx == height - 1:
			nostart += 1
		# attack didn't end and sim ends
		elif start >= 0 and end < 0 and idx == height - 1:
			noend += 1
			# account for max
			end = height
			lengths.append(end-start)
		# move forward each step
		else:
			w_h += ch[idx]
			w_a += j 
	end = -1
	start = -1
	wt_at_start = -1
	for idx, j in enumerate(praosa):
		if j>0 and start < 0:
			wpraos_h = praosh[idx]
			wpraos_a = praosa[idx]
			# flag for special case where both win at attack start: prevents attack from ending in 
			# next round
			if wpraos_h == wpraos_a:
				wt_at_start = wpraos_h
			start = idx
		elif start >= 0 and wpraos_h >= wpraos_a and (wt_at_start < 0 or wt_at_start != wpraos_h):
			end = idx
			lengths_praos.append(end-start)
			break
		elif start < 0 and idx == height - 1:
			nostart_praos += 1
		elif start >= 0 and end < 0 and idx == height - 1:
			noend_praos += 1
			end = height
			lengths_praos.append(end-start)
		else: 
			wpraos_h += praosh[idx]
			wpraos_a += praosa[idx]

EC_avg = np.average(lengths)
pra_avg = np.average(lengths_praos)
print "EC: avg {avg}; med {med}; num of attacks {num}; num didn't start {nostart}, didn't end {noend}".format(avg=EC_avg, med = np.median(lengths), num=len(lengths), nostart=nostart, noend=noend)
print "Praos: avg {avg}; med {med}; num of attacks {num}; num didn't start {nostart}, didn't end {noend}".format(avg=pra_avg, med = np.median(lengths_praos),num=len(lengths_praos), nostart=nostart_praos, noend=noend_praos)		

# statement: the median is the distance such that an attacker creates a fork 50% of the time.
# Q1: how often can the attacker create a fork from the average?
def confidence_of_k(target, array):
	_sum = 0.0
	for idx, i in enumerate(array):
		# attack will fail
		if i < target:
			_sum += 1
	# attack succeeds
	return float(len(array) - _sum) / len(array) 
print "EC: Avg {avg} will succeed {num}".format(avg=EC_avg, num=confidence_of_k(EC_avg, lengths))
print "Praos: Avg {avg} will succeed {num}".format(avg=pra_avg, num=confidence_of_k(pra_avg, lengths_praos))

y_ec = []
y_praos = []
# x_value = [10,25,50,100,200,500,750,1000,1500]
x_value = range(1,2000, 5)
for lookback in x_value:
	ec_value = confidence_of_k(lookback, lengths)
	praos_value = confidence_of_k(lookback, lengths_praos)
	print "EC: k {avg} will succeed {num}".format(avg=lookback, num=ec_value)
	print "Praos: k {avg} will succeed {num}".format(avg=lookback, num=praos_value)
	y_ec.append(ec_value)
	y_praos.append(praos_value)

plt.plot(x_value, y_ec)
plt.plot(x_value,y_praos)
plt.show()


