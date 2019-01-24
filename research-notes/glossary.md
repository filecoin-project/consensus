Glossary
author: @sternhenri, @zenground0
=====

Seed -- What we use as input to generate randomness in a round of leader election
Grinding --
Ticket -- Implementation choice as seed.
Slot -- Period over which a leader is elected. 0 or 1 blocks can be generated in a slot.
Round -- Same as slot.
Epoch -- Period over which a same seed is used as a source of randomness for a leader. Multiple of slots (1 to n).
PoST -- A primitive built from proof of replication (using VDF under the hood) and SNARKs that cryptographically verifies that specific data was stored for a given amount of time.
Candidate VDF for leader election.
VDF -- A cryptographic primitive that takes a verifiable number of computations to compute but can be verified in a constant number of steps.  Full definition online. 
Running a PoST can be thought of as a VDF for leader election.
Lookback-parameter -- the number of blocks (or slots, or units of time) traversed back in a blockchain to fetch the value of a seed or a committee