# Rule catalogue: schema, encode, and revise

Date: 2026-08-21
Status: paper source; development inventory
Owners: [five reported cells](five_rungs_of_rule_help_2026-08-20.md) for cell meaning;
this file for the named-rule list

This is the comparable grain for both tasks: **named, independently
stoppable rules**, classed by the locked assignment rule.

- **Extract** = model ledger. Parse is code. On Gan, score the model's
  `final_label` only. `_normalize_event` / `_resolve_final_label` run
  at encode.
- **Encode** = same finding written into the designed / gold
  form, including codebook attach and Gan resolve-if-blank. `project_cuis`
  is encode and runs at the encode-replay stop.
- **Select** = gate / drop / rewrite / reselect / invent.
  Same five kinds on Gan and ExECT.

The rules row of the 3×3 is a **different** rule set. It is not this
catalogue. Live ExECT `exect_llm_only` still scores the mixed
`project_and_gate` bundle; that view is not cell 2. Replay cells 2–4
use the split below.

### How to read: runs at vs authority

- **Runs at** — where the flag fires in the stack: schema, encode
  (encode-replay), or revise.
- **Authority** — what kind of hop the rule is: parse, dialect,
  encode, gate, rewrite, reselect, invent.

A rule can run at encode and still be encode authority (not dialect). SF
`encoding.*` on encode-replay is encode or dialect unless the row
invents a new mention. Diagnosis surface spelling / alias runs at
revise: dialect when spelling-only, rewrite when concept remap.

Status:

- **live** — on in the default hybrid / replay stack
- **format-replay** — applied on ExECT encode cell (cell 3); the live producer may
  not run it

---

## Gan 2026

One current seizure-frequency label. Replay cells 2–4 share one
`gan_llm_with_rules` raw. Default revise mode is `llm_revise`
(legacy alias: `hybrid_full_stack`).

### Schema

| Rule | Status | Authority | What it does |
| --- | --- | --- | --- |
| `json_dialect_repair` | live on `raw_model` and later | parse | Recover JSON / Python-literal dialect so the object parses |
| `repair_selected_answer_payload` (structural + quarantine) | live | parse | Keep a typed events+selection object; quarantine illegal event rows |
| Schema validation (`StructuredExtractionRecord`) | live | parse | Reject an untyped payload |
| Event normalize (`_normalize_event`) | live | encode / render leak | Attach a Gan-normalized label, kind, and monthly rate to each event |
| Resolve selected label (`_resolve_final_label`) | live | encode / render leak | Turn the model's selected event ids into one submitted string |

### Encode

`basic_label_repair` is set in `llm_encode` (legacy alias
`selected_evidence_derivation`) but
**skipped at runtime** when the selected-evidence renderer is on.

| Rule | Status | Authority | What it does |
| --- | --- | --- | --- |
| `selected_evidence` renderer | live on cell 3 | encode (not dictionary) | Rewrite the submitted string from the already chosen evidence; does not change `selected_event_ids` |
| `words_to_numbers` / `once_twice_thrice` | live, inside renderer | dialect | Same rate, digit/word form |
| `format_prediction_rate` | live, inside renderer | encode | `N per unit` gold dialect |
| Early / late / pre-window rate derivation | live, inside renderer | encode | Bound flatten, explicit rate, Q-interval, median interval, vague+period |
| `daily_label_from_selected_evidence` | live, inside renderer | encode | Daily dialect from the selected span |
| `no_reference_daily` | live (fix flag on) | encode | Inside the rate renderer: treat some no-reference daily readings as encode |
| Cluster derivation | live, inside renderer | encode | Two-part cluster gold dialect from the selected span |
| Window count (single / range / sum) | live, inside renderer | encode | Count-over-window dialect |
| Diary dialect in the renderer (`monthly_diary_label_from_text` and calendar / sleep-awake / date-list helpers) | live, inside renderer | encode | Same selected span, diary string |
| `blocks_inexact_span_family_rewrite` | live, inside renderer | gate | Block a kind change unless the quote is an exact source span |
| `basic_label_repair` / `repair_prediction_label` | live only when selected-evidence is **off** | encode | Label-string normalize without selected evidence |

### Revise

Applied in `DEFAULT_SEMANTIC_FAMILY_ORDER` when the matching flag is on.

| Rule | Status | Authority | What it does |
| --- | --- | --- | --- |
| `usual_interval` | live | reselect | Prefer a stated usual interval over a brief-daily or unknown selection |
| `typical_over_ytd` | live | reselect | Prefer a typical recurring rate over a year-to-date observation total |
| `breakthrough` | live | reselect | If the label is unknown / no-reference, write a recent breakthrough count over a seizure-free duration |
| `non_epileptic` | live | rewrite | If current events are non-epileptic, submit `no seizure frequency reference` |
| `residual_jerk` | live | reselect | Retarget some unknown / multiple / per-day labels using dated residual jerks near clinic |
| `post_change_burst` | live | reselect | Override a seizure-free or high-rate label after a treatment-change burst |
| `dated_sequence` | live | reselect | Build a rate from a near-clinic dated seizure sequence |
| `elapsed_anchor` | live | reselect | Rate or seizure-free duration from time since a dated last event |
| Sustained seizure-free veto on `elapsed_anchor` | live | gate | Keep a sustained selected seizure-free label; record the elapsed proposal as vetoed |
| `monthly_diary` (revise family) | live | reselect | May switch the submitted label to a diary-derived state |
| Diary preserve-label guard | live | gate | Leave the current label when the diary family must not override |
| `diary_sum_all_months` | live | rewrite | Hop-audit fix inside diary / revise |
| `vague_seizure_free_diary` | live | rewrite | Hop-audit fix for vague seizure-free diary wording |
| `date_list_span` | live | rewrite | Hop-audit fix for date-list span reading |

---

## ExECTv2

Four-family inventory. Replay cells 2–4 share one `exect_llm_only` raw.
Cell 4 is living assembly (`residual_benchmark_added`).

### Shared (all families)

| Rule | Class | Status | Authority | What it does |
| --- | --- | --- | --- | --- |
| Parse Compact events + flatten (`mentions_from_events`) | Schema | live | parse | Typed mention per event; attribute name aliases (`name` → `DrugName`) |
| Format-only JSON retry | Schema | live on eligible local **calls**; not in cells 2–4 replay | parse | One re-ask after schema fail |
| Drop out-of-scope entity | Schema | live | gate | Non-four-family names never enter the inventory |
| Evidence copy from mention text (Dx / Rx) | Encode | live + format-replay | encode | Same finding; fill evidence from exact mention text |
| Exact-substring evidence whitespace repair | Encode | live + format-replay | dialect | Same finding |
| Strip model `CUI` / `CUIPhrase` | Encode | live + format-replay | encode | Drop model-supplied codebook ids |
| Closed-vocab / legal-key strip (`repair_attributes`) | Encode | live + format-replay | encode | Drop illegal keys/values; canonicalize remaining values |
| `project_cuis` | Encode | live + format-replay | encode (runs_at=encode) | Attach gold codebook id; does not add/drop a mention |
| Evidence reject (not a substring) | Revise | live (gated producer); **not** on encode-replay | gate | Withhold the finding |
| SF no-state render drop | Revise | live producer | gate | Drop SeizureFrequency with no frequency-state attrs |
| Investigations modality-only duplicate drop | Revise | live producer | gate | Drop a modality-only mention when a result-bearing twin exists |

### Diagnosis

| Rule | Class | Status | Authority | What it does |
| --- | --- | --- | --- | --- |
| `encoding.diagnosis_standard_name` | Encode | format-replay | encode | Write the same extracted diagnosis with a closed benchmark name; spelling, abbreviations, and word-order only; no qualifier overwrite |
| Surface spelling / alias (`DIAGNOSIS_SURFACE_CONVENTION_REPAIRS`, alias map) | Revise in the lens (some rows are spelling-only) | live lens | dialect when spelling-only; rewrite when concept remap | Rewrite submitted concept text toward gold wording; includes both spelling and concept remaps |
| `diagnosis_convention_attribute_repairs` | Encode when text already rewritten | live, on rewrite | encode (encode-when-already-rewritten) | Fill `DiagCategory` / Certainty / Negation |
| Concept remap from evidence (`epilepsy` + intractable cue; FCD → syndrome; `focal onset` → `focal epilepsy`) | Revise | live lens | rewrite | Different submitted concept |
| `selection.diagnosis_specificity_hierarchy` | Revise | live lens | rewrite | Stated hierarchy: lobe syndromes under focal epilepsy under epilepsy; generalised epilepsy on the other branch. A probable temporal/frontal/parietal/occipital modifier (or a named lobe syndrome) may overwrite `epilepsy`, `focal epilepsy`, or a structural-etiology form. Possible laterality may overwrite generic `epilepsy`. Possible or queried onset does not create a lobe syndrome. Cross-branch sibling facts stay put. |
| `selection.diagnosis_source_local_specificity` | Revise | live Select stack | rewrite | Restore the encoded source diagnosis when a later Select rewrite broadens an already-specific diagnosis or conflates a generic diagnosis with a sibling class |
| `selection.diagnosis_explicit_heading_phenotype` | Revise | live Select stack | reselect | Retain an absence row explicitly emitted under a Diagnosis heading unless JME is present and owns that phenotype |
| Convention-noise drop | Revise | live | gate | Delete standalone symptoms, weak generic epilepsy, family-history context, PNES/febrile |
| JME covers phenotype drop | Revise | live | gate | Delete absence/jerk siblings when JME is present |
| Bounded residual-add | Revise | live | invent | Invent a Diagnosis from a source pattern |
| Residual redundancy skip | Revise | live | gate | Block an add already implied by kept concepts |

Diagnosis encode-replay runs only `encoding.diagnosis_standard_name`, the
same-fact subset of the convention dictionary. Qualifier overwrite
(`focal epilepsy` plus probable temporal → `temporal lobe epilepsy`) is
select, not encode. Finding/cause-to-syndrome remaps and any add, drop,
split, or merge remain revise operations.

### SeizureFrequency

| Rule | Class | Status | What it does |
| --- | --- | --- | --- |
| `encoding.word_number` | Encode | format-replay + inside SF projection | Digit form of a word count |
| `encoding.range_split` | Encode | format-replay + projection | `2-3` → lower/upper |
| `encoding.interval_completer` | Encode | format-replay + projection | Fill period/count from “every N …” |
| `encoding.last_event_zero` | Encode | format-replay + projection | Complete a last-event zero count |
| `encoding.last_clinic_frame` | Encode | format-replay + projection | Complete a last-clinic frame |
| `encoding.dated_heading_count` | Encode | format-replay + projection | Complete a dated heading count |
| `encoding.mention_text_cleanup` | Encode | format-replay + projection | Same mention, cleaner text |
| `encoding.sf_local_evidence` | Encode | format-replay | Write explicit `seizure free` when the same mention is already a zero count and the local evidence says so; no type retarget or invented bound |
| `selection.sf_named_type_from_evidence` | Revise | live projection | rewrite | Generic `seizure`/`episode`, or parent `absence`, may take one unambiguous named type from the mention's own evidence |
| `selection.sf_explicit_recurrence_lower_bound` | Revise | live projection | rewrite | Explicit `has had further … seizures` with no count writes `LowerNumberOfSeizures=1` |
| `selection.sf_named_type_identity` | Revise | live Select stack | rewrite | Reconcile all named SF rows in one evidence/state group so a row cannot be reassigned to a sibling seizure type; permits explicit more-specific refinements |
| `selection.sf_to_diagnosis_explicit_type` | Revise | live Select stack | invent | Add the Diagnosis view of an already-selected named SF fact. This is a ledger-only benchmark-format projection, not an unused-note scan |
| `encoding.sf_standard_name` | Encode | format-replay | Write the same seizure type with a closed 16-head name; attach its CUI at `project_cuis` |
| Count / unit / month normalize | Encode | live helpers | Designed-form tokens |
| CUIPhrase-preserve bundle | Encode | live, inside ownership | Keep phrase after CUI attach |
| Exact-mention dedupe | Encode | live projection | Collapse identical mentions |
| `state.drop_unlabelled_active_rate` | Revise | live | Drop unlabelled attack/episode rates |
| `state.drop_historical_active_rate` | Revise | live | Drop onset / younger-age rates |
| `state.drop_preceded_by_current_seizure_free` | Revise | live | Drop until-now rates beside current seizure-free |
| `state.drop_historical_or_advice_seizure_free` | Revise | live | Drop best-period / DVLA seizure-free |
| `state.last_event_date_to_seizure_free` | Revise | live | Dated last event → seizure-free |
| `state.last_event_active_to_seizure_free` | Revise | live | Active-rate last event → seizure-free |
| `state.temporal_direction` | Revise | live | Repair Since/During / temporal attrs |
| `ownership.generic_active_to_named` / `generic_surface_to_named` | Revise | live | Assign the rate to the named type |
| `ownership.drop_umbrella_clone` | Revise | live | Drop a generic clone of a named rate |
| `ownership.drop_bare_count_active_rate` | Revise | live | Drop a bare count beside a fuller rate |
| `ownership.drop_lifetime_oneoff_active_rate` | Revise | live | Drop a lifetime one-off |
| `ownership.drop_dated_cluster_next_to_free` | Revise | live | Drop a dated cluster beside seizure-free |
| `ownership.retarget_last_week_named_to_generic` | Revise | live | Retarget last-week named type |
| `ownership.drop_drugchange_before_if_other_active_rate` | Revise | live | Drop pre-change residue |
| `ownership.drop_scope_residue` | Revise | live | Drop leftover scope residue |
| `unknown_suppression.drug_response_scope` | Revise | live | Drop unknown change that is drug-response scoped |
| `unknown_suppression.contextual_or_historical_change` | Revise | live | Drop contextual / historical unknown change |
| Candidate-span residual add | Revise | live if spans exist | Add a state mention from a candidate span |

SF `encoding.*` on encode-replay is encode/dialect (same finding into
designed form) unless a row invents a new mention. Ownership retarget
and state drops at revise are rewrite / gate. Candidate-span residual
add is invent.

### Prescription

| Rule | Class | Status | Authority | What it does |
| --- | --- | --- | --- | --- |
| `encoding.prescription_local_slots` | Encode | format-replay | encode | Prefer cadence in the regimen's own mention over a sibling rescue phrase; repair one explicit local dose/unit pair; leave ranges and multi-dose text unchanged |
| `encoding.prescription_formulation_name` | Encode | format-replay | dialect | Strip a controlled/extended/modified/prolonged/sustained-release suffix when the remaining base drug is known |
| `encoding.prescription_standard_name` | Encode | format-replay | dialect | Write ordinary-regimen mention text as the resolved generic `DrugName`; preserve rescue, future-plan, and weight-based context |
| Brand → generic (`resolve_drug_surface` then `normalize_drug_name`) | Encode | format-replay; lens uses `normalize_drug_name` only | dialect | Same regimen, standard name |
| `DoseUnit` respell | Encode | format-replay + live lens | dialect | `mgs` → `mg` |
| `DrugDose` value normalize | Encode | format-replay + live lens | dialect | Same regimen |
| Fill `Frequency` if missing / `As_Required` | Encode | format-replay + live lens | encode | Same regimen |
| Prefer current dose over a current-to-target range | Encode | format-replay + live lens | encode | Still one regimen |
| Split fused AM/PM `DrugDose` | Revise | live lens | rewrite | One mention → two facts |
| Split slash-delimited daily doses | Revise | live lens | rewrite | Multiplicity change |
| Split explicit uneven once-daily | Revise | live lens | rewrite | Multiplicity change |
| Drop non-ASM | Revise | **live leftover** | gate | Deletes the finding; manifest says the lens never removes |
| Drop planned-start / titration-only | Revise | **live leftover** | gate | Deletes the finding |
| `selection.prescription_local_regimen_scope` | Revise | live Select stack | rewrite | Keep a rescue cadence local to its named medicine instead of spreading it to sibling regimens in the same evidence window |
| `selection.prescription_active_titration` | Revise | live Select stack | reselect | Retain the explicit initial current regimen before a future titration; prescribe/start requests and target-dose rows remain suppressed |
| `selection.prescription_exact_regimen_dedupe` | Revise | live Select stack | drop | Drop a historical-initiation assertion only when a current assertion carries the same exact regimen; identical current assertions retain benchmark multiplicity |

### Investigations

| Rule | Class | Status | Authority | What it does |
| --- | --- | --- | --- | --- |
| Strip cross-modality `*_Performed='No'` not in the mention text | Encode | format-replay + live lens | encode | Same test, drop junk attrs |
| Infer `*_Performed='Yes'` when a result is present | Encode | format-replay + live lens | encode | Same finding |
| `encoding.investigation_local_result` | Encode | format-replay | encode | Make an already-selected test abnormal when its modality-local evidence has an explicit unnegated abnormal finding |
| Pending-cue drop | Revise | live lens | gate | Delete await/request/appointment without a completed result |

---

## How to read a comparison

Schema is the same kind of thing on both tasks: get a typed object
(with Gan’s known label-render leak). Gan encode is one selected-
evidence encode renderer on one selected event — not a dictionary.
ExECT encode is several same-fact writers across four families; the
largest score move is codebook attach (`project_cuis`, encode at
encode-replay). Gan revise is nine mechanism families on one label
(mostly reselect). ExECT revise is per-family revise (gate, rewrite,
invent) plus SF projection.

Do not compare “4 gold families vs 9 Gan revise families.” Do not count regexes
as rulesets. A live leftover (Prescription non-ASM / planned-start)
is still revise until it is measured and either deleted or documented.
