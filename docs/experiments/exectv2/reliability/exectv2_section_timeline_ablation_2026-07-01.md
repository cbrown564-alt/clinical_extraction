# ExECTv2 Section/Timeline Context Ablation (2026-07-01)

Status: dev140-only pilot ablation, aggregate scoring only. Answers the
supervisor-brief conformance audit's identified gap (no Section/Timeline
Agent) — see `docs/research/supervisor_brief_conformance_audit_2026-07-01.md`
and Phase C of `docs/plans/supervisor_brief_gap_closure_plan_2026-07-01.md`.

## Predeclared hypothesis

A deterministic, letter-wide section-segmentation + chronological-reference
pre-extraction pass, threaded as optional context into the SeizureFrequency
and Investigations LLM stages' prompts, improves those two families'
`clinical_headline` F1 over the frozen v08 dev140 baseline — the two
single-LLM-stage families where sample letters (EA0001/EA0030/EA0075, see
the audit doc) showed genuine multi-date retrospective content ("EEG 1992",
"MRI 1993", "diagnosed... at 18") a timeline could plausibly disambiguate.
Diagnosis and Prescription were out of scope for this pilot (see the plan
doc's scope-decision section).

## Method

- New module: `exectv2/deterministic/section_timeline.py` (pure Python,
  zero LLM cost) — `segment_letter()` splits a letter into labeled sections
  (Diagnosis/Medication/SeizureFrequency/Investigations/Plan/Narrative);
  `build_timeline()` scans the whole letter for absolute dates (DMY,
  Month+Year, investigation-labelled bare years) and relative anchors
  (since-last-clinic, N-units-ago, at-age-N, at-time-of-diagnosis,
  last-year); `render_context_block()` renders a length-bounded (≤600 char,
  ≤8 events) text block. 12 unit tests in
  `tests/test_exectv2_section_timeline.py`, all passing.
- Threaded as an **optional, default-`None`** `timeline_context` parameter
  into `llm_sf_state_adjudicator.py::build_prompt_input`/`run_split` and
  `entity_verifier/prompt.py::build_prompt_input` (+ `config.py`,
  `runner.py`, and the `llm_investigations_verifier.py` facade) — verified
  byte-identical prompt payloads when unset, so no existing frozen artifact
  is affected by this change.
- **Baseline ("without timeline")**: reused the frozen v08 dev140 lane
  files directly, zero new calls —
  `experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl`
  and
  `experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.jsonl`.
- **With-timeline arm**: re-ran the raw SF adjudicator and Investigations
  verifier stages live (`openai/gpt-4.1-mini`, dev140, same
  `draft_mentions` per letter as the frozen baseline — reconstruction
  verified byte-faithful before any live call), each with
  `timeline_context` set for 133/140 letters (7 letters had no extractable
  section/timeline signal). Zero call failures, zero parse errors across
  all 280 calls. Then replayed the same deterministic downstream chain the
  baseline went through (SF: `sf_state_projection` →
  `sf_unknown_suppression` → `llm_sf_union_arbitration`; Investigations:
  `llm_investigations_arbitration`).
- **Scoring**: both arms scored through the same
  `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml`
  manifest via `build_finding_assembly()`, overriding only the
  `sf_union_arbitration_v08` and `investigations_arbitration_v02` producer
  artifact paths (Diagnosis/Prescription producers untouched). The scoring
  path was verified before any live call by reproducing the known frozen
  v08 dev140 numbers exactly (SeizureFrequency 0.9053, Investigations
  0.9132) from the untouched baseline manifest.
- Driver: `experiments/exectv2_section_timeline_ablation.py`
  (`--stage smoke` for the zero-cost verification above, `--stage live
  --confirm-live-spend` for the live run).

## Result

| Family | Baseline (without timeline) | With timeline | Delta |
| --- | ---: | ---: | ---: |
| SeizureFrequency | 0.9053 | 0.8947 | -0.0106 |
| Investigations | 0.9132 | 0.9098 | -0.0034 |

**Null result — hypothesis not supported.** Both families moved slightly
negative, not positive. The SeizureFrequency delta (-0.0106) is smaller
than this project's own established measurement noise floor for that
metric family (a faithful re-run of the same SF program previously moved
the `state_profile` metric by ±0.03 across identical runs — see
`docs/experiments/exectv2/seizure_frequency/exectv2_sf_canonical_metric_row_analysis_2026-06-29.md`);
`clinical_headline` is a different metric than `state_profile`, so this is
not a direct citation of the same noise band, but it is the closest
available reference point and the delta sits comfortably inside it. The
Investigations delta (-0.0034) is smaller still. **Neither delta should be
read as a reliable negative effect** — the honest reading is "no detected
improvement, and the small negative movement is consistent with run-to-run
noise on a 140-row dev split," not "the timeline context actively hurts."

A plausible (untested) mechanism: the raw letter text was already present
in both prompts, so the timeline block is a restatement of information the
model could already see rather than new information — any effect would
have to come from re-framing/emphasis, not fact discovery, which is a much
weaker channel to move F1 through. This pilot did not do row-level
adjudication to confirm or refute that mechanism; that would be the natural
next step if this direction is pursued further, which it isn't required to
be — see Conclusion.

## Conclusion

This directly answers the supervisor brief's Section/Timeline Agent role
with real evidence rather than an assumption either way: a minimal,
deterministic, letter-wide timeline pre-extraction stage does not
measurably improve the two families most likely to benefit from it, on
this corpus, at this scale. Combined with the corpus finding that ExECTv2
letters are single-encounter snapshots (not multi-visit documents — see
the audit doc), this is consistent with temporal reasoning already being
adequately handled by the existing per-fact attribute extraction
(`PointInTime`, `TimeSince_or_TimeOfEvent`, `FrequencyChange`) for this
task, rather than needing a dedicated upstream stage. The module itself
(`section_timeline.py`) remains in the codebase, tested and available, in
case a future direction (e.g. a genuinely multi-encounter dataset) makes
the timeline distinction load-bearing again.

**Not pursued further**: Diagnosis/Prescription extension, row-level
mechanism adjudication, or a larger sample — the effect size does not
justify the additional cost, and the brief's role is now answered with
evidence either way.

## Artifacts

- `experiments/exectv2_section_timeline_ablation.py` (driver)
- `experiments/exectv2_section_timeline_ablation_dev140_sf_adjudicator_with_timeline.jsonl`
  (+ `.md` report)
- `experiments/exectv2_section_timeline_ablation_dev140_sf_projection_with_timeline.jsonl`
- `experiments/exectv2_section_timeline_ablation_dev140_sf_suppression_with_timeline.jsonl`
- `experiments/exectv2_section_timeline_ablation_dev140_sf_union_with_timeline.jsonl`
  (+ `.md` report)
- `experiments/exectv2_section_timeline_ablation_dev140_inv_verifier_with_timeline.jsonl`
  (+ `.md` report)
- `experiments/exectv2_section_timeline_ablation_dev140_inv_arbitration_with_timeline.jsonl`
  (+ `.md` report)
- `experiments/exectv2_section_timeline_ablation_dev140_result.json`
- `src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/deterministic/section_timeline.py`
- `tests/test_exectv2_section_timeline.py`

## Guardrails respected

dev140 only; frozen holdouts (`test59`/`test450`) untouched; frozen v08
baseline artifacts read, never modified; aggregate scoring only.
