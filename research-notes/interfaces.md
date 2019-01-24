Interfaces
author: @sternhenri
====

EC: (randomness, distribution, weighting fn) -> (~1 provable leader)
Must guarantee:
eventual leader (on expectation one) found proportional to distrib
locally predictable, only at given epoch. (ie secret leader)
SPC: (network members, pledged storage) -> (power table -> regular proofs of storage from all members) 
Must guarantee:
Pledged and used storage is reflected in leader choice
Chosen leader does not influence power table
FIL: full system
Must guarantee:
All dealt storage is accounted for at regular intervals