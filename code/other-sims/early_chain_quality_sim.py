import numpy as np 

nh=70
na=30
ntot=na+nh
height=13
p=1./float(ntot)
diff_praos=[]
diff_ec=[]
sim=100000
NumOfAttacks=1
diff_headstart=[]
adv=[]
hon=[]
adv_sucess=[]
h=[]
adv_abs=[]
success=0
j_chain=[]
for i in range(sim):
	adv_chain=0
	hon_chain=0
	for k in range(NumOfAttacks):
	#For Praos for a chain to grow we need to have at least one player
	#elected leader -> this raises the chain by one
	#at each height add one if at least one is elected
	#honest chain
	#not excatly, for each height we need to count one if there is one success!
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested 1000 times.
		# praosh=[1 for i in range(len(ch)) if ch[i]>0 ]
		# praosa=[1 for i in range(len(ca)) if ca[i]>0 ]

		# diff_praos.append(sum(praosh)-sum(praosa))
		# #for ghost the chain grows by the number of elected leader
		# #at each height add the number of elected leader

		diff_ec.append(sum(ch)-sum(ca))

		j=0
		for j in range(len(ch)):
			if ch[j]>0 and ca[j]>0:
				break
		if j<len(ch)-1: diff_headstart.append(sum(ch)-(sum(ca)+ch[j]))
		else: diff_headstart.append(sum(ch)-(sum(ca)))
		#print diff_headstart[i]
		#count only after j!
		h.append(j)
		#if j<len(ch)-1 and .. it means the attacker succeedeed in the head start attack
		# and the honest chain switches to its chain
		# ths the adversary cotrols the next blocks after j (until it releases)
		#and diff_headstart.append(sum(ch[j:])-(sum(ca[j:])+ch[j]))<0
		s=0
		if j<len(ch)-1 and sum(ch[j:])-(sum(ca[j:])+ch[j])<0: 
			success+=1
			s=1
		if j<len(ch)-1 : adv_chain+=sum(ch[j:])-(sum(ca[j:])+ch[j])
		else:  adv_chain+=0

		if s==1: 
			adv_chain_absolute=height-j
			j_chain.append(j)
			adv_sucess.append(height-j)
		else: adv_chain_absolute=0
	adv_abs.append(adv_chain_absolute)
	adv.append(adv_chain)
	hon.append(hon_chain)

print np.average(adv),np.average(j_chain),np.average(h),success/float(sim),np.average(adv_abs),np.average(adv_sucess), np.average(diff_ec)


#print np.average(diff_praos), np.average(diff_ec), np.average(diff_headstart)
