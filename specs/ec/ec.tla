/* Expected Consensus
--------------------------------- MODULE ec ---------------------------------
EXTENDS Integers, TLC, FiniteSets, Sequences

Min(set) ==
    CHOOSE x \in set: \A y \in set: x <= y

Range(f) ==
    {f[x]: x \in DOMAIN f}

(* --algorithm ExpectedConsensus
variables
    NumMiners=5;
    miners = 1..NumMiners;
    MaxRounds=10;
    MaxLeaders = 3;
    rounds = 1..MaxRounds;
    miner_rounds = [miner \in miners |-> 0];
    leaders = <<{}>>;
    
define
    FairMining ==
        \A miner \in miners: miner_rounds[miner] - Min(Range(miner_rounds)) <= 1

    BoundedLeaders == 
        ~\E leader_group \in Range(leaders): Cardinality(leader_group) > MaxLeaders
        
    NoProgress ==
        miner_rounds[CHOOSE m \in miners: TRUE] < 11
        
    Scratch(miner) ==
        \* all have equal chance of winning
        LET e == RandomElement(miners) IN
            e = miner

end define;

process miner \in miners
begin
    Start:
        await miner_rounds[self] <= Min(Range(miner_rounds));
        if Scratch(self) then
            leaders := <<Head(leaders) \union {self}>> \o Tail(leaders);
        else 
            skip;
        end if;
        
    Tick:
        miner_rounds[self] := miner_rounds[self] + 1;
        if \A miner \in miners: miner_rounds[miner] = Min(Range(miner_rounds)) then
            leaders := <<{}>> \o leaders;
        end if;
    goto Start;
                
end process;

end algorithm; *)

\* BEGIN TRANSLATION
VARIABLES NumMiners, miners, MaxRounds, MaxLeaders, rounds, miner_rounds, 
          leaders, pc

(* define statement *)
FairMining ==
    \A miner \in miners: miner_rounds[miner] - Min(Range(miner_rounds)) <= 1

BoundedLeaders ==
    ~\E leader_group \in Range(leaders): Cardinality(leader_group) > MaxLeaders

NoProgress ==
    miner_rounds[CHOOSE m \in miners: TRUE] < 11

Scratch(miner) ==

    LET e == RandomElement(miners) IN
        e = miner


vars == << NumMiners, miners, MaxRounds, MaxLeaders, rounds, miner_rounds, 
           leaders, pc >>

ProcSet == (miners)

Init == (* Global variables *)
        /\ NumMiners = 5
        /\ miners = 1..NumMiners
        /\ MaxRounds = 10
        /\ MaxLeaders = 3
        /\ rounds = 1..MaxRounds
        /\ miner_rounds = [miner \in miners |-> 0]
        /\ leaders = <<{}>>
        /\ pc = [self \in ProcSet |-> "Start"]

Start(self) == /\ pc[self] = "Start"
               /\ miner_rounds[self] <= Min(Range(miner_rounds))
               /\ IF Scratch(self)
                     THEN /\ leaders' = <<Head(leaders) \union {self}>> \o Tail(leaders)
                     ELSE /\ TRUE
                          /\ UNCHANGED leaders
               /\ pc' = [pc EXCEPT ![self] = "Tick"]
               /\ UNCHANGED << NumMiners, miners, MaxRounds, MaxLeaders, 
                               rounds, miner_rounds >>

Tick(self) == /\ pc[self] = "Tick"
              /\ miner_rounds' = [miner_rounds EXCEPT ![self] = miner_rounds[self] + 1]
              /\ IF \A miner \in miners: miner_rounds'[miner] = Min(Range(miner_rounds'))
                    THEN /\ leaders' = <<{}>> \o leaders
                    ELSE /\ TRUE
                         /\ UNCHANGED leaders
              /\ pc' = [pc EXCEPT ![self] = "Start"]
              /\ UNCHANGED << NumMiners, miners, MaxRounds, MaxLeaders, rounds >>

miner(self) == Start(self) \/ Tick(self)

Next == (\E self \in miners: miner(self))
           \/ (* Disjunct to prevent deadlock on termination *)
              ((\A self \in ProcSet: pc[self] = "Done") /\ UNCHANGED vars)

Spec == Init /\ [][Next]_vars

Termination == <>(\A self \in ProcSet: pc[self] = "Done")

\* END TRANSLATION
=============================================================================
\* Modification History
\* Last modified Tue Apr 23 17:17:30 PDT 2019 by porcuquine
\* Created Mon Apr 22 20:51:05 PDT 2019 by porcuquine
