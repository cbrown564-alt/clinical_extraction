# ExECTv2 SeizureFrequency Agentic Redo — Hard Panel Results

Self-contained fresh study on the 53-letter dev140 hard panel (disagreement-bearing letters from the SF canonical row-adjudication), rescored on the production score_frequency_state.clinical_headline metric (not the state_profile/GEPA metric those letters were originally adjudicated on).

**Post-hoc finding (not predeclared):** 22/53 of this panel's letters have EMPTY gold SeizureFrequency annotations (the adjudication doc's own "gold annotated nothing" cases). `clinical_headline` F1 is structurally 0.0 on an empty-gold letter regardless of what's predicted -- even a perfectly correct empty prediction scores 0.0, not 1.0 (verified directly). This mechanically ties all 4 conditions at 0.0 on those letters and floors every condition's mean F1 equally, which is why the all-53 numbers below look far lower than the production SF headline (0.9053). The gate is evaluated on the 31 non-empty-gold letters only, where real per-letter signal exists; all-53 numbers are kept for transparency, not used for the gate decision.

## Condition Mean F1 -- all 53 letters (includes floor-effect letters)

| Condition | Mean F1 | n | True Failures |
| --- | ---: | ---: | ---: |
| single_greedy | 0.1547 | 53 | 0/53 |
| single_agent_tools_react | 0.1258 | 53 | 0/53 |
| multi_agent_d3_static | 0.1258 | 53 | 0/53 |
| multi_agent_dynamic_orchestrator | 0.1208 | 53 | 0/53 |

## Condition Mean F1 -- 31 non-empty-gold letters (informative subset)

| Condition | Mean F1 | n | True Failures |
| --- | ---: | ---: | ---: |
| single_greedy | 0.2645 | 31 | 0/31 |
| single_agent_tools_react | 0.2151 | 31 | 0/31 |
| multi_agent_d3_static | 0.2151 | 31 | 0/31 |
| multi_agent_dynamic_orchestrator | 0.2065 | 31 | 0/31 |

## Win/Loss vs single_greedy -- 31 non-empty-gold letters (gate basis)

| Candidate | Wins | Losses | Ties |
| --- | ---: | ---: | ---: |
| single_agent_tools_react vs single_greedy | 3 | 4 | 24 |
| multi_agent_d3_static vs single_greedy | 2 | 3 | 26 |
| multi_agent_dynamic_orchestrator vs single_greedy | 1 | 4 | 26 |
| multi_agent_dynamic_orchestrator vs multi_agent_d3_static | 1 | 3 | 27 |

## Win/Loss vs single_greedy -- all 53 letters (reference only, not gate basis)

| Candidate | Wins | Losses | Ties |
| --- | ---: | ---: | ---: |
| single_agent_tools_react vs single_greedy | 3 | 4 | 46 |
| multi_agent_d3_static vs single_greedy | 2 | 3 | 48 |
| multi_agent_dynamic_orchestrator vs single_greedy | 1 | 4 | 48 |
| multi_agent_dynamic_orchestrator vs multi_agent_d3_static | 1 | 3 | 49 |

## Predeclared Gate Outcomes

Evaluated on the non-empty-gold subset per the post-hoc finding above -- a metric-mechanics correction to where the panel actually carries signal, not a threshold change. The locked thresholds themselves are unchanged from the predeclaration.

- Angle 1 gate (react vs greedy): wins=3 losses=4 -> FAIL (locked threshold: wins>=5, losses<=1)
- Angle 2 dynamism gate (dynamic orchestrator vs d3-static): wins=1 losses=3 -> FAIL (locked threshold: wins>=3, losses<=1)

## Claim Boundary

dev140-only, aggregate + per-letter F1 on a fixed hard panel; no test59/test450 use, no holdout row-level inspection, no benchmark claim.
