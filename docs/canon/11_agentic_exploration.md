# 11 — Agentic and multi-agent exploration

Last updated: 2026-08-16

The agentic and multi-agent architecture exploration evaluated whether decomposing extraction into specialized ReAct agents or dynamic multi-agent orchestrations could overcome the single-prompt plateau without requiring deterministic rule passes.

## Measured Findings (Gan 2026 hard50 and ExECTv2 dev140)

| Task / Panel | Condition | Primary Score | Win/Loss vs Single Greedy | Gate Outcome |
| --- | --- | ---: | ---: | --- |
| Gan hard50 | `single_greedy` | 19/50 (38.0%) | baseline | — |
| Gan hard50 | `single_agent_tools_react` | 23/50 (46.0%) | +4 net (12W / 8L) | **FAIL** (losses > 1) |
| Gan hard50 | `multi_agent_d3_static` | 29/50 (58.0%) | +10 net (14W / 4L) | — |
| Gan hard50 | `multi_agent_dynamic_orchestrator` | 32/50 (64.0%) | +13 net (17W / 4L) | **FAIL** (losses > 1) |
| ExECT dev140 | SF Agentic hard panel | — | Multi-agent ceiling reached | **FAIL** (did not clear promotion bar) |

## Interpretation & Claim Boundaries

1. **Decomposition Benefit**: Decomposing extraction into specialist agents (e.g. rate vs duration vs frequency) yielded accuracy gains over single-call greedy prompting on hard discrimination panels (+8% to +26% on Gan hard50).
2. **Dynamism vs Static Decomposition**: Dynamic orchestration (allowing the LM to choose specialist tools dynamically) outperformed static run-all decomposition (+3 net wins on Gan hard50).
3. **High Regression Rate on Clean Cases**: Neither ReAct single-agent nor dynamic multi-agent cleared the predeclared promotion gate (which required losses ≤ 1 on n=50). While the architectures recovered difficult cases, they introduced non-trivial regressions (4–8 losses out of 50) on rows where greedy was already correct.
4. **Conclusion**: Multi-agent and agentic decomposition did not achieve the consistency or reliability of the deterministic rule-augmented hybrid pipeline (`llm_with_rules`). The exploration was concluded as an exploratory negative comparator.

## Retained Evidence & Lineage

- Gan agentic redo results: `docs/research/gan2026/gan2026_agentic_redo_results_2026-07-01.md`
- Multi-agent research directions review: `docs/research/shared/exploratory_research_directions_multiagent_review_2026-07-01.md`
- Git lineage commit: `b2b1e3f3` / `da53aa3d`
