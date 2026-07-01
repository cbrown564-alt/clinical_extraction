# Gan 2026 Agentic Redo — Battery + Hard50 Results

## Condition-Final Accuracy

| Panel | Condition | Purist | Pragmatic | Call/Parse Failures |
| --- | --- | ---: | ---: | ---: |
| battery | single_greedy | 18/27 | 18/27 | 0 |
| battery | single_self_consistency_temperature | 19/27 | 19/27 | 0 |
| battery | single_agent_tools_react | 20/27 | 20/27 | 18 |
| battery | multi_agent_d3_static | 16/27 | 16/27 | 15 |
| battery | multi_agent_dynamic_orchestrator | 20/27 | 20/27 | 13 |
| hard50 | single_greedy | 17/50 | 20/50 | 0 |
| hard50 | single_self_consistency_temperature | 11/50 | 13/50 | 0 |
| hard50 | single_agent_tools_react | 21/50 | 21/50 | 31 |
| hard50 | multi_agent_d3_static | 32/50 | 32/50 | 36 |
| hard50 | multi_agent_dynamic_orchestrator | 34/50 | 34/50 | 40 |

## Win/Loss vs Comparators (hard50)

| Candidate | Comparator | Wins | Losses | Both correct | Both wrong |
| --- | --- | ---: | ---: | ---: | ---: |
| single_agent_tools_react | single_greedy | 8 | 4 | 13 | 25 |
| multi_agent_d3_static | single_greedy | 16 | 1 | 16 | 17 |
| multi_agent_dynamic_orchestrator | single_greedy | 20 | 3 | 14 | 13 |
| multi_agent_dynamic_orchestrator | multi_agent_d3_static | 5 | 3 | 29 | 13 |

## Predeclared Gate Outcomes

- Angle 1 gate (single_agent_tools_react vs single_greedy, hard50): wins=8 losses=4 -> FAIL (locked threshold: wins>=5, losses<=1)
- Angle 2 dynamism gate (dynamic_orchestrator vs d3_static, hard50): wins=5 losses=3 -> FAIL (locked threshold: wins>=3, losses<=1)

## Claim Boundary

validation-development matched-budget agentic redo; no holdout use, no row-level test450 inspection, and no benchmark claim.
