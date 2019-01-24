**Note: THE FILECOIN PROJECT IS STILL EXTREMELY CONFIDENTIAL. Do not share or discuss the project outside of designated preview channels (chat channels, Discourse forum, GitHub, emails to Filecoin team), not even with partners/spouses/family members. If you have any questions, please email legal@protocol.ai.**

# Filecoin Consensus
---

One of Filecoin's main goals is to create a useful Proof-of-Work based on storage, building upon past work in both Proof-of-Work and Proof-of-Stake protocols.

This repository houses a lot of our work on this area of research: Filecoin consensus. While it is by no means exhaustive, it should provide a good place from which to start engaging on Filecoin consensus research. You may also want to read up on [Filecoin](https://github.com/filecoin-project/specs) and [Filecoin Research](https://github.com/filecoin-project/research).

## Table of Contents

- [What is consensus in Filecoin?](#what-is-consensus-in-filecoin?)

- [License](#license)

## What is consensus in Filecoin?

The state of the Filecoin network (i.e. who stores what where) is maintained in a blockchain. It is updated as new blocks are mined by a chosen network participant at regular intervals. This "leader" earns FIL for this and is chosen from the set of participants in the Filecoin network in proportion to how much storage they have on the network. In proceeding thus, block creation
- Provably updates the state of the Filecoin network to reflect network activity;
- Mints new FIL tokens that can be used to buy or sell storage;
- Incentivizes actors to put storage on the network. 

All of this happens through the composition of three distinct protocols:
1. The Filecoin protocol -- which specifies how storage and retrieval works in the network, and allows participants broadly to participate.
1. Storage Power Consensus (SPC) -- which generates a power table from the protocol, provably reflecting how much storage participants have effectively committed to the network.
1. Expected Consensus (EC) -- which is invoked during leader election to select a miner from a weighted set of participants.

These protocols are meant to be modular and have [interfaces](link) which enable us to swap them out or improve them without affecting the rest of the Filecoin stack, for instance updating proofs without changing how SPC functions, or leader election without changing the Filecoin protocol.

## Consensus Research

#### Current state of Filecoin consensus work

To gain familiarity with this subject matter, we refer the reader to:
- [Filecoin Spec](https://github.com/filecoin-project/specs/) -- The spec is the output of these research efforts and reflects our must up-to-date working version of the protocols. The reader may specifically want to look at:
    - [Expected Consensus](https://github.com/filecoin-project/specs/blob/master/expected-consensus.md)
    - [Mining](https://github.com/filecoin-project/specs/blob/master/mining.md) -- the routine that invokes expected consensus.
- [Filecoin Whitepaper](https://filecoin.io/filecoin.pdf) -- We urge readers to pay special attention to Section 6: `Useful Work Consensus`.
- [Power Fault Tolerance Technical Report](https://filecoin.io/power-fault-tolerance.pdf) (PFT) -- Outlining some of the motivations and implications of this work, reframing Byzantine Fault Tolerance as a function of power committed to the network (in our case storage) rather than number of nodes.

#### Current avenues of research

Most of our work to date focuses on 

| **Topic** | **Description** | **Status** | **Links** |
| --- | --- | --- | --- | --- |
| Security Model | 
| Assumptions | 
| Formal Treatment of EC soundness | 
| EC incentive compatibility | 
| Attacks | 
| Design Decisions | specifically, LBP, Slashing, Weighting, VDF use
| Convergence | 
| Finality | 
| Null Blocks |
| SSLE |
| Formalizing PFT | 
| Slashing Spec | 


## Common Questions

**Why EC?**

Permissionless, robustly (dynamically) reconfigurable, (power table can be updated)

**Where does it fit into FIL?**

**Common misconceptions**
We use tickets for two reasons in the spec as currently laid out:
Preventing PoST precomputation - we use winning tickets from the previous block as our challenge for PoSTs.
Wanted property of ticket: “verifiable” recency on the chain
Leader Election - we use the tickets from a miner’s PoST as provable means of secretly and provably checking whether one’s been elected to post the block
Wanted property of ticket: “verifiable” input on the chain
Claim: These uses of tickets are entirely unrelated, and could be swapped out from some random on-chain or off-chain source of verifiable randomness.
Collateral for what? (solved)
Miners can earn FIL in two ways:
by mining FIL through participation in EC
May involve slashing as a means of speeding up convergence/disincentivizing divergence
by fulfilling orders
Will involve slashing as a means of punishing broken contracts
We loosely refer to both of these as mining, in fact, strictu sensu, only participation in EC is mining
Claim 1: The collateral needs for both actions are distinct different (in fact EC may not strictly require collateral).
Claim 2: Only EC need involve FIL, for all intents and purposes market-making (renting out space) could happen through whatever currency
As it happens the requirement for doing either of these actions is the same: pledging storage to the network, but the relationship between the two is complex:
Mining implies fulfilling orders (no orders -> no power -> pointless mining)
Fulfilled orders likely implies mining (if giving power to the network, why not try and earn extra income through consensus?)
PoSTs for what?  (solved) -- from call today it was just a way to reuse a VDF
Related to the above, it seems there are two reasons to generate PoSTs:
Mining FIL (through EC)
By creating a ticket
By maintaining power table
Proving storage to a client (in an order)
Claim: miners elected to post a block should be incentivized to include other miners’ PoSTs in spite of the impact it has on the power table (and thus their likelihood to mine again)
Block reward for what?
Claim: In traditional PoW/PoS, miners participate in the system for the block reward; in our case, given a utility token, it may not be the main reason they do.

**EC vs SSLE**



## Other docs/sims

## License

The Filecoin Project is dual-licensed under Apache 2.0 and MIT terms:

- Apache License, Version 2.0, ([LICENSE-APACHE](https://github.com/filecoin-project/research/blob/master/LICENSE-APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
- MIT license ([LICENSE-MIT](https://github.com/filecoin-project/research/blob/master/LICENSE-MIT) or http://opensource.org/licenses/MIT/)