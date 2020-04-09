import numpy as np 
import time
from math import floor

nh=60
na=40
ntot=na+nh
heights=range(250,151,10)
p=5./float(1*ntot)

sim=1000000

ec =[]


start_time = time.time()

## Here we consider the epoch boundary attack with a Byzantine (i.e. not rational
## fully malicious adversary).
## The idea is that whenever the adversary is elected leader it could potentially
## maintain two chains of same weight growing, but as soon as it is not
## elected leader anymore, then the honest players will have to converge to the same
## chain, assuming perfect synchronicity.
## however when the adversary is not elected leader (and stops the epoch boundary attack)
## it could still try and maintain the chain that has been abandoned by the honest players
## if the adversary gets luck then the abandoned chain can catch up with the other chain
## and thus the adversary can continue the epoch boundary attack.

for height in heights: #the adversary tries to keep maintaining two chain of same weight and
#length "height", we try different heights and see the probability of succeeding. Ig this probability is
#small enough, we consider this height a good finality candidate.
	win_ec = 0
	#longestfork =[]
	for i in range(sim):
		ch = np.random.binomial(nh, p, height)
		ca = np.random.binomial(na, p, height)
		# result of flipping a coin nha times, tested height times. (i.e. number of leaders
	# at ach slot for both adversary and honest players)
		j=0
		win =1
		while j<height-1 and win:
			if ca[j]==0:#the adversary is not elected leader in round j this means that in round
			#j+1 all the honest parties will mine on the same chain
				sumh = ch[j+1] #weight of honest chain "after forks" (assuming forks were of same length before)
				suma = ca[j+1] #weight of adversarial chain "after forks"
				ind = j+2 
				while sumh>suma and ind<height: #as soon as adversary catches up with honest chain, assume
				#it can create a fork again
					sumh+=ch[ind]
					suma+=ca[ind]
					ind+=1
				if ind == height and sumh>suma: #we have reach the end of the attack
				#and adversary has not catch up
					win =0
					break
				else: #adversary has catch up and can continue the forks until
				#it is not elected leader again
					j= ind

				#if the adversary did not catch up, we try to see
				#if it has a better chance by instead, trying to
				#perform a headstart attack from a round before
				if j>0 and win == 0 :
					if ch[j]/2 +ch[j+1] - (ca[j-1]-1+ca[j+1]) < ch[j+1]- ca[j+1]: #check if the advantage,
					#i.e. diff between abandoned and honest chain,
					#is better in this case (if not no need to try)
						sumh = ch[j]/2 +ch[j+1]#at round j the power of honest miners is still split between two chains
						#at round j+1 it goes all back to one chain
						suma = ca[j-1]-1+ca[j+1]#the adversary used all the blocks it withheld in period j-1
						#(all of them minus 1 that it used to maintain the forks)
						ind = j+2 
						while sumh>suma and ind<height: #as soon as adversary catches up with honest chain, assume
						#it can create a fork again
							sumh+=ch[ind]
							suma+=ca[ind]
							ind+=1
						if ind == height and sumh>suma: #we have reach the end of the attack
						#and adversary has not catch up
							win =0
							break
						else: #adversary has catch up and can continue the forks until
						#it is not elected leader again
							j= ind				
			else:
				j+=1
		if win ==1:
			win_ec+=1
		#longestfork.append(j)
	#print np.average(longestfork)
	ec.append(float(win_ec)/float(sim))

print ec

print("--- %s seconds ---" % (time.time() - start_time))