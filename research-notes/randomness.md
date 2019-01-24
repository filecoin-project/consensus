##Randomness

author: @sternhenri, @zenground0

-----------

**Random oracle:**
Let’s assume we have a perfect randomness beacon
It spits out a single seed at every slot
It generates them instantly
They are all independent
All miners get them instantly

Every miner uses that to see if they’ve won at each slot
It gets us:
Same random seed for all miners at time t (ie no grinding via forks)
Recovery from attack at every slot (derived from independent seeds)
Random number is verifiable by all parties at every slot

**Need-to-have:**
2 - Should not use more than 2 CPUs at any time
4 - Should not be globally predictable
5 - Should be immediately globally verifiable
6 - Should be able to recover from an attack
Refresh randomness if there is bias
Successful attack at t, has no impact on t+1
7 - Nodes should be able to participate sporadically (need to be online always vs need to be online at some time)

**Nice-to-have:**
A - Should prevent grinding
B - Should not be locally predictable beyond 1-recent
C - each seed is independent from past ones
1 - Should be “easy” to resume/catch-up after interruption

(from: https://docs.google.com/presentation/d/1wL9wWvQ0nlOYxQhmzg8uiEyX2B77e6ruZQulFMKatV8/edit#slide=id.g4690a1b346_2_50)

**Problems:**
Global predictability -- prepared DOS attacks against leader

- Tool: VRF to calculate randomness input to leader election given public seed

Local predictability of leader election -- predictable selfish mining / double spending, fork grinding

- Tool: VDFs to prevent knowing in advance, sampling from recent past

Power over seed -- leads to grinding

- Tool: Epoch-based seed selection, lookback parameters, off-chain randomness

Other tooling:

- Lookback parameters (for committee or seed)
- Duration of seed use (epochs)
- MPC
- SW timestamp ordering