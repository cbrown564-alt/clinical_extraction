# ExECTv2 Qwen Same-Core Repair v02 Dev140 Readout

- Readout date: `2026-06-25`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v02_dev140`
- Predeclaration: `docs/experiments/exectv2/reliability/exectv2_qwen_model_swap_repair_v02_predeclaration_2026-06-25.md`
- Frozen core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false_qwen_output_contract_repair_v02`
- Decision: **does not pass; Qwen remains diagnostic-only**

## Summary

Repair v02 addressed the two v01 blocking structured-output failures as
predeclared:

- `EA0007`-style out-of-enum clinical events are dropped rather than coerced.
- `EA0035`-style malformed non-scored `rationale` text can be blanked before
  JSON/schema validation.

The concrete v01 failure payloads both parse under the v02 parser in targeted
regression checks. On the live v02 structured rerun, the full `140/140`
structured producer completed with `0` call failures and `0` parse/schema
failures. However, exact evidence validity failed the predeclared `>=0.99`
gate, so the run was stopped before completing the downstream same-core
assembly.

## Completed Structured Producer Checkpoint

Artifact:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.jsonl`

Report:
`experiments/exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured_checkpoint.md`

| Checkpoint | Rows | Call failures | Blocking parse/schema failures | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| structured producer | 140 / 140 | 0 | 0 | 0.9637 |

Structured checkpoint counts:

- clinical events raw: `817`
- mentions raw: `827`
- mentions scored: `797`
- evidence-invalid dropped: `30`

The live v02 structured run did not reproduce the specific `diabetes` family or
malformed-rationale parse failures from v01; nonetheless, the v02 parser is
pinned by tests and by offline parsing of the saved v01 failed raw payloads.

## Gate Decision

| Gate | Predeclared threshold | Observed | Decision |
| --- | --- | --- | --- |
| Architecture parity | same frozen core | same config core and live components | pass |
| Operational stability | `0` call failures and `0` blocking parse/schema failures | structured producer `0` / `0` | pass on completed structured producer |
| Evidence validity | `>=0.99` exact evidence rate | structured checkpoint `0.9637` | fail |
| Clinical non-regression | overall `>=0.8018`, SF `>=0.6919` | not run to assembly after evidence failure | not evaluated |

Because evidence validity failed on the completed structured producer, Qwen is
not eligible for the next same-core full-200 operational candidate set. The
appropriate default candidate set remains GPT-4.1-mini plus DeepSeek. Qwen can
remain as a diagnostic same-core row or be revisited only under a fresh repair
predeclaration focused on evidence exactness, not parser/schema stability.

## Notes

The aborted downstream run produced an incomplete Diagnosis decomposer artifact
while the evidence gate was already failed; those incomplete Diagnosis files
were removed to avoid presenting partial rows as completed same-core evidence.

## Follow-Up Evidence Repair Check

After the initial v02 readout, the shared evidence gate was updated to apply
standard source-exact evidence repair before dropping a mention:

- case plus whitespace drift
- escaped tab/newline drift
- bounded `...` omission repair when it resolves to one exact source span
- section-header plus selected list-item repair when it resolves to one exact
  source section span

Replaying the saved v02 structured raw outputs through the updated gate reduces
the completed structured-producer evidence failures from `30` to `3`:

| Replay surface | Raw mentions | Evidence-invalid | Scored mentions | Evidence validity |
| --- | ---: | ---: | ---: | ---: |
| v02 structured raw replay with standard evidence repair | 827 | 3 | 824 | 0.9964 |

This confirms that part of the original evidence-validity failure was standard
copy-drift repair, not clinically meaningful unsupported evidence. The remaining
three failures are one source typo normalization case (`Sine`/`Since`) and two
EA0114 carbamazepine rows where Qwen appended a sentence not present in the
source. This replay crosses the evidence-validity threshold, but it is still a
post-hoc saved-raw replay rather than a fully predeclared completed same-core
assembly rerun.
