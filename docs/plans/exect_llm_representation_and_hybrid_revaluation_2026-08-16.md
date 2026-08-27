# ExECT LLM representation and hybrid re-evaluation

Date: 2026-08-16  
Status: Fork A `v4` `dev20` is a negative result; v4 `dev140` damage catalog is an answer; trust-item remasure is an answer; mention-unit v1 `dev20` is a revise; prompt fundamentals are signed off; mention-unit v2 `dev20` is an answer; mention-unit v2 `dev140` is a revise; empty-gold extras catalog is an answer; hybrid encoder catalog is an answer; leftover-form remasure is an answer ([leftover-form](../research/exectv2/mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md))  
Owner: ExECT pipeline and evaluation work

## Purpose

Re-evaluate the ExECT `llm` and `llm_with_rules` methods around the clinical
representation the model should produce, using the Gan 2026 LLM-only and
structured-events pipelines as the design precedent.

The current ExECT prompt asks the model to emit a representation that is too
close to the gold/scorer shape. This makes deterministic code responsible for
recovering facts the model should have expressed naturally, while also making
the LLM-only and hybrid methods artificially similar. The intended result is a
clearer two-method comparison:

* `llm` asks the model for clinically useful, evidence-backed atomic facts and
  semantic attributes. Deterministic code performs transport, evidence, and
  mechanical representation checks only.
* `llm_with_rules` asks the model for the same kind of complete atomic facts
  and exact evidence, but leaves clinical attribute parsing to named
  deterministic rules before benchmark projection.

The hybrid should be better because rules make a useful clinical event
machine-comparable and resolve bounded conventions—not because the prompt has
forced the model to predict arbitrary gold encodings.

This plan does not change the selected v0.9.24 / Decision 0050 result, alter
gold, inspect ExECT `test60`, or authorize new model calls before the contract
and protocol are approved.

## Governing evidence and constraints

* Gan semantic-versus-scoring separation:
  `docs/design/gan2026_normalization_semantics.md`.
* Gan event-ledger precedent:
  `docs/architecture/method_cards/gan2026_llm_only.md` and
  `docs/architecture/method_cards/gan2026_llm_with_rules.md`.
* Current ExECT ownership boundary:
  `docs/decisions/0040-final-exect-llm-with-rules-family-ownership.md`.
* Current one-call comparison boundary:
  `docs/decisions/0041-single-call-exect-model-comparison.md`.
* Current selected assembly policy:
  `docs/decisions/0045-exect-default-policy-not-joint-combined.md`.
* Current primary comparison fill:
  `docs/decisions/0046-exect-primary-method-comparison-boundary.md` and
  `docs/decisions/0050-current-stack-hybrid-primary-fills.md`.
* v26 is evidence for redesign, not a candidate to promote: it was clean to
  parse but fell to 0.8610 headline F1, 0.7111 SeizureFrequency F1, and 7/20
  exact on the frozen development sample.
* Development rows may be inspected; `test60` remains aggregate-only.
* Any rule that changes event selection, state, timeframe, multiplicity,
  diagnosis concept, or other clinical meaning must be named, attributed,
  tested, and ablated separately from representation and scorer formatting.

## Target method contracts

Both methods target the same ExECT clinical inventory: an independently scored
set of atomic, evidence-backed facts. They use matched one-call lanes with the
same rows, model, generation settings, and control policy, but their model
schemas are intentionally different. This tests model-led structuring against
deterministic parsing without allowing either lane to replace model recall with
an independent extractor.

### Shared clinical inventory

The model should return a structured inventory, not gold-shaped mentions. Each
inventory item is one atomic clinical proposition and should preserve, as
applicable:

* family and clinically meaningful event type;
* a complete natural-language event statement and exact supporting evidence;
* assertion and temporality (current, historical, planned, resolved,
  negated, uncertain);
* subject and scope, including seizure type or medication target;
* quantities, units, interval/window, duration, and change direction as stated;
* relevant clinical qualifiers such as diagnosis concept, regimen purpose, or
  investigation result; and
* explicit absence or cessation facts only when the note supports that absence.

Multiple facts may share one evidence span. For example, a current regimen and
its planned withdrawal are separate Prescription items, and a current seizure,
an older seizure, and a ten-month seizure-free interval are separate
SeizureFrequency items. ExECT does not require one fact to win over another.

The inventory uses a shared envelope with small, family-specific flat
attributes. Prefer semantic names such as `name`, `dose`, `unit`, `schedule`,
`purpose`, `status`, `type`, `count`, `period`, `result`, and `certainty` over
legacy scorer names such as `DrugName` or `NumberOfSeizures`. The scorer adapter
owns the legacy mapping.

The schema must allow clinically useful facts that do not map one-to-one onto a
gold annotation. For example, “last seizures in teenage years” should remain a
historical last-event fact with its evidence and temporal scope. A later rule
may derive an ExECT state or scorer-facing attribute from an emitted fact, but
the model should not be asked to collapse the fact merely because the
benchmark stores a different encoding.

### `llm`

The model owns the clinical inventory and its semantic attribute parsing. The
model output uses a shared envelope with a family-specific flat `attributes`
object. For example, a Prescription item may contain `name`, `dose`, `unit`,
`schedule`, `purpose`, and `status`.

Deterministic stages may:

* parse and validate the payload;
* perform format-only repair;
* preserve exact evidence and reject unsupported evidence;
* flatten the inventory without adding clinical facts; and
* expose the raw semantic inventory and, separately, any scorer adapter needed
  to compare representations.

They must not recover missing diagnosis concepts, invent seizure-frequency
states, apply diagnosis residual additions, or perform diagnosis/prescription
recoveries. The LLM-only score must be defined against a declared semantic
view and must not silently inherit hybrid transforms.

### `llm_with_rules`

The model receives the same clinical inventory objective and one-call boundary,
but its output intentionally contains only the event carrier and evidence:
`family`, `event`, and `evidence`. Clinical attributes are forbidden in this
model schema.

Rules may parse both the event and its exact evidence for that emitted
inventory item. They may normalize or derive an attribute directly supported by
that item, but they may not search unrelated note text or create a new fact
from a supported span.

Deterministic stages then own named transformations in this order:

1. transport and schema repair;
2. evidence validation and event-level quality gates;
3. family-specific parsing into the semantic task representation;
4. bounded semantic normalization and attribute derivation;
5. deduplication and materialization of clinician-useful and benchmark views;
6. scorer projection.

If parsing fails, the raw event and evidence remain in the semantic trace and
only the affected projection fails. Every transformation must retain
before/after events, rule category, action, evidence, and first
prediction-changing owner. The pipeline must never label a semantic change as
“just projection.”

## Representation decisions to resolve before implementation

For each family, create a small contract table with four columns:
`clinical fact the model should express`, `simple semantic fields needed to
preserve it`, `deterministic parsing or derivation allowed`, and `benchmark
projection`.

* **Diagnosis:** preserve each model-emitted concept and assertion separately
  from CUI lookup, heading conventions, synonym normalization, subsumption,
  and any residual recovery. Normalize an emitted concept, but do not add a
  model-absent parent, companion, or residual concept in the default hybrid.
* **SeizureFrequency:** represent rate statements, state changes, last-event
  dates/durations, seizure type, historical versus current scope, and
  “never had”/“no further” distinctions. Treat supported zero-event intervals
  as explicit facts. Rules may derive ExECT state and ownership fields from an
  emitted fact, but must not lose the natural event or select one fact over
  another.
* **Prescription:** represent medication, action, dose, unit, schedule,
  route, purpose, start/stop/change status, and planned versus active regimen.
  Current regimens and planned changes are separate facts when both are stated.
  Rules may normalize surfaces and parse explicitly emitted regimens; they must
  not substitute a deterministic medication extractor for the model lane.
* **Investigations:** represent the investigation, status/result, date or
  plan status, and evidence. Rules may normalize, deduplicate, and project
  modality/result fields from an emitted fact without inventing a finding.

Use gold-anchored semantic fact and attribute recovery as the primary semantic
evaluation where the annotations support it. Retain the existing
`clinical_headline` scorer as a declared benchmark projection, not as the sole
definition of clinical success. Report supported facts retained, unmapped,
added, removed, and transformed; do not treat unannotated but evidence-backed
facts as automatic errors or silently convert them into new gold labels.

## Implementation phases

### Phase 0 — Freeze the question and inventory current behavior

1. Add a predeclared study protocol naming splits, row policy, model, prompt
   version, replay mode, scorer, repair policy, and no-holdout rule.
2. Inventory every current ExECT model field, prompt instruction, parser,
   projection, diagnosis recovery, SF state rule, prescription lens, scorer
   adapter, and trace field.
3. Build a dev140 ledger of where current output is gold-shaped, where a rule
   changes clinical meaning, and where v26 loses clinically useful information.
4. Define the minimum representative development slice, including shared-
   evidence multiple facts, zero-event intervals, planned medication changes,
   diagnosis parent/companion additions, and investigations with results.

Deliverable: approved contract table and row-level development taxonomy. No
production behavior or locked-split change.

### Phase 1 — Define the shared semantic event contract

1. Design a versioned ExECT inventory schema inspired by Gan's event ledger,
   but keep ExECT-specific families and simple flat attributes.
2. Define separate model contracts: semantic attributes for `llm`, and only
   `family`, `event`, and `evidence` for `llm_with_rules`.
3. Make evidence, temporality, assertion, scope, and natural event text first-
   class fields; remove fields whose only purpose is matching a gold encoding.
4. Define allowed representations for ambiguity, absence, cessation, planned
   change, and multiple facts sharing one evidence span.
5. Specify which fields are model-owned, deterministic parsing or derivation
   outputs, and scorer-only fields. Add the rule that no model-absent fact may
   be recovered by the default hybrid.
6. Add schema snapshots, prompt contract tests, parse/repair tests, and an
   attribution record before making live calls.

Deliverable: a frozen semantic contract and machine-readable ownership matrix.

### Phase 2 — Rebuild `llm_only` as a genuine model-led baseline

1. Update the prompt to request the semantic inventory and family-specific flat
   attributes, not CUI/gold-shaped outputs.
2. Keep only transport/schema repair, evidence containment, and mechanical
   flattening in the LLM-only path.
3. Remove or bypass diagnosis recovery, SF state projection, unknown
   suppression, prescription recovery, and other clinical transforms from the
   LLM-only score path.
4. Preserve raw model events and a semantic candidate view in every row trace.
5. Define the comparison score before the first live batch and report any
   benchmark projection separately from the raw semantic result.

Deliverable: reproducible ExECT LLM-only implementation with no hidden hybrid
behavior and a focused test suite.

### Phase 3 — Rebuild `llm_with_rules` as semantic normalization plus bounded rules

1. Use the matched one-call `llm_with_rules` lane, whose model output contains
   only atomic event text and exact evidence; do not accept clinical attributes
   in its schema.
2. Implement family-specific parsing into the semantic representation first,
   then shared, clinically defensible normalization: units,
   dates, temporal anchors, canonical drug surfaces, diagnosis aliases, and
   investigation forms.
3. Reintroduce family rules one family at a time, beginning with SF temporal
   interpretation and state construction, then Prescription, Diagnosis, and
   Investigations.
4. Keep model-absent diagnosis additions and other clinical fact recovery out
   of the default hybrid. If proposed separately, evaluate them as a distinct
   rule family rather than carrying them forward because they improve the old
   score.
5. Keep scorer projection last and report semantic facts, rule-derived
   attributes, rule-added facts, rule-removed facts, parse failures,
   representation-only changes, and benchmark changes separately.

Deliverable: a hybrid pipeline whose improvement can be attributed to named
   deterministic transformations.

### Phase 4 — Prove the representative slice

1. Replay saved outputs where the new contract can be evaluated without calls;
   otherwise run only the predeclared dev20 slice.
2. Inspect all changed development rows and classify rescues, regressions,
   retained misses, evidence failures, and representation losses.
3. Run family-level and rule-family ablations. A rule must show its clinical
   purpose, exact evidence, and net rescue/harm before it is retained.
4. Compare old LLM-only, new LLM-only, old hybrid, and new hybrid on matched
   rows, with the old selected stack retained as a control. The new lanes use
   one independent model call each per row, with the same model and generation
   settings.

Deliverable: a development report and decision recommending keep, revise, or
reject for each family and rule group.

### Phase 5 — Transfer and promotion gate

1. Transfer the selected contract and prompt unchanged to dev140.
2. Require clean parse/schema accounting, exact-evidence accounting, semantic
   retention, attribution completeness, and no unapproved rule changes.
3. Run the repository's focused tests, then the required `.venv` checks:
   `python -m pytest`, `ruff check src tests`, and `mypy src`.
4. Only after a separate predeclared holdout protocol may aggregate-only
   `test60` re-scoring occur. No row-level holdout error analysis is allowed.
5. Update decisions, generated architecture, method cards, README, status, and
   paper claim boundaries only after the evidence owner is complete.

## Success criteria

The redesign is successful only if:

* `llm_only` contains no hidden clinical recovery or hybrid rule behavior;
* both methods target the same clinically meaningful atomic inventory, while
  their method-specific model contracts remain explicit;
* hybrid changes are individually attributable and reversible;
* natural facts such as historical last-event statements survive into the
  semantic trace even when they project to an arbitrary ExECT form;
* the evaluation reports raw event/evidence coverage, semantic attribute
  retention, hybrid parse success and failure, benchmark projection changes,
  and every added, changed, or dropped field;
* the hybrid improves useful representation or benchmark projection without
  recovering model-absent facts, relying on gold-shaped prompt leakage, or
  using unreported scorer repairs; and
* claims remain limited to the declared development/holdout evidence and do
  not imply clinical validation.

## Non-goals

Do not tune the current v26 prompt, revive archived `combined` assembly, add a
second model call within either method, inspect locked ExECT rows, change
annotations, or optimize the scorer before the semantic contract is settled.
The matched comparison uses one call per method lane, not a second call within
one lane. Do not remove useful Gan rules; use Gan as the precedent for
separation and attribution, not as a reason to copy Gan-specific labels or
synthetic-letter quirks into ExECT.

## Completion record

The implementation, protocol, contract tests, dev20 artifact, ablations, and
bounded decision are recorded in the [development report](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).
The row-level revise decision is owned by the
[dev20 mechanism analysis](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).
The deeper design challenge is
[assumption challenge](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md):
v2 changed the task and kept the scorer. **Fork A is selected:** the scored
object remains the ExECT coded inventory; Decision 0040 stays in force; the
v10 grammar belongs in named hybrid rules. The live `dev20` v3 run is a **revise**
result: [v3 result](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).
The measured research-lane contract is `exectv2_semantic_inventory_v4`.
The live `dev20` v4 run is a **negative_result**:
[v4 result](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).
Mention-unit v1 on frozen `dev20` is a **revise**:
mention-unit v1 (pruned; recover from Git history).
Mention-unit v2 on frozen `dev20` is an **answer**:
[mention-unit v2](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_2026-08-16.md).
The frozen-language `dev140` transfer is a **revise**: wording still
copies (131/187 exact on `llm`); empty-gold extras rose versus v4 /
trust-item. Do not retune. Do not start mention-unit v3 or Fork B from
that extras rise.
[mention-unit v2 `dev140`](../research/exectv2/mention_unit_v2_fork_a_luna_dev140_2026-08-16.md).
The empty-gold extras catalog is an **answer**: more frequency
statements on shared empty-gold letters, not more over-read letters.
[extras catalog](../research/exectv2/mention_unit_v2_empty_gold_sf_extras_luna_dev140_2026-08-16.md).
The hybrid encoder catalog is an **answer**: names stay; counts and
investigation results do not.
[hybrid encoder](../research/exectv2/mention_unit_v2_hybrid_encoder_damage_luna_dev140_2026-08-16.md).
The leftover-form remasure is an **answer**: leftover evidence words
recover form. Default encoder stays `landed`.
[leftover-form](../research/exectv2/mention_unit_v2_leftover_form_encoder_luna_dev140_2026-08-16.md).
Prompt fundamentals stay signed off: only Prescription is current-only;
leftover words go in `llm` fields or hybrid evidence.
[prompt fundamentals](exect_prompt_fundamentals_2026-08-16.md).
Protocol:
[mention-unit v2](../research/exectv2/mention_unit_v2_fork_a_luna_dev20_protocol_2026-08-16.md);
[mention-unit v2 `dev140`](../research/exectv2/mention_unit_v2_fork_a_luna_dev140_protocol_2026-08-16.md).
Instruction job (also over-applies “current”):
[instruction job](../research/exectv2/prompt_variant_slots_2026-08-16.md).
A v4 `dev140` projection-damage catalog is an **answer**:
[catalog](../research/exectv2/../../decisions/0055-exect-semantic-inventory-and-method-contracts.md).
The no-call `trust_item` remasure on those saved raws is an **answer**:
[trust-item remasure](../research/exectv2/prompt_variant_slots_2026-08-16.md).
The published v9 manual is a closed coding book for rewrite, not a
prompt (v9 placement note pruned; recover from Git history).
No holdout claim or selected-stack change is authorized.

## Fork A v4 contract

This section is the measured v4 scored-object contract. Mention-unit
v2 uses the signed-off clinical-name prompts, not the rows below. The
earlier “shared clinical inventory” language remains the v4 historical
intent. The “apply now” / “current rates” rows below are part of the
current-scope drift; do not copy them into the next prompt.
v3 asked for the coded set and still lost on type and count encoding.

One list of items. Each item is a clinical event string. `llm` also fills
coded attributes on that item. Hybrid items are event and evidence only.

| Family | Model should emit | Hybrid may derive or rewrite | Headline projection |
| --- | --- | --- | --- |
| Diagnosis | Named epilepsy and seizure-type events that apply now | Event-only parse, heading split, closed-table rewrite, noise drop, JME phenotype drop | CUI and `DiagCategory` |
| SeizureFrequency | Current rates, seizure-free states, last events as zero-count events | Event-only parse, dual-family reuse onto Diagnosis when the event names a typed rate, `sf_attribute_encoding`, uncoded-phenomenology suppression | `NumberOfSeizures` and type CUI |
| Prescription | Current regimens | Event-only parse preferring the event drug, planned-only and non-epilepsy suppression | Drug name, dose, unit, schedule |
| Investigations | Completed tests and results | Event-only parse, pending-test suppression | Modality performed and result |

Shared rules:

* Empty family: emit nothing. Empty-gold extras are false positives.
* `llm` emits a flat typed `attributes` object. Nested family-name blobs are
  unwrapped as transport repair. The adapter is a declared scorer map,
  including last-event → `NumberOfSeizures=0`. Non-current prescriptions stay
  in the semantic trace.
* `llm_with_rules` emits only `family`, `event`, and `evidence`. Rules parse
  the event string and a closed table. They do not read the evidence span or
  the letter to grow mentions. Letter-level residual addition is out.
* Decision 0040 stays in force for rewrite, project, and suppress.
  Extractor substitution is not allowed.
* One call per method per row. Matched model and settings.
* No `dev140` or `test60` until a predeclared `dev20` is mechanically clean
  and SeizureFrequency extras stay well below 36.
