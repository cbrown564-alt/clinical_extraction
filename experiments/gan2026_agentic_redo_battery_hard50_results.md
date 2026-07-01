# Gan 2026 Agentic Redo — Battery + Hard50 Results

Self-contained fresh study: all 5 conditions run in this session, same settings. Not compared against the 2026-06-12 hard50 numbers -- see docs/experiments/gan2026/agentic/gan2026_agentic_redo_results_2026-07-01.md for why that comparison was dropped (likely hosted-model drift, unverifiable and irrelevant to this run's internal validity).

## Condition-Final Accuracy

"True failures" = no usable answer produced at all (call error or unparseable/missing final_label) -- this is the reliability-relevant failure metric. "Repair rate" = the schema/label repair layer fixed a format issue but still produced a scored answer -- informative, not a failure (see predeclaration's evidence/schema-validity reporting requirement).

| Panel | Condition | Purist | Pragmatic | True Failures | Repair Rate |
| --- | --- | ---: | ---: | ---: | ---: |
| battery | single_greedy | 19/27 | 19/27 | 0/27 | 0/27 |
| battery | single_self_consistency_temperature | 18/27 | 18/27 | 0/27 | 0/27 |
| battery | single_agent_tools_react | 20/27 | 20/27 | 0/27 | 13/27 |
| battery | multi_agent_d3_static | 17/27 | 17/27 | 0/27 | 16/27 |
| battery | multi_agent_dynamic_orchestrator | 18/27 | 18/27 | 0/27 | 18/27 |
| hard50 | single_greedy | 19/50 | 21/50 | 0/50 | 0/50 |
| hard50 | single_self_consistency_temperature | 15/50 | 18/50 | 0/50 | 0/50 |
| hard50 | single_agent_tools_react | 23/50 | 24/50 | 1/50 | 30/50 |
| hard50 | multi_agent_d3_static | 29/50 | 29/50 | 5/50 | 31/50 |
| hard50 | multi_agent_dynamic_orchestrator | 32/50 | 32/50 | 1/50 | 35/50 |

## Win/Loss vs Comparators (hard50)

| Candidate | Comparator | Wins | Losses | Both correct | Both wrong |
| --- | --- | ---: | ---: | ---: | ---: |
| single_agent_tools_react | single_greedy | 12 | 8 | 11 | 19 |
| multi_agent_d3_static | single_greedy | 14 | 4 | 15 | 17 |
| multi_agent_dynamic_orchestrator | single_greedy | 17 | 4 | 15 | 14 |
| multi_agent_dynamic_orchestrator | multi_agent_d3_static | 7 | 4 | 25 | 14 |

## Predeclared Gate Outcomes

- Angle 1 gate (single_agent_tools_react vs single_greedy, hard50): wins=12 losses=8 -> FAIL (locked threshold: wins>=5, losses<=1)
- Angle 2 dynamism gate (dynamic_orchestrator vs d3_static, hard50): wins=7 losses=4 -> FAIL (locked threshold: wins>=3, losses<=1)

## Claim Boundary

validation-development matched-budget agentic redo; no holdout use, no row-level test450 inspection, and no benchmark claim.
