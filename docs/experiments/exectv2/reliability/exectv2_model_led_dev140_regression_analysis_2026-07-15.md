# ExECTv2 model-led dev140 deterministic-regression analysis

Date: 2026-07-15  
Status: development mechanism answer complete; rule changes not implemented

## Answer

The decision-0040 architecture is correct, but its current Diagnosis and
Prescription post-model policies are not safe enough to promote unchanged.
Seizure Frequency projection and suppression are supported by the component-
local dev140 result, and Investigations remains a behavior-preserving adapter.

The next candidate should:

1. keep Seizure Frequency projection and suppression;
2. keep Prescription normalization and supported regimen splitting;
3. disable Prescription residual additions by default;
4. revise Prescription dropping so an explicitly current regimen is preserved
   even when the same evidence also describes a future taper or increase; and
5. revise Diagnosis residual recovery so a broader concept is not added when
   the model already supplied an evidence-backed specific concept, while also
   preserving specific model-owned phenotypes that the current drop policy
   removes.

These are candidate recommendations, not implemented rules. They require a new
predeclaration and frozen rerun.

Machine-readable evidence:
`experiments/exectv2_model_led_dev140_regression_analysis_20260715.json`.
Protocol:
[dev140 deterministic-regression protocol](exectv2_model_led_dev140_regression_analysis_protocol_2026-07-15.md).

## Protocol and boundary

- Dataset and split: ExECTv2 dev140, using the 140 identifiers in the repository
  split manifest.
- Row permission: the user permitted dev140 analysis on 2026-07-15.
- Test policy: test60 rows were not assembled, scored, serialized, inspected, or
  quoted. The full200 producer blobs were filtered by identifier into temporary
  dev-only files before assembly.
- Models: GPT-4.1-mini, the historical DeepSeek API run with incomplete runtime
  metadata, and Qwen 3.6 35B repair v02.
- Replay: saved outputs only; zero model calls.
- Gold, scorer, prompts, and rules: unchanged.
- Primary row comparison: equality of family-local `clinical_headline` keys
  before and after deterministic clinical changes.
- Secondary compatibility view: the entity-agnostic gold surface used by the
  preceding full200 architecture audit.

The secondary view was added after the analysis exposed a scoring dependency.
It reconciles the earlier aggregate regression counts; it does not replace the
predeclared component-local primary comparison.

This is inspected development evidence. It does not establish test60 transfer,
clinical validity, cross-model generalization, or a promoted final policy.

## Score ladder

The deterministic changes improve final assembled dev140 clinical-headline F1
for all three saved conditions. The row analysis below shows why the aggregate
gain is not enough for promotion.

| Model | Model-owned overall | Final overall | Diagnosis | SF | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| GPT-4.1-mini | 0.7798 | 0.8378 | 0.7702 → 0.8727 | 0.6519 → 0.7018 | 0.8558 → 0.8867 | 0.8583 → 0.8583 |
| Historical DeepSeek API run | 0.8229 | 0.8747 | 0.7906 → 0.8892 | 0.7228 → 0.7635 | 0.9040 → 0.9268 | 0.9091 → 0.9091 |
| Qwen 3.6 35B repair v02 | 0.7997 | 0.8565 | 0.7480 → 0.8653 | 0.6760 → 0.7193 | 0.9330 → 0.9481 | 0.8718 → 0.8718 |

## Changed-row result

There are 319 model/family rows whose family-local keys change. All 319 changed
rows have exact selected evidence.

| Family | Wrong → correct | Correct → wrong | Changed, still wrong |
| --- | ---: | ---: | ---: |
| Diagnosis | 81 | 18 | 82 |
| Seizure Frequency | 38 | 0 | 20 |
| Prescription | 41 | 23 | 16 |
| Investigations | 0 | 0 | 0 |
| **Total** | **160** | **41** | **118** |

The compatibility view has the same total of 41 correct-to-wrong rows but a
different composition: Diagnosis 16, Seizure Frequency 2, and Prescription 23.
Its two Seizure Frequency regressions are both EA0078 under GPT and DeepSeek.
The family-local view has no Seizure Frequency regression on that letter. The
compatibility scorer is crediting an entity-agnostic unknown key, so EA0078 is a
scoring-surface dependency rather than evidence that the SF rule damaged its
own family output.

## Mechanism evidence

Mechanism groups can overlap on one row. The counts below therefore describe
exposure to a mechanism, not mutually exclusive causal totals.

| Mechanism group | Wrong → correct | Correct → wrong | Interpretation |
| --- | ---: | ---: | --- |
| Diagnosis residual addition | 34 | 16 | Material rescue, but repeated broad-concept false additions make the current policy unsafe |
| Diagnosis drop | 52 | 3 | Usually helpful, but it removes an evidence-backed absence-seizure phenotype on EA0156 |
| Diagnosis attribute/concept rewrite | 3 | 3 | Too entangled with other actions for a separate safety claim |
| Diagnosis heading recovery | 0 | 0 | Three changed rows remain wrong; no demonstrated row-level rescue here |
| Prescription drop | 35 | 18 | Helpful overall, but often mistakes a current regimen followed by a future change for planned-only medication |
| Prescription normalization | 11 | 3 | The three harms overlap with drop or residual addition; uniquely attributable normalization has one gain and no harm |
| Prescription regimen split | 1 | 0 | Retain |
| Prescription residual addition | 4 | 6 | Net harmful at group level; the four uniquely attributable rows are all correct-to-wrong |

For uniquely attributable rows, Diagnosis residual addition has 15 local
wrong-to-correct and 13 correct-to-wrong changes. Prescription drop has 29 and
15. Those ratios confirm that aggregate improvement does not make either
current policy safe.

### Diagnosis

The repeated regression is semantic subsumption. On EA0008 the model-owned
output already matches the two gold concepts, including a specific focal
seizure type. Residual recovery adds the broader `focal seizures` concept and
turns all three model conditions wrong. The same pattern recurs on EA0016,
EA0067, EA0117, EA0137, and EA0178. EA0132 combines residual addition, rewrite,
and drop actions, so its first harmful owner remains unresolved.

EA0156 is a separate drop failure. DeepSeek and Qwen both supply the gold
`absence seizures` and `juvenile absence epilepsy` concepts; the deterministic
policy drops `absence seizures`. Exact evidence is present. The current drop
rule therefore needs a general model-preserving boundary, not an EA0156
exception.

Recommendation: revise, then rerun a frozen candidate. Add a semantic
subsumption guard for residual concepts and require an explicit supported noise
condition before dropping a specific evidence-backed model concept. Do not
remove all Diagnosis repair: it produces 81 family-local rescues.

### Seizure Frequency

Projection and suppression produce 38 family-local wrong-to-correct changes and
zero correct-to-wrong changes. The largest mechanism is
`state.drop_unlabelled_active_rate` with 20 rescues; last-event conversion adds
six, contextual/historical unknown suppression adds five, and seizure-free
precedence adds three. Twenty changed rows remain wrong, so the mechanism is
not sufficient, but it does not create a component-local regression on dev140.

Recommendation: retain the current model-led projection/suppression chain. Keep
the compatibility scorer caveat visible and do not reintroduce the prohibited
independent extractor union.

### Prescription

The harmful drop cases share a general current-versus-future boundary. Examples
include current lamotrigine or brivaracetam regimens followed by instructions
to taper, stop, or increase them (EA0008, EA0067, EA0116, EA0119, EA0120,
EA0154, and EA0186). The current regimen is gold and exactly evidenced, but the
rule removes it. EA0087 also loses current split lamotrigine doses while keeping
levetiracetam.

Residual addition is worse. Its four uniquely attributable changed rows are all
correct-to-wrong. It adds planned or contextually incomplete regimens on EA0074,
EA0148, EA0150, and EA0166; there is no uniquely attributable rescue. Across
overlapping rows it has four rescues and six regressions.

Recommendation: disable residual additions in the next candidate. Preserve an
explicit current regimen when future-change language follows it, and limit
dropping to planned-only evidence. Retain normalization and supported regimen
splitting.

### Investigations

Investigations has no prediction-changing row in any model condition.

Recommendation: retain the thin adapter.

## Decision

- Keep decision 0040 as the architecture owner.
- Do not promote the historical model rows or the current Diagnosis and
  Prescription correction policies.
- Treat the Seizure Frequency chain and Investigations adapter as retained
  components for the next candidate.
- Predeclare one bounded no-call candidate that disables Prescription residual
  addition and adds general model-preserving guards for Diagnosis subsumption
  and Prescription current-versus-future selection.
- If that candidate cannot reduce correct-to-wrong rows without losing the
  documented rescues, keep the negative result and use the model-owned output
  for the affected mechanism rather than adding row-specific rules.
