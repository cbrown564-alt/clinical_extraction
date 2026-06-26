# Gan 2026 Consensus/Fresh v0.9 Frozen Protocol

Date: 2026-06-26

Status: predeclared hard-slice, robustness, and locked-test protocol. This
document does not authorize a `test450` run by itself. It records what
`gan2026_consensus_fresh_agreement_selector_v0_9` must clear before its role can
move beyond `component_ladder`.

Addendum after the constrained Gate 4 audit: the completed constrained audit is
final-evaluation evidence only. It cannot be reinterpreted as an exact v0.9
selector holdout claim. An exact v0.9 selector holdout claim requires a new
exact-source Gate 3 preflight and a separately authorized aggregate-only Gate 4
audit over exact component roles.

Final exact-source addendum: the missing exact three-agent consensus test
component was generated and frozen on 2026-06-26, exact-source Gate 3 passed,
and a fresh user-authorized aggregate-only exact-source Gate 4 passed promotion
bars. The resulting claim is limited to an exact v0.9 selector holdout over the
frozen source set documented below; it still does not authorize post-test
tuning or locked-test row-level failure inspection.

## Objective

Decide whether the validation-only v0.9 consensus/fresh selector deserves a
holdout-facing upgrade from component-ladder evidence to a frozen selector
candidate.

The candidate is strong but not yet holdout-facing:

- Deterministic Purist: `697/750`
- Consensus Purist: `708/750`
- Fresh-evidence Purist: `682/750`
- Selected Purist: `733/750`
- Changed labels: `49`
- Wrong-to-correct: `36`
- Correct-to-wrong: `0`
- Changed-label precision: `0.7347`

The risk is not the aggregate. The risk is whether the selector changes labels
only on stable, transferable failure families. Existing validation bands show
weak changed-label precision in `band_submonthly` (`1/5`) and `band_weekly`
(`4/10`), and the residual audit shows that `11/17` remaining wrong rows lack a
Purist-correct component at all.

## Frozen Candidate

- Pipeline: `consensus_fresh_agreement_selector`
- Selector version: `gan2026_consensus_fresh_agreement_selector_v0_9`
- Selector policy: `semantic_equiv_unknown_uncertainty_v0_9`
- Code owner:
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py`
- Prediction-bearing behavior: keep the deterministic baseline unless a
  predeclared selector gate accepts an independently corroborated consensus or
  fresh-evidence replacement.
- Model calls: none for selector replay. Any upstream component-generation
  model calls must be frozen and reported separately before selector scoring.
- Split manifest: `gan2026_split_v1`
- Scorer: unchanged Gan-compatible Purist first; Pragmatic as sidecar.
- Primary comparator: deterministic baseline in the selector artifact.
- Claim boundary: hybrid selector over saved deterministic, consensus, and
  fresh-evidence components. This is not clean LLM-only evidence.

## Exact v0.9 Holdout Claim Boundary

The phrase "exact v0.9 selector holdout" is reserved for a locked `test450`
audit whose source components match the validation v0.9 replay roles exactly.
The constrained Gate 4 source set does not satisfy this boundary.

Before any exact v0.9 holdout claim is allowed:

- build and SHA-256 pin an exact three-agent test consensus component using the
  validation consensus policy: deterministic floor plus GPT, Qwen, and DeepSeek
  structured-event components under the exact validation consensus rule;
- explicitly audit deterministic-source identity so the selector's deterministic
  comparator, the consensus floor, and any fresh-evidence fallback/reference use
  the same deterministic role as validation v0.9;
- prove that the test fresh-evidence component matches the validation
  fresh-evidence role used by v0.9, or document it before audit as a frozen
  exact holdout counterpart with the prompt/safety-version difference named;
- rerun Gate 3 as `exact_source_symmetry`, requiring `450/450` coverage for the
  deterministic component, exact three-agent consensus component, and
  fresh-evidence component, with `0` duplicates and `0` off-manifest rows;
- hash-pin every source artifact and record prompt-hygiene checks showing no
  gold labels, row correctness, or deterministic-top labels were passed into
  upstream model prompts;
- keep the locked-test inspection boundary intact: no row-level failures,
  rationales, evidence, selected events, or transitions may be opened for
  development.

Only after this exact-source Gate 3 passes may the user authorize a fresh
aggregate-only Gate 4 for the exact v0.9 source set. The failed constrained Gate
4 must not be used to tune prompts, selector gates, component-generation
artifacts, deterministic rules, normalization, scorer behavior, or model choice.

Completed exact-source artifacts:

- `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26.jsonl`
- `experiments/gan2026_agentic_structured_event_consensus_unanimous_exact_test450_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_exact_source_symmetry_preflight_2026-06-26.json`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate3_exact_source_symmetry_preflight_2026-06-26.md`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.json`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_frozen_gate4_exact_aggregate_audit_2026-06-26.md`

Exact Gate 4 aggregate result:

- Deterministic Purist: `343/450`
- Consensus Purist: `366/450`
- Fresh-evidence Purist: `351/450`
- Selected Purist: `359/450`
- Selected Pragmatic: `368/450`
- Net Purist gain vs deterministic: `+16`
- Changed labels: `35`
- Wrong-to-correct: `21`
- Correct-to-wrong: `5`
- Changed-label precision: `0.6000`
- Gate result: pass

## Frozen Evidence

Primary validation artifact:

- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md`

Required companion diagnostics:

- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.json`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.json`
- `experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.json`

Repository HEAD when this protocol was written:

```text
7ba6e0419dadc4d52e62770e39db872684faba0c
```

The working tree was clean before this protocol and registry-role update.
Current SHA-256 pins:

```text
a20cb3dad61b96ccbae57c94c7a254c493873010c193e88660d6ad814e27647f  src/clinical_extraction/tasks/seizure_frequency/gan2026/agentic/consensus_fresh_agreement_selector.py
66256c6686ff6b4c657bcca1f1952146aa911a75b5fe5daee58e686bc1b8449e  experiments/build_gan2026_v09_semantic_equiv_unknown_replays.py
35f1962b2a302892bc42b3425c9b67be95d9c24c6cf09c94280e51968fcc0d6f  experiments/build_gan2026_v09_residual_component_generation_audit.py
6eb216d3a4c330a494c57930247b9e83fda139217c86798d3a79b0751548290a  experiments/build_gan2026_v10_component_repair_probe.py
1b1c3804722c3fe7e55bd2a80f396420eedc39fd97cda83ef5c88e2f4b717f28  experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.jsonl
e493c4f5bd68477757d922ca62c46bf37380698e26fea7d47651c3031a25193f  experiments/gan2026_consensus_fresh_agreement_selector_v0_9_validation750_no_call_replay_2026-06-15.md
6bbb33b4cbd23ad907551faff891a05c6ad16fd0af214a4625acae27b21c402f  experiments/gan2026_consensus_fresh_agreement_selector_v0_9_semantic_equiv_unknown_synthetic_stress_2026-06-15.json
3e5680447988781725079231fe299c9317189474f9ce25f38489610d3adbb4c4  experiments/gan2026_consensus_fresh_agreement_selector_v0_9_residual_component_generation_audit_2026-06-15.json
7f8b1cd36c20e7c894285c9346d6f0ee13f3db91b21da1635ae78761d0bd7684  experiments/gan2026_consensus_fresh_agreement_selector_v0_10_component_repair_probe_2026-06-15.json
5dd39c552bcb60a40f0c79245a9f7346fd27a064cd27263c902e879af3bf7c57  data/Gan (2026)/splits/gan2026_split_v1.json
```

## Gate 1: Validation Hard-Slice Audit

Purpose: confirm that the validation gain is not hiding brittle selector
behavior in known weak families.

Surface: validation only. Use the frozen v0.9 selector JSONL and the frozen
residual audit. Do not read locked test rows.

Predeclared slices:

1. All `49` changed-label rows.
2. Boundary-band changed rows:
   `band_zero`, `band_unknown`, `band_submonthly`, `band_monthly`,
   `band_weekly`, and `band_daily`.
3. All `17` selected-wrong residual rows.
4. Residual rows with a correct unselected component (`6` rows).
5. Residual rows with no correct component available (`11` rows).
6. Residual taxonomy families:
   `unknown_over_quantified_rate`,
   `last_event_or_seizure_free_overinfer_unknown`,
   `cluster_burden_component_failure`,
   `highest_semiology_or_denominator_conflict`,
   `fresh_only_correct_candidate`,
   and `consensus_fresh_correct_but_blocked`.

Required readout:

- selected Purist and Pragmatic counts;
- wrong-to-correct, correct-to-wrong, wrong-to-wrong, and correct-to-correct;
- changed-label precision overall and by slice;
- selector action distribution by slice;
- exact evidence/source-validity diagnostics when present in source components;
- explicit count of rows where no current component can produce the gold label.

Promotion gate:

- overall selected Purist remains at least `733/750`;
- overall correct-to-wrong remains `0`;
- every predeclared slice has non-negative net Purist change;
- no slice has correct-to-wrong > `0`;
- changed-label precision is at least `0.70` overall;
- low-precision bands must be named as portability risks, not treated as
  solved families;
- residual rows with no correct component are excluded from selector-superiority
  claims and assigned to component-generation follow-up.

Failing any item blocks a holdout-facing selector claim. It may still preserve
the row as component-ladder evidence.

## Gate 2: Robustness And Stress Panels

Purpose: test the selector gates on source-near cases and adversarial component
states before spending holdout budget.

Surface: synthetic and source-near validation-only panels. These are mechanism
tests, not benchmark evidence.

Required panel families:

1. Normalized-equivalent agreement positives and negatives.
2. Unknown-uncertainty positives where both model components say `unknown`.
3. Unknown/no-reference churn negatives.
4. Last-event-only and seizure-free over-inference negatives.
5. Cluster-burden preservation, including fully specified cluster cadence plus
   events-per-cluster controls.
6. Multiple semiology and denominator/window conflict controls.
7. Non-equivalent consensus/fresh disagreement controls.
8. Parseable denominator/window refinement controls inherited from v0.8.

Each family must include at least one positive, one deterministic-correct
negative control, and one paraphrase or minimally perturbed variant when the
family naturally supports it.

Required readout:

- desired-action match rate;
- false-positive selector actions on deterministic-correct controls;
- selected wrong-to-correct and correct-to-wrong transitions;
- action distribution by panel family;
- cases where selector behavior depends on label spelling rather than normalized
  equivalence or semantic family.

Promotion gate:

- desired-action match >= `0.90` overall and no below-`0.80` family;
- correct-to-wrong = `0`;
- deterministic-correct negative-control false positives = `0`;
- no cluster-burden demotion;
- no no-reference-to-unknown churn unless the component profile explicitly
  states unquantified seizure-frequency evidence.

Failing this gate sends the selector back to validation-only design. Do not
proceed to test.

## Gate 3: Test Source-Symmetry Preflight

Purpose: ensure the locked-test audit uses the same component roles as the
validation v0.9 selector.

The exact v0.9 test phase is blocked until this inventory is complete and
hash-pinned:

- deterministic test component with locked `test450` coverage;
- exact three-agent consensus component matching the validation consensus
  policy: deterministic floor plus GPT, Qwen, and DeepSeek structured-event
  components under the validation consensus rule;
- deterministic-source audit proving the selector comparator, consensus floor,
  and fresh-evidence fallback/reference use the same deterministic role as the
  validation v0.9 replay;
- fresh-evidence component matching the validation fresh-evidence role, or a
  pre-audit frozen exact holdout counterpart with any prompt/safety-version
  difference named;
- source-row coverage exactly `450/450` for each component;
- no duplicate or off-manifest source rows;
- SHA-256 pins for every source artifact;
- no gold labels, row correctness, or deterministic-top labels passed into any
  model prompt for upstream component generation;
- no row-level test failures, rationales, evidence, selected events, or
  transitions opened for development.

Resolved caveat: the completed constrained Gate 3 documented only the older
available two-agent consensus artifact, even though DeepSeek `test450`
structured-event source coverage existed. The exact-source follow-up generated
and froze the missing GPT+Qwen+DeepSeek unanimous consensus replay. The
exact-source Gate 3 report also documents that the deterministic floor is
aligned to the validation rules-tool baseline role, not the constrained Gate 4
canonical-pipeline comparator.

## Gate 4: Locked Test450 Aggregate Audit

Run this only after Gate 1, Gate 2, and the relevant Gate 3 source preflight
pass and the user explicitly authorizes the frozen aggregate-only holdout audit.
An exact v0.9 Gate 4 requires a fresh authorization after exact-source Gate 3
passes. The completed constrained Gate 4 authorization does not carry over.

Permitted first readout:

- aggregate selected Purist and Pragmatic counts/rates;
- deterministic comparator Purist and Pragmatic counts/rates;
- wrong-to-correct, correct-to-wrong, and changed-label count;
- changed-label precision;
- selector action counts;
- component source coverage and parse/schema/call failures;
- predeclared slice aggregates only if slice membership was fixed without
  reading test labels or row-level failures.

Forbidden before starting a new validation-only development cycle:

- test row-level failure inspection;
- opening test rationales, selected evidence, selected events, or row-level
  transitions for development;
- changing selector gates, component-generation prompts, source artifacts,
  deterministic rules, normalization, scorer, or model choice from the test
  result;
- rerunning a tuned `test450` variant based on this result.

Promotion gate:

- selected Purist improves over the deterministic comparator by at least `+10`
  rows;
- correct-to-wrong <= `5`;
- changed-label precision >= `0.60`;
- selected Purist is at least the prior closest consensus/fresh aggregate anchor
  when source symmetry is exact; if source symmetry is constrained, report only
  as constrained holdout evidence;
- no source-coverage, parse/schema, or artifact-integrity failure changes the
  interpretation.

If the aggregate test fails, record the result as final-evaluation evidence and
return to validation-only component-generation work. If it passes, upgrade the
selector to a holdout-backed selector candidate with conservative claim language;
do not relabel it as a clean architecture comparator unless the source-symmetry
preflight proves exact role parity.

Claim language is limited as follows:

- `exact v0.9 selector holdout` is allowed for the completed 2026-06-26
  exact-source Gate 4 result because exact-source Gate 3 passed and the fresh
  aggregate-only exact-source Gate 4 cleared the promotion bars;
- `constrained holdout evidence` is the strongest allowed language when the
  source set uses the older available two-agent consensus artifact or any other
  documented non-parity component;
- failed constrained Gate 4 evidence remains final-evaluation evidence and may
  not be used as a tuning signal for a later exact-source run.

## Technical-Failure Policy

If a hard-slice or robustness script fails before producing a result, rerun the
same frozen command or regenerate the report from the same frozen inputs. If a
test audit fails operationally, inspect only completion counts and technical
metadata needed for recovery.

Do not use locked-test row content to debug the selector, source components, or
scorer. Any substantive fix starts a new validation-only candidate.

## Registry And Reporting

After each completed gate:

- write a dated report under `experiments/` or `docs/experiments/gan2026/`;
- update `experiments/registry.jsonl` and regenerate `experiments/RUN_INDEX.md`
  only for durable claim-of-record artifacts;
- preserve `registry_roles=["component_ladder"]` until a frozen holdout result
  clears the promotion gate;
- add `holdout_anchor` only to a completed locked-test aggregate artifact;
- keep reliability and component-impact language separate from accuracy
  candidate language.
