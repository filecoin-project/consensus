import numpy as np 

nh=66667
na=33333
ntot=na+nh
heights=range(200,201,50)
p=1./float(1*ntot)

sim=1000000

ec =[]
praos = []

for height in heights:
	win_ec = 0
	win_praos = 0
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# is this sim of praos overly optimistic: it glosses over potential fork when multiple honest wins
		# put another way, it represents choice between longest honest and longest adv, and not between longest honests
		praosh=[1 if ch[i]>0 else 0 for i in range(len(ch))]
		praosa=[1 if ca[i]>0 else 0 for i in range(len(ca))]
		w_a = ch[0]+sum(ca)#num,ber of blocks created by adversary + headstart
		w_h = sum(ch)
		wpraos_h = sum(praosh)
		wpraos_a = sum(praosa)

		if w_a>=w_h: win_ec+=1
		if wpraos_a>=wpraos_h: win_praos+=1
	print win_ec, win_praos
	ec.append(float(win_ec)/float(sim))
	praos.append(float(win_praos)/float(sim))

print ec, praos