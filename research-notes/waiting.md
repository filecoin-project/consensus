Waiting is irrational
author: @zenground0
===

One the key assumptions behind the design of Filecoin consensus is that rational miners will not necessarily wait to release blocks in the protocol specified block time without some PoW-style hardware-enforced reason to wait. Waiting could be enforced by a PoST (though this appears to be deprecated) or a VDF.

The intuition behind this does seem reasonable: miners are incentivized to get their blocks included in the chain and can get away with fudging timestamps to rush block propagation. This could eventually lead to a situation where high bandwidth highly connected miners are disproportionally represented in the chain which has centralizing effects on the network.

However we should be aware that this assumption is not considered by most other PoS consensus protocols out there. This can be explained in part because some of these protocols are not considering security in a rational actor model (i.e. Snow White and Algorand), but this isn't true across the board.

It would be great to articulate the "waiting can be irrational argument" as it has significant impact on consensus design.

Rough idea: one place to start is by examining how the sleepy consensus model responds to added rationality assumptions. One of the assumptions of SC/SW is that all alert node clocks are synchronized within delta, another is that the proportion of alert nodes is higher than the proportion of adversary nodes at any time.

One modification to the model is to consider nodes that occasionally lag more than delta from other honest nodes but out of rational interest do NOT reject chains with future timestamps in the hope of catching themselves up and winning block rewards. 1. Is this a rational strategy for nodes? 2. How would this group of not too powerful deviators (not too powerful because they experience delay and maybe we don't give them the full set of powers given to adversary in the sleepy model) affect the security guarantees of sleepy consensus?