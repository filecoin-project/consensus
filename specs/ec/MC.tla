---- MODULE MC ----
EXTENDS ec, TLC

\* MV CONSTANT declarations@modelParameterConstants
CONSTANTS
M1, M2, M3
----

\* MV CONSTANT definitions miners
const_1556327768723618000 == 
{M1, M2, M3}
----

\* SYMMETRY definition
symm_1556327768723619000 == 
Permutations(const_1556327768723618000)
----

\* CONSTANT definitions @modelParameterConstants:1NumMiners
const_1556327768723620000 == 
3
----

\* CONSTANT definitions @modelParameterConstants:2USE_RANDOM
const_1556327768723621000 == 
TRUE
----

\* CONSTRAINT definition @modelParameterContraint:0
constr_1556327768723622000 ==
ModelBoundedLeaders
----
\* SPECIFICATION definition @modelBehaviorSpec:0
spec_1556327768723623000 ==
Spec
----
\* INVARIANT definition @modelCorrectnessInvariants:0
inv_1556327768723624000 ==
FairMining
----
\* INVARIANT definition @modelCorrectnessInvariants:1
inv_1556327768723625000 ==
BoundedLeaders
----
\* INVARIANT definition @modelCorrectnessInvariants:2
inv_1556327768723626000 ==
NoProgress
----
=============================================================================
