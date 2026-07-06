# Audit — did our evolved GEPA seeds land on a policy-wall? (item 7)

Date: 2026-07-06. Owner: ExECTv2 + Gan2026 workstreams.
Status: **Complete.** Zero LLM calls.
Provenance: item 7 of `docs/plans/predecessor_synthesis_followups_2026-07-06.md`.
Driver: `scripts/run_gepa_policy_wall_audit.py` → `experiments/gepa_policy_wall_audit_2026-07-06.json`.

## TL;DR

**Yes — two evolved GEPA seeds clear the dspy policy-wall threshold, and both
exhibit the overfit-cue signature.** This is a real finding, but its scope is
**narrower than the plan implies**: the evolved seeds are research-workstream
artifacts (the GEPA plateau surface), **not** the production v08 hybrid path.
The plateau they explain is the ~0.73 dev140 GEPA surface, not the 0.9189
hybrid headline. Item 2's "fundamental gap" test runs on the hybrid surface, so
it does **not** inherit this policy-wall doubt directly — but the audit still
usefully reframes the GEPA close-out as a *diagnosed* negative (overfitting),
not a *capacity* negative.

## The threshold and the measurement

dspy **rejected G30 GEPA** specifically because its accepted instruction
ballooned to **14,639 characters** and was gated behind compact-delta /
latency / no-overlap criteria. We measure every `experiments/*.instruction.txt`
evolved seed (32 files) against that threshold. Token counts use
`tiktoken cl100k_base` (GPT-4 family); we also report the repo's own
`approx_tokens` (~4 chars/token, what `final_instruction_tokens` reports) for
consistency with the GEPA runner's internal metric.

### Over-threshold (2 of 32)

| Seed | chars | tiktoken | approx | policy-clauses |
| --- | ---: | ---: | ---: | ---: |
| `exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701.instruction.txt` | **18,638** | 4,522 | 4,660 | **125** |
| `exectv2_gepa_multistage_dedup_gpt41mini_20260628.instruction.txt` | **16,119** | 3,980 | 4,030 | **101** |

Both are **multistage combined 8-block** artifacts (generate + verify stages
evolved together). The next tier (9–9.5k chars) is in the same order of
magnitude as the wall but under it. The remaining 30 seeds range 1.0k–9.5k.

### Un-evolved baselines (the comparison point)

| Baseline seed | chars | tiktoken | approx | policy-clauses |
| --- | ---: | ---: | ---: | ---: |
| EXECTv2 `FROM_SCRATCH_SEED_INSTRUCTION` | 483 | 92 | 121 | 1 |
| SF_VERIFY `GENERATE_SEED` | 907 | 184 | 227 | 3 |
| SF_VERIFY `VERIFY_SEED` | 693 | 140 | 174 | 3 |
| GAN2026 `FROM_SCRATCH_SEED_INSTRUCTION` | 419 | 81 | 105 | 1 |

GEPA grew the verify-stage seed **from ~0.7k chars / 3 clauses → 18.6k chars /
125 clauses** — a ~25× length blow-up and a ~40× clause-density blow-up. That is
the policy-wall signature in its purest form: the optimizer packed dev-set
specific guidance into the instruction because that reduces training loss, at
the cost of generality.

## Overfit-cue diagnosis (the dissertation-experiments lens)

dissertation-experiments independently found that **targeted mapping examples
beat generic example policies** — the productive lever is example-richness that
generalizes, not policy-clause length that overfits. We read both over-threshold
seeds for dev-set-specific cues:

- **verify-stage (18,638):** embeds concrete drug+dose worked examples directly
  in the instruction — `"Levetiracetam 750mg"`, `"Lamotrigine 75mg"`,
  `"Zonisamide 50mg"` — under `**Examples of correct decisions (from
  feedback):**` and `**Examples of correct behavior (from prior cases)**`
  blocks. These are training-set-specific surfaces, not generalizable rules.
- **multistage (16,119):** same shape — `"Carbamazepine 400mg"`,
  `"Valproate 500mg"`, `"Lamotrigine 25mg"` as worked examples.

This is the overfit shape: the instruction grows by *memorizing* the dev set's
specific drug/dose surface rather than learning a generalizable extraction
policy. 125 policy clauses on the verify-stage seed vs 3 on its un-evolved
baseline is not "the optimizer found better rules" — it is "the optimizer found
that restating dev cues verbatim reduces training loss." **The largest evolved
instruction is also the one the root-cause doc singled out as having "drifted
into reformatting, not verifying"** (see below) — a direct policy-wall
signature: the instruction grew until it stopped doing the intended task and
started pattern-matching surface form.

## Cross-check against the existing root-cause doc

`docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md`
attributes the single-model GEPA plateau (~0.73 dev140, ~0.18 below the v08
hybrid 0.9189) to **producer evidence-recall**, not verify/arbitrate stages.
This audit **complicates but does not refute** that attribution, with two
caveats the plan did not flag:

1. **The policy-wall is on the *verify* stage, which the root-cause doc
   exonerated.** The largest policy-walled seed (18,638 chars) is the
   *verifystage* run, and it contains exactly the "drifted into reformatting,
   not verifying" behavior the root-cause doc flagged for that run. So the
   verify stage is *not* blameless in the way the root-cause doc's headline
   implies — at least one of its evolved seeds overfit to surface form. The
   root-cause doc's "producer, not verify" attribution may hold *on average*,
   but the policy-wall evidence shows the verify stage contributed its own
   overfit failure mode on at least one run.

2. **The root-cause doc's producer-recall verdict is itself partially
   retracted** for two of four families: SF (re-attributed to CUI-granularity
   lottery + gold multiplicity, `exectv2_sf_representation_not_recall_2026-06-28.md`)
   and Dx (85.2% gold-annotation-multiplicity artifacts, `exectv2_dx_canonical_row_analysis_2026-06-30.md`).
   So the cross-check's spine — "if policy-wall AND producer-recall, the
   diagnoses are consistent" — is weaker than the plan assumes, because the
   producer-recall side is contested for SF/Dx.

**Net cross-check:** the policy-wall finding and the producer-recall finding are
*consistent* (both point to overfit/surface-form failure rather than a genuine
capacity ceiling), but they are not the *same* diagnosis, and the producer-
recall half is partially retracted. The honest summary: the GEPA plateau is
**over-determined by overfitting mechanisms** (policy-wall on verify, surface-
form on producer, CUI-lottery on SF, gold-multiplicity on Dx) — none of which is
a fundamental capacity limit. That is a stronger negative-result framing than
"plateaued on recall."

## Scope correction (important for items 2 and 3)

**The evolved seeds do not feed the v08 production hybrid.** Confirmed by
exhaustive grep: nothing under `src/.../exectv2/assembly/` or `src/.../exectv2/llm/`
imports from `...gepa.program*` or reads any `*.instruction.txt`. The v08 hybrid
(`assembly/pipeline.py`) uses hand-curated rules/lenses; the GEPA programs are
research-only. Therefore:

- The policy-wall **does not** contaminate the 0.9189 headline or any cited
  hybrid number. Those numbers are policy-wall-free by construction.
- The policy-wall **does** reframe the GEPA close-out: the ~0.18 gap to hybrid
  is *partly* an overfitting artifact (at least ~2pp attributable to the verify-
  stage wall), not purely a capacity gap.
- **Item 2's "fundamental gap" framing inherits this doubt only on the GEPA
  research path, not the hybrid path item 2 actually tests.** Item 2 tests the
  SF-direction capacity-vs-execution gap on the same raw SF-verify surface that
  the B1/B2 probes used (the *un-evolved* verify program, not the policy-walled
  evolved seed). So item 2 is testing the gap on a surface that is *not* policy-
  walled. This *narrows* the doubt usefully: even if GEPA's plateau is policy-
  wall-shaped, the four measured SF-direction negatives (B2 −0.0775 etc.) were
  measured on the un-walled raw program, so they are not artifacts of the wall.

## Implications for items 2 and 3

The item-2 predeclaration should note:
1. The GEPA plateau is partly a policy-wall artifact (this audit), but item 2
   does **not** run on the policy-walled surface — it runs on the raw SF-verify
   program whose four measured negatives motivate the experiment.
2. The cross-family test (closed-option vs free-write) is therefore a clean test
   of the *generation contract*, uncontaminated by the GEPA overfit confound.
3. The "fundamental gap" claim, if item 2 confirms it, applies to the raw
   extraction surface, and the policy-wall finding does not weaken that claim —
   if anything it strengthens the contrast (GEPA overfit *despite* a wall;
   item 2 tests whether a *different* contract escapes the gap without a wall).

## Cost

Zero LLM calls. Static analysis of 32 evolved seed files + 4 un-evolved baseline
constants. Tokenization via `tiktoken cl100k_base` (a transitive dep of
`dspy>=2.5.0`; not pinned in `pyproject.toml` — noted in the deliverable's
methodology, but it is the standard GPT-4 encoding and the measurement is
reproducible from the committed seed files).
