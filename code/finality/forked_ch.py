import numpy as np

def forked_ch(ch,ca,height):
	fork_finished = 0
	newch = [ch[0]+1]
	for i in range(1,height):
		if ca[i]>0 and fork_finished == 0 :
			## to do: what happened when ch[i] == 0?
			pi = float(ca[i])/float(ca[i]+ch[i])
			c = np.random.binomial(1,pi,1)[0]
			if c == 1:
				newch.append(1)
			else:
				newch.append(2)
		if ca[i]>0 and fork_finished == 1 :
			fork_finished = 0
			newch.append(1+ch[i])
		if ca[i]==0 and fork_finished ==0 :
			newch.append(1)
			fork_finished = 1
		if ca[i] ==0 and fork_finished == 1:
			newch.append(ch[i])
	return newch
