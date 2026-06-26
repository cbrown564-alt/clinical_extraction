# Gan 2026 Consensus/Fresh v0.9 Frozen Gate 3 Source-Symmetry Preflight

- Date: `2026-06-26`
- Surface: `test450` metadata inventory only
- Split manifest: `data/Gan (2026)/splits/gan2026_split_v1.json`
- Split manifest SHA-256: `5dd39c552bcb60a40f0c79245a9f7346fd27a064cd27263c902e879af3bf7c57`
- Test manifest rows: `450`
- Gate passed: `true`
- Gate scope: `constrained_source_symmetry`
- Consensus mode: `closest_available_constrained_two_agent`
- Locked test audit authorized by this report: `false`

## Inspection Boundary

This preflight inspected only technical metadata: artifact paths, hashes,
`source_row_index` coverage, duplicate/off-manifest counts, call/parse
counts, and prompt-input key metadata. It did not report or develop from
gold labels, row correctness, rationales, evidence text, selected events,
or row-level transitions.

## Required Components

| Component | Role | Coverage | Duplicates | Off manifest | Calls failed | Parse/repair rows | Prompt hygiene | Prompt rows checked | SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| deterministic_floor | deterministic test component | 450/450 | 0 | 0 | 0 | 0 | `n/a` | 0 | `df6bd9314a9fcfd8be2a68b3998dc91a917370cd221b83a3ea6b2243d1176de3` |
| consensus_available_two_agent | closest-available constrained consensus component | 450/450 | 0 | 0 | 0 | 0 | `n/a` | 0 | `b336273f1bfa499e5465f4509a3dc8f447c972794f3c79ac60ff221789e09736` |
| fresh_evidence_v06_safety_v09 | fresh-evidence component matching frozen test V12 role | 450/450 | 0 | 0 | 0 | 450 | `pass` | 450 | `e317b088bbcdc0a2f668b0e600bccaf17664a5d4ae2e734c0531684e786a1295` |

## Source Substrates

| Substrate | Role | Coverage | Duplicates | Off manifest | Calls failed | Parse/repair rows | Prompt hygiene | Prompt rows checked | SHA-256 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | ---: | --- |
| gpt_structured_events_v05 | GPT structured-event source substrate | 450/450 | 0 | 0 | 0 | 308 | `pass` | 450 | `0c9bd96a49cfd22e57f2f9c421dbc78bf0e3a0f16233a67e09c853c174c2b40c` |
| qwen_structured_events_patch | Qwen structured-event source substrate | 450/450 | 0 | 0 | 0 | 382 | `pass` | 450 | `61ac7d12c9580188c3f5c467a41d55d4962cf7f81052e5617dd19868ef997f59` |
| deepseek_structured_events_v06 | DeepSeek structured-event source substrate | 450/450 | 0 | 0 | 0 | 311 | `pass` | 450 | `d57dc30c7c859c47e072e9278df3f2be1e70c56a9e62acae0e16f43f5c0cddca` |

## Interpretation

Gate 3 passes only as constrained source-symmetry. The deterministic floor,
available consensus component, fresh-evidence component, and GPT/Qwen/
DeepSeek source substrates each cover the locked manifest exactly
`450/450` with `0` duplicate and `0` off-manifest source rows.

The exact validation consensus policy is not present as a three-agent
test replay artifact. The available consensus component is the older
two-agent constrained replay, while the DeepSeek test source artifact was
added later as source coverage for future frozen consensus/scaffolding
audits. Therefore any Gate 4 readout must be reported as constrained
holdout evidence, not as an exact v0.9 selector holdout claim.

This report does not authorize Gate 4. The next step requires explicit
user authorization for one frozen aggregate-only locked `test450` audit.
