# Gan 2026 Label-Binding v0.7 — Predeclaration

Date: 2026-06-15

Cycle 3 of the F1 dynamic workflow
(`docs/research/gan2026_f1_dynamic_workflow_protocol_2026-06-15.md`). Predeclared
**before any run**, per the predeclaration hard gate. This file states the exact
consistency repair, the per-panel expected effect (direction + rough magnitude),
the regression risk, and the stop rule. Nothing here is revised after the run.

## Cycle-2 diagnosis (the basis for this cycle)

The v0.6 triage scaffold makes the model FORM the correct finding, but the
emitted `final_label` contradicts that finding. Inspecting the actual emitted
decision records on the five v0.6 battery residuals (verbatim from the Cycle-2
checkpoints):

| Case | `answer_kind` | `final_label` (v0.6) | Rationale (model's own words) | Gold Purist |
| --- | --- | --- | --- | --- |
| A2a | `unknown` | `3 per 6 week` | "...circadian disruption... no habitual rate is established and the label is unknown." | `seizure_freq_unknown` |
| A6a | `unknown` | `2 per 6 week` | "...medication supply interruption, so the count does not establish a habitual baseline and the label is unknown." | `seizure_freq_unknown` |
| A4a | `frequency` | `multiple per day` | "...stable cluster pattern recurring every 4 to 5 weeks with multiple seizures per cluster..." | `seizure_freq_more1mon_less1week` |
| B6 | `frequency` | `1 per 4 to 5 week` | "...recurrent clusters of seizures every four to five weeks with multiple events per cluster..." | `seizure_freq_more1mon_less1week` |
| B3 | `seizure_free` | `seizure free for multiple year` | "...continuous seizure-free interval for many months except for a single one-off event..." | `seizure_freq_unknown` |

So on 4 of 5 residuals (A2a, A6a, A4a, B6) the model's emitted
`answer_kind`/rationale is CORRECT and the `final_label` simply does not bind to
it. B3 is the lone genuine mis-reasoning (a single past event read as a
continuous seizure-free interval).

## The change (v0.7, additive; v0.5/v0.6 intact)

Add a new prompt version `gan2026_llm_only_direct_labeler_v0.7` and, gated on
that version only, a **label-binding repair** in the labeler's
decision-parsing/label-rendering layer (`parse_decision_json`), applied to the
parsed decision record *before* the existing evidence-format repair. The repair
keys ONLY on the model's own emitted structured fields (`answer_kind`,
`rationale`, `time_window`, `evidence`). It NEVER reads gold, row index, or any
saved-row behaviour. The emitted JSON schema, scoring, and gold normalization are
untouched. v0.5 stays the module default; v0.6 stays byte-for-byte unchanged
(the repair is a no-op for any version != v0.7).

Three binding rules:

1. **Coerce-to-unknown.** When the model's emitted `answer_kind` is `unknown`,
   `no_reference`, or `unresolved_multiple`, the answer it formed is "no usable
   rate". Coerce `final_label` to match: `unknown` for `unknown` /
   `unresolved_multiple`, `no seizure frequency reference` for `no_reference`.
   (If `final_label` is already that, the rule is a no-op.) This binds the label
   to the model's own verdict and is keyed purely on the emitted
   `answer_kind` enum. Targets A2a, A6a.

2. **Cluster-cadence render.** When `answer_kind == "frequency"` AND the model's
   own `rationale` (or `evidence`) describes a **cluster cadence** — an explicit
   cluster/run/grouping token (`cluster`, `clusters`, `run`/`runs`,
   `grouping(s)`, `group together`, `arriving in runs`) co-occurring with a
   recurrence-interval cue (`recur`, `recurring`, `every`, `come round`,
   `coming round`, `arriving ... every`) — AND `final_label` is NOT already a
   cluster form, re-render `final_label` to
   `1 cluster per <window>, multiple per cluster`, where `<window>` is the
   recurrence interval parsed from the emitted `time_window` (falling back to the
   `rationale`/`evidence` text), with word-numbers converted to digits and a
   `lo to hi` range preserved (e.g. "every 4 to 5 weeks" -> `4 to 5 week`). If no
   numeric window can be parsed, the label is left unchanged (no fabrication).
   Negation guard: the rule does NOT fire when the cluster token is explicitly
   negated in the same finding (`no grouping`, `no cluster`, `not clustered`,
   `no clustering`, `without grouping`). Targets A4a, B6; must NOT touch A4b
   ("single isolated seizure ... no grouping or clustering").

3. **Seizure-free-vs-one-off scaffold sharpening (B3).** Sharpen the v0.7 STEP-4
   wording so a single past event with NO asserted ongoing seizure-free interval
   is `unknown`, not a seizure-free duration: an isolated recent/past event
   ("one short blank spell a fortnight back", "the first thing of its kind for
   months", "last event N months ago") describes a last-event-only history, not
   a witnessed continuous seizure-free period — `unknown`. A seizure-free label
   requires the note to ASSERT an ongoing interval free of ALL events, not the
   absence of prior events before a one-off. This is a prompt change (the model
   currently emits `answer_kind=seizure_free` for B3, so a parse-layer coercion
   keyed on `answer_kind` would not catch it — the finding itself must change).
   Targets B3.

## The clinical principle (neurologist-endorsable, distribution-independent)

> A clinician's structured conclusion and the reported frequency label must
> agree. If the assessment is that no usable habitual rate exists (provoked,
> transient, adherence-confounded, last-event-only), the recorded frequency is
> `unknown`, not a number that happens to appear in the note. A cluster pattern is
> recorded with its cluster axis (clusters per window + events per cluster), never
> flattened to a daily burst rate nor to a single-event interval. A single past
> event with no asserted ongoing seizure-free interval is not a seizure-free
> duration — it is `unknown`.

This is core clinical reasoning that transfers identically to real KCL letters;
it is keyed on the model's own structured reasoning, NOT on saved validation
rows.

## Why this is principled, not validation-mining

The repair reads only fields the model genuinely emits for any input
(`answer_kind`, `rationale`, `time_window`, `evidence`). It would behave
identically on a never-seen KCL letter: a letter whose model verdict is `unknown`
gets an `unknown` label; a letter whose model reasoning names a recurring cluster
gets the cluster label. No branch consults gold, the source row index, or which
case moved. It enforces internal consistency of the model's own output — the
definition of a non-overfit, transfer-safe repair.

## Expected effect per panel (direction + rough magnitude)

Baseline (v0.6, Cycle-2 battery): A 3/6 both-correct + 2 overfit-only; B 5/7; C 8/8 (100%).

- **Panel A (minimal pairs).**
  - A2 (transient): A2a `3 per 6 week` -> `unknown` via rule 1 (emitted
    `answer_kind=unknown`). A2b stays a rate (`answer_kind=frequency`). Pair ->
    both-correct. High confidence.
  - A6 (adherence): A6a `2 per 6 week` -> `unknown` via rule 1 (emitted
    `answer_kind=unknown`). A6b stays. Pair -> both-correct. High confidence.
  - A4 (cluster): A4a `multiple per day` -> `1 cluster per 4 to 5 week, multiple
    per cluster` via rule 2 (rationale names cluster recurring every 4-5 weeks).
    Lands `seizure_freq_more1mon_less1week` = gold. A4b ("single isolated ... no
    grouping or clustering") must NOT trigger (negation guard) and stay
    `1 per 4 to 5 week`. Pair -> both-correct. Moderate-high confidence (rule 2
    is the more complex repair; negation guard is the risk).
  - A1, A3, A5 already both-correct in v0.6; rules 1/2 are no-ops for them
    (A1b/A3b/A5a are `frequency`/`seizure_free` with consistent labels; A1a/A3a/
    A5b already unknown/no_reference).
  - **Expected:** 6/6 pairs both-correct, zero overfit-only. Bar = every pair
    both-correct AND zero overfit-only.
- **Panel B (source-near).**
  - B6 (cluster): `1 per 4 to 5 week` -> `1 cluster per 4 to 5 week, multiple per
    cluster` via rule 2 (rationale names runs coming round every 4-5 weeks).
    Lands gold band. Moderate-high confidence.
  - B3 (last-event-only): fixed by rule 3 (scaffold sharpening) — the model
    should now emit `answer_kind=unknown` + `final_label=unknown`. This is the
    least certain fix: it depends on the model re-forming the finding, not on a
    deterministic coercion. Moderate confidence.
  - B1/B2/B4/B5/B7 already correct (unknown/no_reference, consistent).
  - **Expected:** 7/7 (target), bar >= 6/7 trigger-independent. If B3 does not
    re-form but B6 binds, B is 6/7 = still a pass.
- **Panel C (KCL OOD).** All 8 already correct at v0.6. The repair must not
  regress any: C4/C5 are `answer_kind=frequency` with clean rates (rules 1/2
  no-op — no cluster cues), C3 `seizure_free` with an asserted 6-month interval
  (rule 3 sharpening must not demote an ASSERTED interval), C6 already emits the
  cluster form (rule 2 no-op since already a cluster form), C1/C2/C7/C8 unknown
  (consistent). **Expected:** maintain 8/8; must stay >= 80%.

## Regression risk (the thing that would make this fail honestly)

- **Rule 1 over-demotion.** If the model emits `answer_kind=unknown` on a row
  whose true answer is a genuine rate, rule 1 forces `unknown` and the row is
  lost. On the battery this never happens (every `answer_kind=unknown` row already
  had `final_label=unknown`; the only two with a concrete label, A2a/A6a, are
  true unknowns). On validation750 this is the primary regression to quantify: count
  rows that flip correct->wrong because the model's emitted `answer_kind=unknown`
  on a genuine-rate gold row.
- **Rule 2 mis-fire.** The negation guard could fail to catch an unusual phrasing
  of "not clustered", or the cluster cue could trigger on incidental prose ("a run
  of bad days"). A4b is the in-battery guard. On validation750, quantify any
  genuine non-cluster rate that gets rewritten to a cluster form.
- **Rule 3 (scaffold) over-withholding.** Sharper seizure-free wording could push a
  genuinely-asserted seizure-free interval (C3, and any validation seizure-free
  gold) to `unknown`. C3 is the in-battery anchor; on validation750 quantify any
  `currently_no_seizure` gold row that flips to unknown.

The honest stop signal: if rules 1/3 trade the two cluster fixes for new
genuine-rate or seizure-free regressions on the battery's positive anchors, Panel
A or C drops and the candidate fails its own bar.

## Stop rule

- **Gate to proceed to validation750:** the battery must clear **Panel A** (every
  pair both-correct AND zero overfit-only) **AND Panel B** (>= 6/7,
  trigger-independent) **AND keep Panel C >= 80%**. Only then run the authorised
  validation750 live pass + held-out-family CV.
- **If any bar fails:** STOP. Do **not** run validation750. Report the residual
  failing-case ids verbatim with each failure's emitted `answer_kind` vs
  `final_label`, and the most likely next change. A battery pass is **necessary,
  not sufficient**, and is not a holdout result.
- No post-hoc bar lowering, no re-running to pick a better seed, no editing the
  repair after seeing which case moved.

## Registration

Battery run registered `mode=live`, `split=validation`, `evidence_validity` =
authored-OOD (NOT Gan rows, NOT holdout, NOT test450), `decision` = promote only
on `transfers`, else `revise`. If the gate clears, the validation750 run is
registered `mode=live`, `split=validation`, `decision` per the family-CV verdict.
test450 is never read or run here.
