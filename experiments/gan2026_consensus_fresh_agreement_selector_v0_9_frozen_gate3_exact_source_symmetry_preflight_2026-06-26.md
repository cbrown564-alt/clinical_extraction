# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 3 Exact Source-Symmetry Preflight

- Date: `2026-06-26`
- Surface: `test450` metadata inventory only
- Split manifest: `data/Gan (2026)/splits/gan2026_split_v1.json`
- Split manifest SHA-256: `5dd39c552bcb60a40f0c79245a9f7346fd27a064cd27263c902e879af3bf7c57`
- Test manifest rows: `450`
- Gate passed: `true`
- Gate scope: `exact_source_symmetry`
- Consensus mode: `exact_three_agent_unanimous_label`
- Locked test audit authorized by this report: `false`

## Inspection Boundary

This preflight inspected only technical metadata: artifact paths, hashes,
`source_row_index` coverage, duplicate/off-manifest counts, call/parse
counts, prompt-input key metadata, and component role metadata. It did
not report or develop from gold labels, row correctness, rationales,
evidence text, selected events, or row-level transitions.

## Role Parity

- Deterministic role parity: `True`
- Validation consensus floor: `experiments\gan2026_hybrid_rules_candidates_llm_adjudicator_validation750_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`
- Exact test consensus floor: `experiments/gan2026_hybrid_rules_candidates_llm_adjudicator_test450_gpt41mini_v02_cluster_diary_candidate_recall_live_2026-06-02.jsonl`
- Consensus policy parity: `True`
- Validation consensus condition: `rules_tool_plus_structured_event_unanimous_exact_label_v0`
- Exact test consensus condition: `rules_tool_plus_three_structured_event_agents_unanimous_exact_label_v0`
- Fresh-evidence counterpart accepted: `True`
- Validation fresh prompt: `gan2026_fresh_evidence_reasoner_v0_4`
- Test fresh prompt: `gan2026_fresh_evidence_reasoner_v0_6`

The test fresh-evidence component is not prompt-identical to the validation v0.4 artifact. It is treated as the protocol-documented frozen exact holdout counterpart: v0.6 with safety v0.9, named before this exact-source preflight.

## Required Components

| Component | Role | Coverage | Duplicates | Off manifest | Calls failed | Parse/repair rows | Prompt hygiene | Row boundary | SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| deterministic_rules_tool_floor | validation-matched deterministic rules-tool floor | 450/450 | 0 | 0 | 0 | 5 | `n/a` | `n/a` | `8155612105b462ec126df3aaebe5e81e2d730448babe1fcc3bfa60348e45dbf2` |
| consensus_exact_three_agent | exact three-agent consensus component | 450/450 | 0 | 0 | 0 | 0 | `n/a` | `pass` | `ad651d457b04c25611bf78fc262a9ada39416ca93de7fb809794fc6cb9efab59` |
| fresh_evidence_v06_safety_v09 | protocol-documented frozen fresh-evidence holdout counterpart | 450/450 | 0 | 0 | 0 | 450 | `pass` | `n/a` | `e317b088bbcdc0a2f668b0e600bccaf17664a5d4ae2e734c0531684e786a1295` |

## Source Substrates

| Substrate | Role | Coverage | Duplicates | Off manifest | Calls failed | Parse/repair rows | Prompt hygiene | Row boundary | SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| gpt_structured_events_v05 | GPT structured-event source substrate | 450/450 | 0 | 0 | 0 | 308 | `pass` | `n/a` | `0c9bd96a49cfd22e57f2f9c421dbc78bf0e3a0f16233a67e09c853c174c2b40c` |
| qwen_structured_events_recent_patch | Qwen structured-event source substrate with validation-matched recent patch role | 450/450 | 0 | 0 | 0 | 382 | `pass` | `n/a` | `61ac7d12c9580188c3f5c467a41d55d4962cf7f81052e5617dd19868ef997f59` |
| deepseek_structured_events_v06 | DeepSeek structured-event source substrate | 450/450 | 0 | 0 | 0 | 311 | `pass` | `n/a` | `d57dc30c7c859c47e072e9278df3f2be1e70c56a9e62acae0e16f43f5c0cddca` |

## Interpretation

Gate 3 passes as exact source-symmetry for the selector source set.
The missing exact three-agent consensus test replay has been generated
and hash-pinned. The deterministic floor is aligned to the validation
rules-tool baseline role, not the older constrained Gate 4 canonical
pipeline comparator. The fresh-evidence component is accepted as the
protocol-documented frozen holdout counterpart, with the prompt/safety
version difference named above.

This report does not authorize Gate 4. The next step requires explicit
user authorization for one fresh aggregate-only exact-source locked
`test450` audit.
