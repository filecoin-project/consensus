# Code

---

This section of the repository holds most of the simulation code used as part of work on Filecoin's Expected Consensus. 

Below, the list of sims.

#### Sims in use

- [convergence](./other-sims/convergence) -- Main Monte-Carlo simulation for EC, modeling finality against withholding attack (as in [BTC section 11](https://bitcoin.org/bitcoin.pdf)).
  - Generates results for convergence (probability a longer adversarial chain was generated starting x blocks back, for variable x) and chain quality (portion of adversarial:honest blocks mined as compared to their relative power).
  - Used for setting recommended conf time in EC, under various settings.
  - Jump to the [list of sim settings](#monte-carlo-settings)
- [markov](./other-sims/ec-markov.py) -- Markov Chain closed-form for EC, as described in [confirmation time observable](https://observablehq.com/d/432bc3aeac0ca166).
  - Models gap between honest and adversarial chain as markov states and maps evolution of the gap over a number of rounds.
  - Works with weighting-fn
  - Works with lbp
  - Works with headstart
- [generate-chain](./other-sims/generate-chain) -- simply outputs short runs of binomial tosses for a set number of miners with equal probability of winning.
  - Helpful to visualize how many blocks can be found per round on expectation in EC, e.g. for visualizing how often null blocks can be found (counterintuitively high).
- [ec-sim-zs](./ec-sim-zs) -- Golang sim and viz of EC.
  - Ultra-aggressive (irrational) mining strategy: mine every available fork, release if heavier (no weighting fn) than your own.
  - Includes editable lbp
  - Useful for head change visualisation.
  - It helps graph the impact of having a randomness lookback on a miner's ability to NaS

### Other Sims

- [ec-sim-w](./ec-sim-w/) -- Golang early sim of how EC works (not to spec).
- [attacks](./attacks) -- Two sims helpful for calculating closed-form forking factor and bounds for EC, related to an (incomplete) [analysis of attacks in EC](https://www.overleaf.com/project/5be983c5db30c7318939372d).

### Monte-Carlo Settings

The list below lays out the different parameter-sets that can be used with the [Monte-Carlo sim](./other-sims/convergence.py) to simulate various results for EC.

In short, the sim uses binomials to estimate number of blocks per round for EC for honest and adversarial miners over series of rounds. It models what an adversary might do by running standard selfish mining, and keeps track of

- how often they mine blocks (vs expected from their power) -- quality
- longest run of block withholding in series -- convergence/finality

#### Params list

Below, the list of parameters to be changed as part of experiments. The full list of settings is printed out after a run for reproducibility.

- store_output -- bool -- True: will store output of run in json under ./monte/; False: only command line output
- alphas -- array, values in [0, .5] -- set of adversarial powers to simulate.
- lookahead -- integer, value >= 1 -- gives power to adversary to simulate randomness lookback.
- rounds_back -- array, values in N+ -- use if looking for outputs of likelihood of successful attack for specific number of rounds back
- e_blocks_per_round -- array, values in N+ -- expected number of blocks per round. Default: 1
- num_sims -- integer, value in N+ -- number of sims to run from which to sample results. Key in that it implies precision for results, eg 100 sims means % level precision, 1,000 means first decimal, 10,000 means second decimal... Sim slows linearly in num_sims.
- target_conf -- array, values in [0,1] -- target security parameter we want: for how far back is proba of a competing chain less than target_conf likely to be found
- Sim-to-run -- array, values in {Sim.EC, Sim.NOHS, Sim.NOTS} -- what model of consensus to run sim over.
  - NOTS -- No TipSets. Ignores potential multiple honest blocks found in a round.
  - NOHS -- No [HeadStart](https://github.com/filecoin-project/consensus/issues/22). Idealized EC (optimistic).
  - EC -- TipSets with HeadStart.
- Wt_fn -- bool -- use number of blocks as measure of weight (false) or use [custom weight fn](https://observablehq.com/d/3812cd65c054082d) (true). The following params make up custom wt fn:
  - powerAtStart -- int, N+ -- PB size of network at start of sim. Default: 5000
  - powerIncreasePerDay -- float, in R*+ -- % increase in storage capacity of network per day. Default: .025 (2.5%)
  - wPunishFactor -- float, in [0, 1] -- see [weight fn observable](https://observablehq.com/d/3812cd65c054082d)
  - wStartPunish -- integer, in N+ -- see [weight fn observable](https://observablehq.com/d/3812cd65c054082d)
  - wBlocksFactor -- float, in [0, inf] -- see [weight fn observable](https://observablehq.com/d/3812cd65c054082d)

Typically static:

- Miners -- integer, > 100 -- all miners have equal power so p = expected_number_of_blocks_per_round/miners. Have found that for m > 100, sim results mostly converge. Default: 10k
- sim_rounds -- integer, in N+ -- This number is how long each simulation lasts (in rounds). Needs to be long enough so that longest selfish run is representative of adv power. Default: 5k

#### Example uses

- Understanding tradeoffs of TipSets in EC (comparing EC, NOHS, NOTS)
  - Used to determine how costly TipSets are to consensus. See [early-sims](https://github.com/filecoin-project/consensus/issues/67)
  - Important factors to modulate: 
    - sim_to_run
- Understanding impact of different expected blocks per round
  - Important factors to modulate: 
    - e_blocks_per_round
- Understanding impact of lookback
  - Important factors to modulate:
    - lookahead