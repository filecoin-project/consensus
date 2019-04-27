/* Expected Consensus
--------------------------------- MODULE ec ---------------------------------
EXTENDS Integers, TLC, FiniteSets, Sequences
CONSTANT miners, NumMiners, USE_RANDOM

MaxRounds == 20
EarlyKill == 20
MaxLeaders == 5
rounds == 1..MaxRounds


Min(set) ==
    CHOOSE x \in set: \A y \in set: x <= y

Range(f) ==
    {f[x]: x \in DOMAIN f}

(* --algorithm ExpectedConsensus
variables
    miner_rounds = [miner \in miners |-> 2];
    leaders = <<{<<CHOOSE miner \in miners: TRUE, {}>>}, {}>>; \* Let someone win the first round.
    
define
    FairMining ==
        \A miner \in miners: miner_rounds[miner] - Min(Range(miner_rounds)) <= 1

    BoundedLeaders == 
        ~\E leader_group \in Range(leaders): Cardinality(leader_group) > MaxLeaders
    ModelBoundedLeaders == 
        ~\E leader_group \in Range(leaders): Cardinality(leader_group) > MaxLeaders - 1
    
    \* This invariant is used to force an error trace after MaxRounds.
    NoProgress ==
        /\ Len(leaders) < MaxRounds 
        /\ miner_rounds \in [miners -> 0..MaxRounds]

    Scratch(miner, tipset) ==
        \* all have equal chance of winning
        RandomElement(miners) = miner

end define;

fair process miner \in miners
begin
    Start:
        await /\ miner_rounds[self] = Min(Range(miner_rounds))
              /\ Len(leaders) >= miner_rounds[self] - 1;      
        if miner_rounds[self] >= MaxRounds then goto Done end if;
    Elect:
        with current_leaders = leaders[miner_rounds[self] - 1] do 
            if current_leaders = {} then
                leaders[Len(leaders)] := leaders[Len(leaders)] \union {<<self, {}>>};
            
                skip; \* TODO: Handle null mining.
            else
                with tipset \in SUBSET {x[1] : x \in current_leaders }  do
                    if USE_RANDOM then
                        if Scratch(self, tipset) then
                            leaders[Len(leaders)] := leaders[Len(leaders)] \union {<<self, tipset>>};
                        else 
                            skip;
                        end if;
                    else
                        with scratched \in BOOLEAN do
                            if scratched then
                                leaders[Len(leaders)] := leaders[Len(leaders)] \union {<<self, tipset>>};
                            else 
                                skip;
                            end if;
                        end with;
                    end if;
                end with;
            end if;
        end with;

        miner_rounds[self] := miner_rounds[self] + 1;
    goto Start;
                
end process;

fair process ticker = "ticker"
begin
    Tick:
        await \A m \in miners: miner_rounds[m] = Min(Range(miner_rounds));
        leaders := Append(leaders, {});
        goto Tick;
end process;

end algorithm; *)

\* BEGIN TRANSLATION
VARIABLES miner_rounds, leaders, pc

(* define statement *)
FairMining ==
    \A miner \in miners: miner_rounds[miner] - Min(Range(miner_rounds)) <= 1

BoundedLeaders ==
    ~\E leader_group \in Range(leaders): Cardinality(leader_group) > MaxLeaders
ModelBoundedLeaders ==
    ~\E leader_group \in Range(leaders): Cardinality(leader_group) > MaxLeaders - 1


NoProgress ==
    /\ Len(leaders) < MaxRounds
    /\ miner_rounds \in [miners -> 0..MaxRounds]

Scratch(miner, tipset) ==

    RandomElement(miners) = miner


vars == << miner_rounds, leaders, pc >>

ProcSet == (miners) \cup {"ticker"}

Init == (* Global variables *)
        /\ miner_rounds = [miner \in miners |-> 2]
        /\ leaders = <<{<<CHOOSE miner \in miners: TRUE, {}>>}, {}>>
        /\ pc = [self \in ProcSet |-> CASE self \in miners -> "Start"
                                        [] self = "ticker" -> "Tick"]

Start(self) == /\ pc[self] = "Start"
               /\ /\ miner_rounds[self] = Min(Range(miner_rounds))
                  /\ Len(leaders) >= miner_rounds[self] - 1
               /\ IF miner_rounds[self] >= MaxRounds
                     THEN /\ pc' = [pc EXCEPT ![self] = "Done"]
                     ELSE /\ pc' = [pc EXCEPT ![self] = "Elect"]
               /\ UNCHANGED << miner_rounds, leaders >>

Elect(self) == /\ pc[self] = "Elect"
               /\ LET current_leaders == leaders[miner_rounds[self] - 1] IN
                    IF current_leaders = {}
                       THEN /\ leaders' = [leaders EXCEPT ![Len(leaders)] = leaders[Len(leaders)] \union {<<self, {}>>}]
                            /\ TRUE
                       ELSE /\ \E tipset \in SUBSET {x[1] : x \in current_leaders }:
                                 IF USE_RANDOM
                                    THEN /\ IF Scratch(self, tipset)
                                               THEN /\ leaders' = [leaders EXCEPT ![Len(leaders)] = leaders[Len(leaders)] \union {<<self, tipset>>}]
                                               ELSE /\ TRUE
                                                    /\ UNCHANGED leaders
                                    ELSE /\ \E scratched \in BOOLEAN:
                                              IF scratched
                                                 THEN /\ leaders' = [leaders EXCEPT ![Len(leaders)] = leaders[Len(leaders)] \union {<<self, tipset>>}]
                                                 ELSE /\ TRUE
                                                      /\ UNCHANGED leaders
               /\ miner_rounds' = [miner_rounds EXCEPT ![self] = miner_rounds[self] + 1]
               /\ pc' = [pc EXCEPT ![self] = "Start"]

miner(self) == Start(self) \/ Elect(self)

Tick == /\ pc["ticker"] = "Tick"
        /\ \A m \in miners: miner_rounds[m] = Min(Range(miner_rounds))
        /\ leaders' = Append(leaders, {})
        /\ pc' = [pc EXCEPT !["ticker"] = "Tick"]
        /\ UNCHANGED miner_rounds

ticker == Tick

Next == ticker
           \/ (\E self \in miners: miner(self))
           \/ (* Disjunct to prevent deadlock on termination *)
              ((\A self \in ProcSet: pc[self] = "Done") /\ UNCHANGED vars)

Spec == /\ Init /\ [][Next]_vars
        /\ \A self \in miners : WF_vars(miner(self))
        /\ WF_vars(ticker)

Termination == <>(\A self \in ProcSet: pc[self] = "Done")

\* END TRANSLATION

\* Liveness == []<>(Len(leaders) <  5)
=============================================================================
