#!/usr/bin/env python3
import utils as u

e=5
att=1/3
h=1-att
max_block=20


maxGrindPr = 0
maxNoGrindPr = 0
for hb1 in range(max_block):
    for ab1 in range(max_block):
        for ab2 in range(max_block):
            totalA= ab1 + ab2
            # - 1
            totalGrindPr = 0
            totalNoGrindPr = 0
            for grinded in range(totalA):
                # HonestToFind
                # honest must find this value at second round to have 
                # a heavier chain
                htf = totalA - grinded
                # probability that honest finds less than htf
                phtf = u.poisson_cdf(htf, h*e)
                # probability of winning for adversary means:
                #  1 honest finds hb1 blocks in first round
                #  2 attacker finds ab1 blocks in first round
                #  3 honest finds less than htf blocks in second round
                #  4 attacker finds ab2 blocks in second round
                p1 = u.poisson(hb1,h*e)
                p2 = u.poisson(ab1,att*e)
                p3 = 1 - u.poisson_cdf(htf,h*e)
                p4 = u.poisson(ab2,att*e)
                pwinA = p1 * p2 * p3 * p4
                totalGrindPr += pwinA
        
            # probability of winning for adversary that don't grind is
            # computed as the same way as for no grinding but there is only one
            # tentative for the attack, no "for grinded" loop
            # 1. honest finds hb1 blocks in first round
            # 2. attacker finds ab1 blocks in first round
            # 3. honest finds less than totalA at second round
            # 4. attacker finds ab2 blocks in second round
            p1 = u.poisson(hb1,h*e)
            p2 = u.poisson(ab1,att*e)
            p3 = 1 - u.poisson_cdf(totalA,h*e)
            p4 = u.poisson(ab2,att*e)
            pwinANoGrind = p1*p2*p3*p4
            totalNoGrindPr += pwinANoGrind

            if totalGrindPr > maxGrindPr:
                maxGrindPr = totalGrindPr

            if totalNoGrindPr > maxNoGrindPr:
                maxNoGrindPr = totalNoGrindPr

print("max probability when grinding {:.4f}".format(maxGrindPr))
print("max probability when no grinding {:.4f}".format(maxNoGrindPr))
print("ratio: {:.4f}".format(maxGrindPr/maxNoGrindPr))



