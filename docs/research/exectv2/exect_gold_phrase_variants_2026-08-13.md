# ExECT gold phrase variants: why the inventory rules do not belong in the prompt

Date: 2026-08-13  
Status: paper source; development gold only; writing-test passed 2026-08-14  
Parent: [why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md)  
Companion catalog: [every development gold key and its official source phrases](exect_gold_phrase_variant_catalog_2026-08-13.md)  
Workbook: [mention spreadsheet](../artifacts/exect_gold_phrase_variants_2026-08-13.xlsx)  
Artifact: [`experiments/exectv2_gold_phrase_variant_inventory_20260813.json`](../../../experiments/exectv2_gold_phrase_variant_inventory_20260813.json)  
Regenerator: `python scripts/build_exectv2_gold_phrase_variant_inventory.py`  
Sibling: [Gan phrase-variant inventory](gan_gold_phrase_variants_2026-08-13.md)

## The short answer

ExECT gold is four small output dialects and a large, messy input dialect.

On the 140 development letters there are **934 four-family mentions**,
**31 render templates**, and **288 distinct gold keys**. Those keys are
licensed by **335 distinct official source spans**. The scored gold key
itself appears inside the official span on **3 of 934 mentions**. Almost
every scored fact is a transformation, not a copy.

The job is not “pick one current label.” It is **recover the complete
set**: cover the families gold marks as present, leave empty families
empty, keep distinct mentions distinct, and bind attributes. A prompt
could list the aliases, regimen slots, and state templates those spans
require. That is the wrong place to put them.

1. **Cost.** The list is long and family-specific. Most of it is idle on
   any one letter.
2. **Interference.** A letter with one named epilepsy and a clean
   lamotrigine line then sits next to DiagCategory policy, SF state
   projection, brand-to-generic maps, and investigation result assembly.
3. **Opacity.** When the mapping lives in generated prose, a later change
   to a CUIPhrase, a frequency token, or an MRI-result convention is a
   wording edit, not a named stage.
4. **Set assembly.** Enumerating aliases still does not say which facts
   to keep, drop, or split. Forty-one development letters have no
   SeizureFrequency gold. Emitting a rate there is a spurious extra.

The hybrid keeps the two jobs apart. The model reads flexible clinical
language and proposes evidence-linked mentions. Deterministic stages own
the output dialects, the inventory policies, and the record of what
changed.

This draft is ExECT `dev140` only. It is not a performance claim.

## What “exhaustive” means here

| Item | Count | What it is |
| --- | ---: | --- |
| Development letters | 140 | `exectv2_split_v2` `dev` only |
| Four-family mentions | 934 | Diagnosis 405, Prescription 206, SeizureFrequency 187, Investigations 136 |
| Distinct gold keys | 288 | The scored units, including 175 that appear once |
| Distinct render templates | 31 | Family-specific closed shapes |
| Distinct official source spans | 335 | Dataset `raw_text`, hyphen-unfolded for listing |
| Gold key inside the official span | 3 | Near-copy of the scored unit is rare |
| Official span verbatim in the letter | 903 | The usual case; the span is often a short token |
| Official span not in the letter | 26 | Truncation, hyphen markup, or spelling drift |
| Letter span recovered | 934 | Official quote, expanded sentence, or scored sentence |
| Empty-SF letters | 41 | A first-class phenotype: recover other facts, do not invent SF |
| Residual `other_paraphrase` | 0 (0.0%) | Below the 10% review target |

The [existing gold taxonomy](../exectv2/gold_task_taxonomy_2026-08-06.md)
partitions mentions by family subtype (`seizure_free`,
`numeric_cadence_rate`, complete regimen, MRI/EEG/CT). This inventory
answers a different question: **how many different ways does the source
say something that gold then renders as one structured fact?**

Locked `test` letters were not loaded. The official reference is still
the dataset `raw_text` field. Offsets drifted after spelling correction
and are not used. A second pass recovers a letter span: if the official
span occurs in the letter, that span is used, and short tokens are
expanded to the containing sentence; otherwise the pass scores a
justifying sentence (`official_span_expanded_to_sentence`,
`official_reference_in_letter`, `scored_justifying_sentence`). Some
recoveries remain weak; they are labelled rather than silently trusted.
The [workbook](../artifacts/exect_gold_phrase_variants_2026-08-13.xlsx)
has both the official span and the recovered sentence on every mention.

## The output dialect is small

Gold is not free text. It is four closed render languages.

| Family | Mentions | Distinct keys | Templates | What gold actually is |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 405 | 80 | 3 `DiagCategory` shapes | CUIPhrase + Epilepsy / MultipleSeizures / SingleSeizure |
| SeizureFrequency | 187 | 118 | 18 state shapes | Type plus a state (cadence, named window, free, change) |
| Prescription | 206 | 79 | 2 | `drug N unit frequency` or `drug as required` |
| Investigations | 136 | 11 | 4 | `MRI/EEG/CT {result}`, optionally with EEG type |

The long tail is real — 175 keys occur once — but it is still a dialect:
named concepts with a category, typed SF states, slotted regimens, and
modality-result components. A prompt could print the 31 templates. That
would not tell the model how to get there from the letter, or which of
several true mentions to keep.

Diagnosis and Investigations are the most closed. Prescription has only
two templates but 79 distinct keys because dose and frequency vary.
SeizureFrequency looks more open (118 keys) only because type × state
combinations proliferate; the state *shapes* collapse to 18 templates.

## The input dialect is not small

One gold key is licensed by many source constructions. The official span
is often shorter than the scored fact.

### Diagnosis: one concept, several surfaces

`epilepsy (DiagCategory=Epilepsy)` has 95 mentions and **7** official
spans. `generalised tonic clonic seizures (DiagCategory=MultipleSeizures)`
has 34 mentions and **8**:

| Official source span | What has to happen |
| --- | --- |
| `generalised tonic clonic seizures` | Near-copy into the gold concept |
| `GTCS` | Abbreviation → canonical phrase |
| `generalised tonic chronic seizures` / `tonic clinic` / `tonic tonic` | Spelling repair |
| `nocturnal generalised tonic clonic seizures` | Qualifier dropped |
| `epilepsy` | Broader term; gold wants the seizure type, not the syndrome |

`temporal lobe epilepsy` is licensed by `possible TLE`, `temporal lobe`,
and `epilepsy Probable temporal`. Front-matter lines (`Diagnosis: …`)
account for 161 Diagnosis mentions. The concept is often in the letter
(357 / 405 CUIPhrases). The scored unit is not: gold also requires
`DiagCategory`, and sometimes a narrower inventory item than the span
names.

### SeizureFrequency: the span is the type; gold is the state

187 mentions collapse onto 36 type phrases and four subtype buckets
(cadence 66, seizure-free 64, qualitative change 33, named window 24).
The official span is a short type token on 104 mentions. `seizures:
seizure-free` is licensed by `seizures`, `seizure`, `further seizures`,
and `she has had no further seizures`. A cadence example:

| Official source span | Gold |
| --- | --- |
| `seizures` in “seizures every 3 to 4 weeks” | `seizures: 1 per 3 to 4 week` |
| `seizure` next to a 2–4 per month statement | `seizures: 2 to 4 per month` |
| `cluster of seizures` in August 2017 | a dated windowed state, not a Gan two-part cluster label |

Seventy mentions remain `type_token_only`: the official span names the
seizure type and the scored state lives in surrounding language. A
prompt that listed “if the letter says seizures, emit `seizures`” would
miss the state. A prompt that also listed every cadence, since-date, and
“returned / reduced / infrequent” map would be the list this inventory
is trying not to put in the model call.

### Prescription: a small slot language, many renderings

200 of 206 mentions are complete regimens. Six are `as required`.
`lamotrigine 75 mg twice daily` has **9** official spans:

`lamotrigine 75mg bd`, `Lamotrigine 75mg twice a day`, `Lamotrigine
75MG BD (to increase as detailed below)`, a heading line that still
says “to reduce”, and a bare `Lamotrigine` whose dose sits elsewhere.

Brand and spelling aliases are first-class: `Tegretol` → carbamazepine,
`Keppra` → levetiracetam, `zobisamide` → zonisamide, `Epilim` /
`Eplim` → sodium valproate. Titration lines still gold the *current*
dose, not the target.

### Investigations: the span names the test; gold names the finding

`CUIPhrase` is in the letter on only **19 / 136** Investigation
mentions. `MRI abnormal` (26 mentions) is licensed by `MRI`, `MRI
scan`, `MRI brain`, and `MRI 2019 right occipital lobe infarct`. `EEG
abnormal` (41) is licensed by `EEG`, `EEGs`, `EEG abnormalities`, and
`EEG is abnormal`. The output dialect is `MRI/EEG/CT {result}`. The
input dialect is a modality token plus a result that may live a sentence
away.

The [catalog](exect_gold_phrase_variant_catalog_2026-08-13.md) lists
every development gold key and every distinct official span under it.
The [workbook](../artifacts/exect_gold_phrase_variants_2026-08-13.xlsx)
is the mention-level view, including the recovered letter span.

## How similar things are said

The constructions below are mutually exclusive within a family. They are
assigned from the **recovered letter span** when one exists, otherwise
from the official span, in a fixed order, by
`scripts/build_exectv2_gold_phrase_variant_inventory.py`. This is a
review taxonomy, not a change to gold or to the scorer. **0 mentions**
remain `other_paraphrase`. Some recoveries are still weak; they stay
labelled `type_token_only` or `official_span_expanded_to_sentence`
rather than being forced into a tighter class.

| Source construction | n | Family | What the source is doing |
| --- | ---: | --- | --- |
| `canonical_concept_phrase` | 183 | Diagnosis | Official span is, or contains, the gold CUIPhrase |
| `front_matter_diagnosis_line` | 161 | Diagnosis | `Diagnosis:` / `Diagnosis –` line |
| `complete_regimen_line` | 98 | Prescription | Drug, dose, and frequency in the span |
| `finding_in_prose` | 72 | Investigations | Result or finding described around a modality token |
| `type_token_only` | 70 | SeizureFrequency | Official span is the type; state is elsewhere |
| `brand_name` | 62 | Prescription | Epilim, Tegretol, Keppra, Lamictal, spelling aliases |
| `numeric_cadence` | 43 | SeizureFrequency | N per unit, every N, daily / weekly |
| `count_in_named_window` | 38 | SeizureFrequency | Count or range anchored to a date or last visit |
| `dated_investigation` | 27 | Investigations | Last MRI / dated scan |
| `titration_or_future_plan` | 24 | Prescription | Current dose bundled with increase / reduce / start |
| `hedged_or_probable_label` | 21 | Diagnosis | Probable, unclassified, likely |
| `modality_token` | 20 | Investigations | Only MRI / EEG / CT |
| `seizure_free_phrase` | 16 | SeizureFrequency | Seizure-free, no further events, none since |
| `modality_plus_result` | 15 | Investigations | Result word already in the official span |
| `drug_name_only_span` | 11 | Prescription | Just the drug name |
| `qualitative_change` | 10 | SeizureFrequency | Returned, increased, infrequent, reduced |
| `cluster_mention` | 10 | SeizureFrequency | Cluster or run of events |
| `umbrella_or_inventory_mismatch` | 9 | Diagnosis | Broader or different concept than gold |
| Remaining nine constructions | 44 | mixed | Site qualifiers, legacy names, PRN, split dose, truncation |

The same phrase family is not one rule. `epilepsy` can gold as
`epilepsy (DiagCategory=Epilepsy)` or as a more specific type.
`seizures` can gold as seizure-free, a cadence, a named-window count, or
a qualitative change. Those are inventory and state conventions, not
parse failures.

## What must happen between phrase and label

The transform column is the job a prompt-only system would have to
perform in language, on every letter, for every mention in the set.

| Transform | n | Job |
| --- | ---: | --- |
| `identity_or_near_copy` | 315 | Gold concept already in the source |
| `frequency_token_to_count` | 92 | `bd` / twice daily / nocte → Frequency=N |
| `result_word_to_component` | 89 | Result or finding prose → MRI/EEG/CT result |
| `alias_to_canonical_concept` | 72 | Synonym, typo, hedge, or truncation → CUIPhrase |
| `project_state_from_context` | 70 | Type token + nearby language → SF state |
| `brand_to_generic` | 62 | Brand or spelling alias → generic |
| `modality_to_finding_component` | 47 | `MRI` → performed + result |
| `cadence_to_state` | 43 | Every-N or N-per-unit → SF cadence state |
| `windowed_count_to_state` | 38 | Dated or last-visit count → named-window state |
| `current_dose_from_titration_span` | 24 | Titration line still golds the current dose |
| `parse_regimen_slots` | 22 | Line or nearby sentence → drug / dose / unit / frequency |
| `zero_count_to_seizure_free` | 16 | Quiet-interval language → zero-count state |
| `qualitative_change_to_state` | 10 | Returned / reduced → FrequencyChange |
| `cluster_to_windowed_state` | 10 | Cluster mention → dated or windowed SF state |
| `inventory_selection` | 9 | Broader letter term; gold keeps a specific item |
| Remaining four transforms | 15 | PRN, DiagCategory, hyphen unfold, residual |

Three of these are not “say it differently.” They are **inventory
policy**:

- A letter can name epilepsy, a focal type, a historical febrile
  seizure, and a later GTCS. Gold keeps a specific set and assigns
  `DiagCategory`.
- Forty-one letters have no SF gold. A well-formed rate extracted from
  a historical sentence is an extra.
- A titration line can state a current dose and a target. Gold wants
  the current slots, not the plan.

A prompt that enumerated surface forms would still not have enumerated
the winner policy for the *set*. Family ownership and projection stay
with the existing ExECT architecture, not with this inventory.

## Why this is the hybrid argument

The theoretical alternative is: put the 31 templates, the 27
constructions, the transforms, the inventory policies, and a long list
of observed paraphrases into the prompt, and ask the model to apply
them to every family at once.

That alternative fails in the ways this inventory makes concrete.

**It is expensive.** 335 observed official spans on development alone,
288 gold keys, 175 singletons, and four family dialects. A complete
prompt would keep growing as new aliases and dose lines appear. Most of
that text is idle on any given letter.

**It overloads simple cases.** `Diagnosis: Unclassified Epilepsy` →
`epilepsy (DiagCategory=Epilepsy)` is a dialect rewrite. If the same
context also contains SF state projection, brand maps, titration-current
dose policy, and MRI-result assembly, the model is asked to reason about
machinery that this letter may not need.

**It hides the decision.** Diagnosis concept repair, SF
`project_and_gate`, and prescription slot fill are inspectable stages
today. If those mappings live only as prompt paragraphs, a change to
what `bd` means, or to when a modality token may become `mri-abnormal`,
is not a named component.

**It still would not specify the set.** Gan’s winner policy is “one
current label.” ExECT’s is “the complete supported inventory, and
nothing else.” Empty-SF letters, single-seizure versus multiple-seizure
category, and extras that are clinically plausible but not in gold are
set decisions. Listing phrases does not list them.

The hybrid does not make every decision correct. It makes the intended
jobs explicit. Flexible reading stays with the model. The output
dialects, the inventory rules, and the record of the change stay
deterministic.

## How to use this draft

- Use the construction table when writing the ExECT half of the “why
  hybrid” paragraph.
- Use four worked families: Diagnosis `epilepsy` / GTCS aliases, SF
  type-token versus state, Prescription `lamotrigine 75 mg twice daily`,
  and Investigations `MRI abnormal`.
- Use the [workbook](../artifacts/exect_gold_phrase_variants_2026-08-13.xlsx)
  to filter by family, construction, or recovered span.
- Use the [catalog](exect_gold_phrase_variant_catalog_2026-08-13.md)
  when a sentence needs a longer list of official spans.
- Do not cite these counts as model performance, holdout evidence, or
  clinical validation.

## What this draft still needs

- **Weak recoveries.** Residual construction is 0.0%, but some expanded
  sentences still miss the justifying rate or result (a nearby heading
  or type sentence rather than the count). They are labelled, not
  silently trusted.
- **No prompt-length experiment.** The token, latency, and interference
  costs are argued from the size of the dialects. They are not measured
  here as a prompt-ablation result.
- **Nine-entity families are out of scope.** PatientHistory and the
  other five entities stay with the existing gold taxonomy.

## Evidence and limits

Literature and dataset lane: the [task-shape framework](../shared/task_shape_framework_2026-08-06.md)
and [ExECT gold taxonomy](../exectv2/gold_task_taxonomy_2026-08-06.md)
own the task definition. This draft adds a gold-only phrase inventory on
development mentions.

Project lane: [why the proposed method is a model plus recorded rules](why_hybrid_architecture_2026-08-09.md)
owns the architectural claim. Pipeline behaviour stays with
[system architecture](../../canon/01_system_architecture.md) and
[paper provenance](../../canon/10_paper_provenance.md). Decision 0046
still owns the primary four-family comparison.

This draft does not establish that a long prompt would fail, that the
current hybrid is optimal, or that every construction is a clinical
universal. It shows that the mapping from letter language to ExECT gold
is large, structured, family-specific, and mostly not an identity — and
that the remaining job is set assembly, not phrase listing.

## Later writing test

**Question:** can the user show a reader, with actual phrases, why ExECT
cannot treat extraction as “copy the facts out of the letter” and why
enumerating the rest in the prompt is the wrong design?

**Success:** the user can point at the four closed output dialects, the
open input dialect, one Diagnosis alias family, one SF type-token versus
state example, the three prompt-enumeration costs plus set assembly, and
the claim limits, without opening the full technical record.

**Result:** passed 2026-08-14. The four family dialects, the 335 official
spans, Diagnosis `epilepsy` / GTCS aliases, the SF type-token versus
state examples, the three enumeration costs plus set assembly, and the
`dev140` / not-performance limits are all on this page. The catalog and
workbook stay available when a sentence needs a longer list.
