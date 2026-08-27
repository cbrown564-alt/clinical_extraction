# 0055: ExECT semantic inventory and method-specific representation contracts

Date: 2026-08-16  
Status: accepted; Fork A selected after the v2 `dev20` revise result
Updated: 2026-08-16 — mention-unit v2 `dev20` is an answer; `dev140` is a revise; extras and hybrid-encoder catalogs are answers ([encoder](../research/exectv2/mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md)); Decision 0050 unchanged
Related: [Decision 0040](0040-final-exect-llm-with-rules-family-ownership.md),
[Decision 0041](0041-single-call-exect-model-comparison.md),
[Decision 0027](0027-clinical-recovery-is-the-exectv2-headline-projection-is-an-artifact-layer.md)  
Implementation plan:
[ExECT LLM representation and hybrid re-evaluation](../plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md)

## Decision

ExECT model-led methods target the same clinical inventory: a set of atomic,
independently supported facts. The methods use different model-facing
representation contracts so that the comparison separates model-led semantic
structuring from deterministic clinical parsing.

`llm_only` asks the model to emit each fact with simple, family-specific
semantic attributes. `llm_with_rules` asks the model to emit the complete
event and exact evidence, while deterministic rules parse that event into the
semantic attributes and the legacy ExECT scorer representation.

Both methods use matched one-call lanes: the same rows, model, generation
settings, and control policy, with one independent call per method per row.
Neither method may substitute an independent deterministic extractor for model
recall.

## Clinical inventory contract

Each inventory item is one atomic clinical proposition with:

* `family`;
* a complete natural-language `event`;
* exact supporting `evidence`;
* family-specific clinical qualifiers, as applicable;
* assertion, temporality, subject, and scope; and
* quantities, units, intervals, durations, or change direction stated by the
  source.

Multiple facts may share one evidence span. Current and planned prescriptions,
current and historical seizure facts, and separate diagnosis concepts remain
separate items. ExECT does not require one fact to win over another.

The semantic schema uses a shared envelope and simple family-specific flat
attributes. Prefer names such as `name`, `dose`, `unit`, `schedule`, `purpose`,
`status`, `type`, `count`, `period`, `result`, and `certainty`. The scorer
adapter owns mappings to legacy fields such as `DrugName` and
`NumberOfSeizures`.

Zero-event intervals and cessation facts are explicit inventory items. A
planned medication change is separate from the current regimen when both are
stated. Multiple facts from one span may repeat the same exact evidence.

## Method boundaries

### `llm_only`

The model owns clinical fact capture and semantic attribute parsing. Its
payload may contain a family-specific flat `attributes` object. Deterministic
code may parse and validate the payload, repair transport/schema format,
validate evidence, flatten the inventory, and build a declared scorer adapter.

It may not recover missing facts, add diagnosis concepts, derive seizure states,
perform prescription recovery, or silently apply hybrid transforms.

### `llm_with_rules`

The model-facing schema contains only the event carrier and evidence:
`family`, `event`, and `evidence`, plus non-clinical metadata if needed.
Clinical attributes are forbidden in this payload so that deterministic parsing
remains the method’s explicit responsibility.

Rules may parse both `event` and its exact `evidence` for that emitted item.
They may normalize or derive an attribute directly supported by that item, but
may not search unrelated note text or create a new fact from a supported span.

If parsing fails, the raw event and evidence remain in the semantic trace and
only the affected projection fails. Every prediction-changing transformation
must retain before/after values, rule category, action, evidence, and first
owner.

Model-absent diagnosis parents, companions, residual concepts, and other
clinical fact recoveries are excluded from the default hybrid. Any proposed
recovery requires a separate rule family, ablation, and decision.

## Evaluation boundary

Semantic evaluation is gold-anchored where the annotations support the fact or
attribute. The existing `clinical_headline` scorer remains a declared
benchmark projection, not the sole definition of clinical success.

Reports must separate:

* raw event and evidence coverage;
* semantic fact and attribute retention;
* hybrid parse successes and failures;
* rule-derived, added, changed, removed, and dropped fields;
* benchmark projection changes; and
* facts supported by evidence but not represented in the annotation.

Unannotated supported facts are not automatic errors and must not be silently
promoted into new gold labels.

## Consequences

* The two methods do not share identical raw JSON, but they share the same
  clinical inventory objective and matched call boundary.
* The hybrid can improve machine comparability without receiving hidden model
  attributes or replacing model recall.
* A higher benchmark score is insufficient if the hybrid drops supported
  inventory facts or hides parser failures.
* Gan remains a precedent for semantic/scoring separation and attribution, not
  a source of ExECT-specific labels or single-answer selection behavior.
* The selected v0.9.24 / Decision 0050 result, ExECT gold, and sealed `test60`
  are unchanged. This decision does not authorize model calls.

## Amendment: Fork A (2026-08-16)

The v2 Luna `dev20` study showed that a natural-language clinical inventory
scored with `clinical_headline` is a different task from ExECT gold. The
selected continuation is **Fork A**:

* The decision metric remains four-family `clinical_headline` against ExECT
  gold. Empty-gold extras, current-scope violations, and uncoded
  phenomenology are false positives on that surface.
* A richer semantic trace may exist for diagnosis, but it is not the
  headline. Last-event remains the gold zero-count / generic encoding.
* `llm` must emit the coded attributes itself. `llm_with_rules` may derive
  them from emitted event and evidence.
* Decision 0040 stays in force: rules may rewrite, project, suppress, and
  apply bounded residual recovery. They may not replace model recall with an
  independent letter extractor.
* The v10 coding grammar belongs in named hybrid rules, not in a 59k prompt
  and not in a diary-style inventory objective.

This amendment does not promote a candidate or change Decision 0050.

The research-lane implementation of Fork A is
`exectv2_semantic_inventory_v4`. The live `dev20` run is a
**negative_result**:
[v4 result](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).
v3 remains the prior revise result.

## Amendment: mention-unit instruction job (2026-08-16)

v3 and v4 showed that Fork A’s scored object was right and the
model-facing item was wrong. Ordinary-language events are not ExECT
mentions. The research-lane contract asks both methods to copy mention
wording from the letter, with family-specific coding fields on `llm`
and rewrite-only rules on `llm_with_rules`. Hybrid may read that
item’s text and evidence. It may not parse a sentence into a new
mention set or search the letter.

Mention-unit v1 on frozen `dev20` is a **revise**. Mention-unit v2 on
the same letters is an **answer**: gold SeizureFrequency wording
appears as `clinical_name`, and empty-gold extras did not rise. The
frozen-language `dev140` transfer is a **revise**: wording still
copies (131/187); empty-gold extras rose versus v4 / trust-item. This
amendment does not change Decision 0050. The v4 `trust_item` remasure
on saved `dev140` raws remains a separate **answer**. Owner:
[mention-unit v2 `dev140`](../research/exectv2/mention_unit_v2_fork_a_luna_dev140_2026-08-16.md),
[mention-unit v2](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md),
[instruction job](../research/exectv2/prompt_variant_slots_2026-08-16.md).
Mention-unit v1 and the v9 rule-vs-prompt note are pruned; recover from
Git history if needed.

## Owners

* Implementation plan:
  [ExECT LLM representation and hybrid re-evaluation](../plans/exect_llm_representation_and_hybrid_revaluation_2026-08-16.md)
* Instruction-job design note:
  [model-facing job](../research/exectv2/prompt_variant_slots_2026-08-16.md)
* Mention-unit v2 hybrid encoder catalog:
  [hybrid encoder](../research/exectv2/mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md)
* Mention-unit v2 empty-gold extras catalog:
  [extras catalog](../research/exectv2/mention_unit_v2_empty_gold_sf_extras_luna_dev140_2026-08-16.md)
* Mention-unit v2 leftover-form remasure:
  [leftover-form](../research/exectv2/mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md)
* Mention-unit v2 `dev140` result:
  [mention-unit v2 `dev140`](../research/exectv2/mention_unit_v2_fork_a_luna_dev140_2026-08-16.md)
* Mention-unit v2 `dev140` protocol:
  [mention-unit v2 `dev140` protocol](../research/exectv2/mention_unit_v2_fork_a_luna_dev140_protocol_2026-08-16.md)
* Mention-unit v2 result:
  [mention-unit v2](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md)
* Mention-unit v2 protocol:
  [mention-unit v2 protocol](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md)
* Current family ownership:
  [Decision 0040](0040-final-exect-llm-with-rules-family-ownership.md)
* Current comparison boundary:
  [Decision 0041](0041-single-call-exect-model-comparison.md)
* Current selected assembly policy:
  [Decision 0045](0045-exect-default-policy-not-joint-combined.md)
