# Rule catalogue: schema, format, and clinical post

Date: 2026-08-21
Status: paper source; development inventory
Owners: [five rungs](five_rungs_of_rule_help_2026-08-20.md) for rung meaning;
this file for the named-rule list

This is the comparable grain for both tasks: **named, independently
stoppable rules**, classed by the locked assignment rule. Schema is
parse and flatten only. Format is the same finding in designed writing.
Clinical post accepts, rejects, rewrites, or invents a finding. Gates
fold into post.

Rung 1 (rules only) is a **different** rule set. It is not this
catalogue. Live ExECT `exect_llm_only` still scores the mixed
`project_and_gate` bundle; that view is not rung 2. Replay rungs 2–4
use the split below.

Status:

- **live** — on in the default hybrid / replay stack
- **format-replay** — applied on ExECT rung 3; the live producer may
  not run it
- **default off** — coded, flag off
- **off** — present but not in the selected lens / mode
- **deleted** — removed; unknown names raise

---

## Gan 2026

One current seizure-frequency label. Replay rungs 2–4 share one
`gan_llm_with_rules` raw. Default post mode is `hybrid_full_stack`.

### Schema

| Rule | Status | What it does |
| --- | --- | --- |
| `json_dialect_repair` | live on `raw_model` and later | Recover JSON / Python-literal dialect so the object parses |
| `repair_selected_answer_payload` (structural + quarantine) | live | Keep a typed events+selection object; quarantine illegal event rows |
| Schema validation (`StructuredExtractionRecord`) | live | Reject an untyped payload |
| Event normalize (`_normalize_event`) | live | Attach a Gan-normalized label, kind, and monthly rate to each event |
| Resolve selected label (`_resolve_final_label`) | live | Turn the model's selected event ids into one submitted string |

### Format

`basic_label_repair` is set in `selected_evidence_derivation` but
**skipped at runtime** when the selected-evidence renderer is on.

| Rule | Status | What it does |
| --- | --- | --- |
| `selected_evidence` renderer | live on rung 3 | Rewrite the submitted string from the already chosen evidence; does not change `selected_event_ids` |
| `words_to_numbers` / `once_twice_thrice` | live, inside renderer | Same rate, digit/word form |
| `format_prediction_rate` | live, inside renderer | `N per unit` gold dialect |
| Early / late / pre-window rate derivation | live, inside renderer | Bound flatten, explicit rate, Q-interval, median interval, vague+period |
| `daily_label_from_selected_evidence` | live, inside renderer | Daily dialect from the selected span |
| `no_reference_daily` | live (fix flag on) | Inside the rate renderer: treat some no-reference daily readings as format |
| Cluster derivation | live, inside renderer | Two-part cluster gold dialect from the selected span |
| Window count (single / range / sum) | live, inside renderer | Count-over-window dialect |
| Diary dialect in the renderer (`monthly_diary_label_from_text` and calendar / sleep-awake / date-list helpers) | live, inside renderer | Same selected span, diary string |
| `blocks_inexact_span_family_rewrite` | live, inside renderer | Block a kind change unless the quote is an exact source span |
| `basic_label_repair` / `repair_prediction_label` | live only when selected-evidence is **off** | Label-string normalize without selected evidence |
| `basic_label_repair_format_only` | mode `strict_format` | Narrower label normalize |
| `clean_scorer_facing_gold_policy` | mode `clean_scorer_facing` | Scorer-facing gold dialect without selected evidence |

### Clinical post

Applied in `DEFAULT_SEMANTIC_FAMILY_ORDER` when the matching flag is on.

| Rule | Status | What it does |
| --- | --- | --- |
| `usual_interval` | live | Prefer a stated usual interval over a brief-daily or unknown selection |
| `typical_over_ytd` | live | Prefer a typical recurring rate over a year-to-date observation total |
| `breakthrough` | live | If the label is unknown / no-reference, write a recent breakthrough count over a seizure-free duration |
| `non_epileptic` | live | If current events are non-epileptic, submit `no seizure frequency reference` |
| `residual_jerk` | live | Retarget some unknown / multiple / per-day labels using dated residual jerks near clinic |
| `post_change_burst` | live | Override a seizure-free or high-rate label after a treatment-change burst |
| `dated_sequence` | live | Build a rate from a near-clinic dated seizure sequence |
| `elapsed_anchor` | live | Rate or seizure-free duration from time since a dated last event |
| Sustained seizure-free veto on `elapsed_anchor` | live | Keep a sustained selected seizure-free label; record the elapsed proposal as vetoed |
| `monthly_diary` (post family) | live | May switch the submitted label to a diary-derived state |
| Diary preserve-label guard | live | Leave the current label when the diary family must not override |
| `month_x_typical_preserve` | **default off** | Hop-audit fix: keep a month-X typical reading |
| `diary_sum_all_months` | live | Hop-audit fix inside diary / post |
| `vague_seizure_free_diary` | live | Hop-audit fix for vague seizure-free diary wording |
| `date_list_span` | live | Hop-audit fix for date-list span reading |

---

## ExECTv2

Four-family inventory. Replay rungs 2–4 share one `exect_llm_only` raw.
Rung 4 is living assembly (`residual_benchmark_added`).

### Shared (all families)

| Rule | Class | Status | What it does |
| --- | --- | --- | --- |
| Parse Compact events + flatten (`mentions_from_events`) | Schema | live | Typed mention per event; attribute name aliases (`name` → `DrugName`) |
| Format-only JSON retry | Schema | live on eligible local **calls**; not in rungs 2–4 replay | One re-ask after schema fail |
| Drop out-of-scope entity | Schema | live | Non-four-family names never enter the inventory |
| Evidence copy from mention text (Dx / Rx) | Format | live + format-replay | Same finding; fill evidence from exact mention text |
| Exact-substring evidence whitespace repair | Format | live + format-replay | Same finding |
| Strip model `CUI` / `CUIPhrase` | Format | live + format-replay | Drop model-supplied codebook ids |
| Closed-vocab / legal-key strip (`repair_attributes`) | Format | live + format-replay | Drop illegal keys/values; canonicalize remaining values |
| `project_cuis` | Format | live + format-replay | Attach gold codebook id; does not add/drop a mention |
| Evidence reject (not a substring) | Post | live (gated producer); **not** on format-replay | Withhold the finding |
| SF no-state render drop | Post | live producer | Drop SeizureFrequency with no frequency-state attrs |
| Investigations modality-only duplicate drop | Post | live producer | Drop a modality-only mention when a result-bearing twin exists |

### Diagnosis

| Rule | Class | Status | What it does |
| --- | --- | --- | --- |
| Surface spelling / alias (`DIAGNOSIS_SURFACE_CONVENTION_REPAIRS`, alias map) | Post in the lens (some rows are spelling-only) | live lens | Rewrite submitted concept text toward gold wording; includes both spelling and concept remaps |
| `diagnosis_convention_attribute_repairs` | Format when text already rewritten | live, on rewrite | Fill `DiagCategory` / Certainty / Negation |
| Concept remap from evidence (`epilepsy` + intractable cue; FCD → syndrome; `focal onset` → `focal epilepsy`) | Post | live lens | Different submitted concept |
| Convention-noise drop | Post | live | Delete standalone symptoms, weak generic epilepsy, family-history context, PNES/febrile |
| JME covers phenotype drop | Post | live | Delete absence/jerk siblings when JME is present |
| Bounded residual-add | Post | live | Invent a Diagnosis from a source pattern |
| Residual redundancy skip | Post | live | Block an add already implied by kept concepts |
| Absence-preservation / residual-subsumption variants | Post | **off** (default variant `default`) | Policy around drops/adds |
| Heading recovery | Post | **off** | Historical; zero-fire |
| Generic-epilepsy companion | Post | **off** (hard `False`) | Used to add generic `epilepsy` beside a subtype |

Diagnosis format-replay does **not** run the convention rewrite. Rung 3
keeps written `epilepsy` and may only attach a CUI.

### SeizureFrequency

| Rule | Class | Status | What it does |
| --- | --- | --- | --- |
| `encoding.word_number` | Format | format-replay + inside SF projection | Digit form of a word count |
| `encoding.range_split` | Format | format-replay + projection | `2-3` → lower/upper |
| `encoding.interval_completer` | Format | format-replay + projection | Fill period/count from “every N …” |
| `encoding.last_event_zero` | Format | format-replay + projection | Complete a last-event zero count |
| `encoding.last_clinic_frame` | Format | format-replay + projection | Complete a last-clinic frame |
| `encoding.dated_heading_count` | Format | format-replay + projection | Complete a dated heading count |
| `encoding.mention_text_cleanup` | Format | format-replay + projection | Same mention, cleaner text |
| Count / unit / month normalize | Format | live helpers | Designed-form tokens |
| CUIPhrase-preserve bundle | Format | live, inside ownership | Keep phrase after CUI attach |
| Exact-mention dedupe | Format | live projection | Collapse identical mentions |
| `state.drop_unlabelled_active_rate` | Post | live | Drop unlabelled attack/episode rates |
| `state.drop_historical_active_rate` | Post | live | Drop onset / younger-age rates |
| `state.drop_preceded_by_current_seizure_free` | Post | live | Drop until-now rates beside current seizure-free |
| `state.drop_historical_or_advice_seizure_free` | Post | live | Drop best-period / DVLA seizure-free |
| `state.last_event_date_to_seizure_free` | Post | live | Dated last event → seizure-free |
| `state.last_event_active_to_seizure_free` | Post | live | Active-rate last event → seizure-free |
| `state.temporal_direction` | Post | live | Repair Since/During / temporal attrs |
| `ownership.generic_active_to_named` / `generic_surface_to_named` | Post | live | Assign the rate to the named type |
| `ownership.drop_umbrella_clone` | Post | live | Drop a generic clone of a named rate |
| `ownership.drop_bare_count_active_rate` | Post | live | Drop a bare count beside a fuller rate |
| `ownership.drop_lifetime_oneoff_active_rate` | Post | live | Drop a lifetime one-off |
| `ownership.drop_dated_cluster_next_to_free` | Post | live | Drop a dated cluster beside seizure-free |
| `ownership.retarget_last_week_named_to_generic` | Post | live | Retarget last-week named type |
| `ownership.drop_drugchange_before_if_other_active_rate` | Post | live | Drop pre-change residue |
| `ownership.drop_scope_residue` | Post | live | Drop leftover scope residue |
| `unknown_suppression.drug_response_scope` | Post | live | Drop unknown change that is drug-response scoped |
| `unknown_suppression.contextual_or_historical_change` | Post | live | Drop contextual / historical unknown change |
| Candidate-span residual add | Post | live if spans exist | Add a state mention from a candidate span |
| `state.drop_stale_older_zero` / `drop_never_had_or_resemble` / `retarget_seizure_free_span` | Post | **default off** (`residuals_v020`) | Extra residual projection |
| Dictionary rewrite / dictionary residual-add | Post | **off** | SF lens is pass-through |

### Prescription

| Rule | Class | Status | What it does |
| --- | --- | --- | --- |
| Brand → generic (`resolve_drug_surface` then `normalize_drug_name`) | Format | format-replay; lens uses `normalize_drug_name` only | Same regimen, standard name |
| `DoseUnit` respell | Format | format-replay + live lens | `mgs` → `mg` |
| `DrugDose` value normalize | Format | format-replay + live lens | Same regimen |
| Fill `Frequency` if missing / `As_Required` | Format | format-replay + live lens | Same regimen |
| Prefer current dose over a current-to-target range | Format | format-replay + live lens | Still one regimen |
| Split fused AM/PM `DrugDose` | Post | live lens | One mention → two facts |
| Split slash-delimited daily doses | Post | live lens | Multiplicity change |
| Split explicit uneven once-daily | Post | live lens | Multiplicity change |
| Drop non-ASM | Post | **live leftover** | Deletes the finding; manifest says the lens never removes |
| Drop planned-start / titration-only | Post | **live leftover** | Deletes the finding |
| Residual-add current regimens | Post | **off** | Measured net-harmful |
| Delete planned/historical as a general noise rule | Post | **off** | Removed; leftover is the planned-start drop |
| `current_guard_only` / `residual_explicit_current_only` | — | **deleted** | Unknown variant raises |

### Investigations

| Rule | Class | Status | What it does |
| --- | --- | --- | --- |
| Strip cross-modality `*_Performed='No'` not in the mention text | Format | format-replay + live lens | Same test, drop junk attrs |
| Infer `*_Performed='Yes'` when a result is present | Format | format-replay + live lens | Same finding |
| Pending-cue drop | Post | live lens | Delete await/request/appointment without a completed result |
| Full noise / result-binding | Post | **off** | Former thick lens |
| Residual investigation providers | Post | **off** in assembly | Prompt-side only |

---

## How to read a comparison

Schema is the same kind of thing on both tasks: get a typed object.
Gan format is one renderer on one selected event. ExECT format is
several same-fact writers across four families; the largest score move
is codebook attach. Gan post is nine mechanism families on one label.
ExECT post is per-family transforms plus SF projection.

Do not compare “4 gold families vs 9 Gan posts.” Do not count regexes
as rulesets. A live leftover (Prescription non-ASM / planned-start)
is still post until it is measured and either deleted or documented.
