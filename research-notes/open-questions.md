## Notes on Open Problems

author: @sternhenri
------

**Formally defining the EC/SPC Interface**
There are multiple candidate constructions for defining the interface between EC and SPC, we would like to work on a formal treatment of these interfaces and the tradeoffs amongst them. This work is relevant to making Filecoin consensus more modular.

**Efficient 51% block signing via all-to-all communications**
This problem deals with finality in SPC systems and attempts to prove that blocks that have been signed by 51% of storage in the chain can be deemed committed.

**Proof-of-Space before SEAL**
We are interested in exploring the ways in which miners could contribute to SPC security ahead of SEALING their pledged sectors. We have certain ideas on how to do this, but would like to explore them for use in the Filecoin protocol.

**PFT**
Power-Fault Tolerance reframes Byzantine Fault Tolerance in terms of the power or influence miners have over a network, for instance computation in Ethereum, Hashing power (or electricity) in Bitcoin, Storage in Filecoin. As the space grows, we believe that a formal treatment of consensus as a function of power rather than individual machines may become more appropriate to understanding the guarantees and limitations of various security models and consensus algorithms.

The team is working on early formalization of insights granted to us through work on Filecoin but is eager to find collaborators to pursue this work with.

**SPC**
Storage Power Consensus can be thought of as the intermediate layer of consensus in the Filecoin system, it sits atop the Filecoin protocol and build and maintains a power table which provably accounts for miners’ storage in the network, and then invokes a consensus algorithm (such as EC or SPC) to elect a leader at every round.

In this sense, SPC uses PoS to approxime a useful Proof-of-Work. We are interested in developing both formal treatments of the assumptions and guarantees SPC makes in a generic setting, as well as heuristics for SPC in the context of Filecoin.

This is a project the team is actively working on, and for which we seek interested collaborators or may even put out RFPs in the future.

