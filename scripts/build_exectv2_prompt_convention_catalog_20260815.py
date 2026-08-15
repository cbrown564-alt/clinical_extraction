"""Build the Phase 1/2 ExECT v0.9.24 prompt-convention catalog.

No production rule. No model call. Gold is not read at classify time.
dev140 letter text is used only to mark worked-example wording overlap.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_builders_full import (
    build_full_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_content import (
    _attribute_vocabulary,
    _decision_procedure,
    _event_lane_guide,
    _family_guidance,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_rules_full import (
    _clinical_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.key_entities.loader import (
    load_worked_examples,
)

REPO = Path(__file__).resolve().parents[1]
OUT_JSON = REPO / "experiments" / "exectv2_prompt_convention_catalog_dev140_20260815.json"
DATE = "2026-08-15"
SCHEMA = "exectv2.prompt_convention_catalog.dev140.v1"
PROMPT = "exectv2_hybrid_key_family_event_ledger_v0.9.24"

RULE_SRC = (
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/"
    "pipelines/key_entities_structured/prompt_rules_full.py"
)
EXAMPLE_SRC = (
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/"
    "prompts/key_entities/structured_worked_examples.yaml"
)
CONTENT_SRC = (
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/"
    "pipelines/key_entities_structured/prompt_content.py"
)
BUILDER_SRC = (
    "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/llm/"
    "pipelines/key_entities_structured/prompt_builders_full.py"
)

# family, class, existing, proposed, predicate, apply, phase, notes
RuleMeta = tuple[str, str, str | None, str | None, str | None, str, int | None, str]

RULE_META: dict[int, RuleMeta] = {
    1: ("architecture", "junk", None, None, None, "none", None,
        "Ledger-lane classification. Decision 0015. Do not migrate; drop from v11."),
    2: ("architecture", "junk", None, None, None, "none", None,
        "Candidates-are-not-predictions restatement. Do not migrate."),
    3: ("architecture", "junk", None, None, None, "none", None,
        "Architecture output envelope. Hygiene leftover is rule 84."),
    4: ("architecture", "junk", None, None, None, "none", None,
        "Rationale style. Not a codebook item."),
    5: ("cross_family", "hygiene", None, None, None, "none", None,
        "One event per fact. Stay in v11 contract."),
    6: ("cross_family", "hygiene", None, None, None, "none", None,
        "Exact substring evidence. Stay in v11."),
    7: ("cross_family", "hygiene", None, None, None, "none", None,
        "Exact substring mention text. Stay in v11."),
    8: ("cross_family", "hygiene", None, None, None, "none", None,
        "Named type may be both Diagnosis and SF. Model selection."),
    9: ("cross_family", "hygiene", None, None, None, "none", None,
        "Do not collapse families. Stay in v11."),
    10: ("diagnosis", "hygiene", None,
         "conventions/diagnosis.py heading split (Phase 5 templates)",
         None, "none", None,
         "Compound-clause split is model selection. Heading templates are separate rows."),
    11: ("diagnosis", "encoding",
         "conventions/diagnosis.py diagnosis_convention_attribute_repairs (partial)",
         "conventions/diagnosis.py certainty map",
         "If mention is Diagnosis and Certainty missing and evidence has no hedge, set Certainty=5 and Negation=Affirmed.",
         "rewrite", 3,
         "Closed enum default. Hedge words live in rule 12."),
    12: ("diagnosis", "encoding",
         "conventions/diagnosis.py (partial hedge in mention text)",
         "conventions/diagnosis.py certainty map",
         "If evidence/text has probable|likely → Certainty=4; possible|suspected|query|differential → 3.",
         "rewrite", 3,
         "Guideline hedge table, not clinical judgment of a new event."),
    13: ("diagnosis", "hygiene", None, None, None, "none", None,
         "Prefer specific stated syndrome; emit both when both stated. Model selection."),
    14: ("diagnosis", "encoding",
         "conventions/diagnosis.py surface repairs (TLE/SSFE keep subtype; generic companion incomplete)",
         "conventions/diagnosis.py heading expansion",
         "If heading surface contains the word epilepsy as a stated diagnosis, keep the subtype mention; add generic epilepsy only when the source independently uses that word as a diagnosis.",
         "add", 5,
         "Companion add is high scrutiny. Do not add from clinic names."),
    15: ("diagnosis", "scope",
         "conventions/diagnosis.py is_redundant_diagnosis_residual_addition",
         "conventions/diagnosis.py companion guard",
         "Do not add generic epilepsy when the only source is a specific subtype heading.",
         "drop", 5,
         "Negative of rule 14. Encoding pack should not invent the companion."),
    16: ("diagnosis", "encoding",
         "conventions/diagnosis.py keeps intractable epilepsy surface",
         None,
         "If mention text is generic epilepsy and evidence span is 'intractable epilepsy', rewrite text to the modifier span.",
         "rewrite", 3,
         "Span cleanup of an already-emitted concept."),
    17: ("diagnosis", "scope",
         "conventions/diagnosis.py _GENERAL_AND_COMPLEX_PARTIAL_EVIDENCE",
         "conventions/diagnosis.py",
         "Drop a Diagnosis mention whose text is 'general seizures' when evidence is 'general and complex partial seizures'.",
         "drop", 4,
         "False concept from a modifier."),
    18: ("diagnosis", "scope", None,
         "conventions/diagnosis.py onset-history drop",
         "Drop Diagnosis 'epilepsy' when evidence is onset-history ('epilepsy started at age N') and another current diagnosis mention exists.",
         "drop", 4,
         "Needs gold-free sibling predicate. Not first slice."),
    19: ("diagnosis", "encoding",
         "conventions/diagnosis.py diagnosis_convention_target (hedge strip partial)",
         "conventions/diagnosis.py span cleanup",
         "Strip probable|possible|query|single|alone from Diagnosis mention text; keep Certainty.",
         "rewrite", 3,
         "Span cleanup. Does not invent a concept."),
    20: ("diagnosis", "encoding",
         "conventions/diagnosis.py rewrites 'epilepsy probable focal onset' to one concept; does not split dash headings",
         "conventions/diagnosis.py heading expansion",
         "If a Diagnosis heading is 'epilepsy' + hedge + bare modifier (focal/generalised), emit implied '<modifier> epilepsy' in addition to or instead of the bare modifier.",
         "add", 5,
         "EA0004 hole: epilepsy – probable focal."),
    21: ("diagnosis", "encoding",
         "conventions/diagnosis.py does not split 'focal epilepsy-Probable temporal'",
         "conventions/diagnosis.py heading expansion",
         "If heading matches '<type> epilepsy-Probable <anatomy>', emit type Certainty=5 and '<anatomy> lobe epilepsy' Certainty=4.",
         "add", 5,
         "EA0002. Worked example 03."),
    22: ("diagnosis", "encoding", None,
         "conventions/diagnosis.py heading expansion",
         "If heading is 'Epilepsy - unclassified, possibly <subtype>', emit epilepsy Certainty=5 and '<subtype> epilepsy' Certainty=3.",
         "add", 5,
         "EA0006. Worked example 05."),
    23: ("diagnosis", "hygiene", None, None, None, "none", None,
         "Use exact abbreviation span (JME). Model selection."),
    24: ("diagnosis", "scope",
         "conventions/diagnosis.py DIAGNOSIS_RESIDUAL_CONVENTION_NOISE (partial)",
         "conventions/diagnosis.py NES/blackout drop",
         "Drop Diagnosis if text/evidence is NES, blackout, anxiety, collapse, or LOC and is not asserted as epileptic.",
         "drop", 4,
         "Gold-free class refuse. Not first slice."),
    25: ("diagnosis", "scope", None,
         "conventions/diagnosis.py + sf encoding",
         "Drop Diagnosis or SF if evidence is a negated resemblance ('no events which resemble X').",
         "drop", 4,
         "Cross-family scope. Predicate is the negation cue."),
    26: ("diagnosis", "scope",
         "conventions/diagnosis.py DIAGNOSIS_STANDALONE_NOISE (myoclonic jerks)",
         "conventions/diagnosis.py isolated-symptom drop",
         "Drop Diagnosis whose text is jerks/aura/flashing lights/dizziness unless part of a named seizure type.",
         "drop", 4,
         "Same childhood sentence can remain on SF (EA0010)."),
    27: ("diagnosis", "already_code",
         "conventions/diagnosis.py DIAGNOSIS_SURFACE_CONVENTION_REPAIRS tonic chronic → tonic clonic",
         None,
         "Rewrite tonic chronic → tonic clonic on Diagnosis/SF surfaces.",
         "rewrite", None,
         "Already in surface repairs. Keep as test fixture."),
    28: ("diagnosis", "encoding", None,
         "conventions/diagnosis.py heading expansion",
         "If heading is 'GTCS with myoclonic jerks, possible JME', emit GTCS Diagnosis and JME Certainty=3; do not emit isolated jerks.",
         "add", 5,
         "Add JME + keep GTCS; jerks stay dropped (rule 26)."),
    29: ("diagnosis", "encoding", None,
         "conventions/diagnosis.py heading expansion",
         "If heading is 'X with secondary generalised Y', emit two Diagnosis mentions for the named types.",
         "add", 5,
         "Compound heading split."),
    30: ("diagnosis", "scope",
         "conventions/diagnosis.py residual noise list",
         "conventions/diagnosis.py problem-list guard",
         "A Diagnosis/problem-list header is not enough to keep NES/anxiety/blackout mentions.",
         "drop", 4,
         "Restates 24. One named predicate."),
    31: ("diagnosis", "encoding",
         "conventions/diagnosis.py diagnosis_category_for_concept / DIAGNOSIS_SINGLE_SEIZURE_SURFACES",
         "conventions/diagnosis.py DiagCategory map",
         "Set DiagCategory from surface number: singular named event → SingleSeizure; plural type → MultipleSeizures; syndrome → Epilepsy.",
         "rewrite", 3,
         "Closed enum. Partly present."),
    32: ("diagnosis", "encoding",
         "conventions/diagnosis.py keeps plural surfaces",
         "conventions/diagnosis.py",
         "Do not singularize plural seizure-type mention text.",
         "rewrite", 3,
         "Span hygiene that changes the scored phrase."),
    33: ("seizure_frequency", "encoding", None,
         "deterministic/sf_attribute_encoding.py mention-text cleanup",
         "If SF text is 'seizure frequency' (or contains those words) and evidence contains seizure/seizures, rewrite text to that exact span.",
         "rewrite", 3,
         "EA0154. Priority 6."),
    34: ("seizure_frequency", "hygiene",
         "sf_state_projection empty-attr rejection via state machine",
         None, None, "none", None,
         "Shape constraint, not the codebook. Stay in v11."),
    35: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "Which span is the SF anchor. Model selection."),
    36: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "SF heading recall. Model selection; code may later encode the heading."),
    37: ("seizure_frequency", "encoding",
         "sf_state_projection dated recovery (candidate path only)",
         "deterministic/sf_attribute_encoding.py dated heading completer",
         "If SF mention has YearDate (or MonthDate+YearDate), no count/range/change, and evidence is a type+date heading, set NumberOfSeizures=1 and TimeSince=During.",
         "rewrite", 3,
         "EA0006. Priority 4."),
    38: ("seizure_frequency", "encoding",
         "sf_state_projection _change_attrs",
         "sf_state_projection",
         "If evidence has returned/experienced since a trigger and no count, keep as FrequencyChange/active, not unknown.",
         "rewrite", 3,
         "State assignment on an emitted mention."),
    39: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "Preserve named-type modifiers. Model selection."),
    40: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "Keep full named anchor. Model selection."),
    41: ("seizure_frequency", "scope",
         "sf_state_projection _UNLABELLED_EVENT_RE / convention noise",
         "sf encoding or ownership drop",
         "Drop SF if anchor is NES/blackout/collapse/anxiety and not asserted epileptic.",
         "drop", 4,
         "Not first slice."),
    42: ("seizure_frequency", "scope",
         "sf_state_projection unlabelled-event reject",
         "sf ownership drop",
         "Drop SF whose text is events/episodes/jerks/minor seizures without an epileptic type assertion.",
         "drop", 4,
         "Duplicate of 41 grain. One predicate."),
    43: ("seizure_frequency", "scope",
         "conventions residual noise; hybrid SF path does not drop childhood febrile",
         "sf ownership drop",
         "Drop SF if evidence is childhood febrile, family-history, or previous-event context without a current-state frame.",
         "drop", 4,
         "EA0009/EA0010 febrile."),
    44: ("seizure_frequency", "scope", None,
         "sf ownership drop",
         "Drop SF if evidence is risk/counselling ('at risk of further seizures').",
         "drop", 4,
         "Cue list is gold-free."),
    45: ("seizure_frequency", "scope", None,
         "sf ownership drop",
         "Drop SF if cadence is bound to diagnostically vague 'episodes of an unusual thought' etc.",
         "drop", 4,
         "Needs a closed cue list."),
    46: ("seizure_frequency", "scope", None,
         "sf ownership drop",
         "Drop SF for old contextual episode cadences without a current epileptic type.",
         "drop", 4,
         "Restates 42/45."),
    47: ("seizure_frequency", "scope",
         "sf_state_projection _ONSET_FRAMING_RE",
         "sf_state_projection",
         "Do not treat 'seizures since age N' as a current rate unless the same sentence is a last-seizures-in-age-range free state.",
         "drop", 4,
         "Partial onset framing exists."),
    48: ("seizure_frequency", "encoding", None,
         "deterministic/sf_attribute_encoding.py range splitter",
         "If NumberOfSeizures matches N-M / N to M / N or M, move to Lower/Upper and clear NumberOfSeizures.",
         "rewrite", 3,
         "Priority 1. Guideline encoding."),
    49: ("seizure_frequency", "encoding",
         "statement_parser knows several/few as count tokens (rules-only only)",
         "deterministic/sf_attribute_encoding.py word-number map",
         "If NumberOfSeizures is couple|few|several|two|none|a number|multiple, rewrite to List 11 integer.",
         "rewrite", 3,
         "Guideline List 11. Hybrid does not apply this today. EA0004."),
    50: ("seizure_frequency", "encoding", None,
         "deterministic/sf_attribute_encoding.py interval completer",
         "If evidence matches every N (to M) TimePeriod and NumberOfSeizures is missing, set NumberOfSeizures=1 and period bounds.",
         "rewrite", 3,
         "Priority 2. EA0008, EA0154."),
    51: ("seizure_frequency", "encoding",
         "sf_dated_cluster / cluster helpers (drop extra, not encode one cluster)",
         "sf_attribute_encoding.py cluster-as-one",
         "If evidence counts a cluster and NumberOfSeizures is a per-seizure expansion, rewrite to 1 cluster event with the stated date.",
         "rewrite", 3,
         "Existing cluster helpers are ownership drops, not this encoding."),
    52: ("seizure_frequency", "encoding",
         "sf_state_projection _change_attrs",
         "sf_state_projection",
         "If evidence is qualitative change without a count, keep FrequencyChange only.",
         "rewrite", 3,
         "Partly present on candidate recovery."),
    53: ("seizure_frequency", "encoding",
         "sf_state_projection temporal alignment (partial)",
         "sf_attribute_encoding.py / sf_state_projection",
         "If evidence is a dated count (in March / in 2014) set During + date fields; do not invent TimePeriod=Month.",
         "rewrite", 3,
         "Partial temporal alignment exists."),
    54: ("seizure_frequency", "encoding",
         "sf_state_projection PointInTime LastClinic (partial)",
         "sf_state_projection",
         "If evidence is since last clinic, set TimeSince=Since and PointInTime=LastClinic.",
         "rewrite", 3,
         "Partially present."),
    55: ("seizure_frequency", "encoding",
         "sf_state_projection last-event rewrite requires active-rate and NumberOfSeizures=1",
         "sf_state_projection widen last-event",
         "If evidence is last event / none since / seizure-free since DATE, set NumberOfSeizures=0 and TimeSince=Since even when the model omitted the count.",
         "rewrite", 3,
         "Priority 3. EA0005, EA0133. Do not require model 1."),
    56: ("seizure_frequency", "encoding",
         "same last-event path",
         "sf_state_projection widen last-event",
         "Same predicate as 55; refuse to keep last-event as one seizure During that date.",
         "rewrite", 3,
         "Duplicate of 55 grain. One named rule."),
    57: ("seizure_frequency", "scope", None,
         "sf_state_projection last-event guard",
         "Do not rewrite to 0 from 'last seizure coincided with missing medication' or 'previous seizure was a year ago' without a no-further/since frame.",
         "none", 3,
         "Negative guard on 55. Apply action none (prevents a rewrite)."),
    58: ("seizure_frequency", "encoding",
         "sf_state_projection last-event rewrite already genericizes to seizure/seizures",
         "sf_state_projection",
         "On a seizure-free rewrite, prefer the underlying seizure span in the same sentence when it is an exact substring.",
         "rewrite", 3,
         "Partly present."),
    59: ("seizure_frequency", "scope", None,
         "sf ownership drop",
         "Drop SF if evidence is safety-advice / if-you-have-a-seizure / driving instruction.",
         "drop", 4,
         "Bare driving-SF. Phase 4."),
    60: ("seizure_frequency", "scope",
         "sf_state_projection _seizure_free_reject (partial)",
         "sf ownership drop",
         "Drop bare seizure-free / well-controlled with no type, count, or since/date/drug-change frame.",
         "drop", 4,
         "EA0006 driving companion."),
    61: ("seizure_frequency", "scope", None,
         "sf ownership drop",
         "Restate of 60 with the driving / well-controlled examples.",
         "drop", 4,
         "Collapse into 59/60."),
    62: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "Anaphoric anchors. Model selection; code may later retarget."),
    63: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "Shared count across two types. Model selection."),
    64: ("seizure_frequency", "hygiene", None, None, None, "none", None,
         "At most one SF mention per rate statement. Shape, not codebook."),
    65: ("prescription", "hygiene", None, None, None, "none", None,
         "Mention text is the drug name. Stay in v11."),
    66: ("prescription", "scope",
         "conventions/prescription.py residual future/historical cues (residual-add path only)",
         "conventions/prescription.py current-regimen drop",
         "Drop Prescription if evidence is start/introduce/increase/previous/stopped/if-further and no separate current/taking statement.",
         "drop", 4,
         "Lens currently does not delete planned regimens (measured net-harmful 2026-08-10). Revisit only after Phase 3 remasure."),
    67: ("prescription", "already_code",
         "conventions/prescription.py split_daily_dose_regimen",
         None,
         "If current regimen has unequal once-daily time-of-day doses, split into Frequency=1 mentions.",
         "add", None,
         "Already hooked in PrescriptionDictionaryLens. Keep as test fixture."),
    68: ("prescription", "encoding",
         "conventions/prescription.py does not prefer current 75 over 75 to 125",
         "conventions/prescription.py current-dose vs target range",
         "If DrugDose is '75 to 125' / '75-125' and evidence also states a current single dose, rewrite to the current dose; if the mention is only the target range of a plan, drop (Phase 4).",
         "rewrite", 3,
         "EA0154. Priority 5. Scope half waits for Phase 4."),
    69: ("prescription", "already_code",
         "conventions/shared.py frequency_code + prescription_convention_attribute_repairs",
         None,
         "bd/twice daily → Frequency=2; once daily/mane/nocte → 1.",
         "rewrite", None,
         "Already fills missing Frequency. Keep as test fixture."),
    70: ("prescription", "hygiene", None, None, None, "none", None,
         "Compact regimen list span. Model selection."),
    71: ("investigations", "hygiene", None, None, None, "none", None,
         "One event per modality. Stay in v11."),
    72: ("investigations", "scope",
         "conventions/investigations.py modality filter (ECG not a target key)",
         "conventions/investigations.py ECG exclusion",
         "Drop Investigations whose only evidence is ECG.",
         "drop", 4,
         "Closed exclusion."),
    73: ("investigations", "scope",
         "conventions/investigations.py _PLANNED_INVESTIGATION_EVIDENCE; lens is no-op",
         "conventions/investigations.py pending drop via a named hybrid rule",
         "Drop Investigations if evidence is planned/requested/repeat without a completed result.",
         "drop", 4,
         "Regex exists; default lens does not drop."),
    74: ("investigations", "scope",
         "same planned-test regex",
         "conventions/investigations.py pending drop",
         "Restate of 73. One predicate.",
         "drop", 4,
         "Collapse into 73/75."),
    75: ("investigations", "scope",
         "conventions/investigations.py planned regex (narrower than prompt cue list)",
         "conventions/investigations.py pending-cue list",
         "If evidence contains will/arrange/request/await/appointment/suggest/recommend/chase/not yet/planned and no separate completed result, drop the mention.",
         "drop", 4,
         "EA0154 awaiting appointment. Widen the regex to the prompt cue list."),
    76: ("investigations", "scope",
         "investigation_convention_attribute_repairs strips unsupported Performed=No in some cases; lens is no-op so default path still keeps v10 Performed=No",
         "conventions/investigations.py + named hybrid apply",
         "Never keep an Investigations mention whose only support is a pending cue with Performed=No.",
         "drop", 4,
         "Default lens still kept v10 EEG Performed=No."),
    77: ("investigations", "scope",
         "conventions/investigations.py is_investigation_convention_noise (partial)",
         "conventions/investigations.py",
         "Drop bare modality-only mentions and duplicates of a result-bearing same-modality mention.",
         "drop", 4,
         "Lens does not currently apply the noise predicate."),
    78: ("investigations", "encoding",
         "conventions/investigations.py result cues",
         "conventions/investigations.py",
         "If evidence is 'EEG did/has/does show X', set EEG_Performed=Yes and EEG_Results=Abnormal.",
         "rewrite", 3,
         "Result encoding on an emitted mention."),
    79: ("investigations", "encoding", None,
         "conventions/investigations.py shortest modality text",
         "If mention text is longer than the shortest exact modality phrase present (MRI scan / MRI / EEG / CT), rewrite to that phrase.",
         "rewrite", 3,
         "Span cleanup."),
    80: ("investigations", "encoding", None,
         "conventions/investigations.py EEG_Type guard",
         "Drop EEG_Type unless evidence explicitly says sleep-deprived or video telemetry.",
         "rewrite", 3,
         "Do not default Standard."),
    81: ("cross_family", "hygiene", None, None, None, "none", None,
         "entity+text required; no invented CUI. Stay in v11."),
    82: ("cross_family", "hygiene", None, None, None, "none", None,
         "Do not invent CUI. Stay in v11."),
    83: ("cross_family", "hygiene", None, None, None, "none", None,
         "Empty list when none. Stay in v11."),
    84: ("cross_family", "hygiene", None, None, None, "none", None,
         "One JSON object. Stay in v11."),
}

# family, class, apply, phase, existing, proposed, predicate, notes
ExampleMeta = tuple[str, str, str, int | None, str | None, str | None, str | None, str]

EXAMPLE_META: dict[int, ExampleMeta] = {
    1: ("cross_family", "hygiene", "none", None, None, None, None,
        "Ordinary extraction shape. Test fixture only."),
    2: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_attribute_encoding.py + LastClinic",
        "Count since last clinic → NumberOfSeizures + Since + LastClinic.",
        "Exact EA0002 sentence."),
    3: ("diagnosis", "encoding", "add", 5,
        "conventions/diagnosis.py misses this split",
        "conventions/diagnosis.py heading expansion",
        "focal epilepsy-Probable temporal → two Diagnosis mentions.",
        "EA0002 heading. Why v0.9.24 exactness is not prompt-free."),
    4: ("diagnosis", "encoding", "add", 5,
        "conventions/diagnosis.py misses this split",
        "conventions/diagnosis.py heading expansion",
        "epilepsy - probable focal → epilepsy + focal epilepsy.",
        "EA0004 heading. Campaign trigger."),
    5: ("diagnosis", "encoding", "add", 5, None,
        "conventions/diagnosis.py heading expansion",
        "Epilepsy - unclassified, possibly generalised → epilepsy 5 + generalised epilepsy 3.",
        "EA0006 heading."),
    6: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_attribute_encoding.py dated heading",
        "Named type + year, no count → 1 During.",
        "EA0006-class heading."),
    7: ("seizure_frequency", "encoding", "rewrite", 3,
        "sf_state_projection seizure-free since date (partial)",
        "sf_state_projection",
        "seizure-free since Month Year → 0 + Since + dates.",
        "General encoding shape."),
    8: ("seizure_frequency", "encoding", "rewrite", 3,
        "statement_parser only",
        "sf_attribute_encoding.py word-number",
        "several → 3 + LastClinic.",
        "List 11. General wording."),
    9: ("seizure_frequency", "encoding", "rewrite", 3,
        "statement_parser only",
        "sf_attribute_encoding.py word-number",
        "several → 3 + LastClinic.",
        "EA0004 heading almost verbatim. Prompt leak of the letter."),
    10: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_attribute_encoding.py interval completer",
        "every 3 to 4 weeks → 1 per 3–4 Week.",
        "Exact EA0007 sentence. General interval shape."),
    11: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_attribute_encoding.py dated heading",
        "Two dated 2014 types; second type missing count → 1 During.",
        "EA0006 heading."),
    12: ("seizure_frequency", "encoding", "rewrite", 3,
        "sf_state_projection _change_attrs",
        "sf_state_projection",
        "returned → FrequencyChange=Increased.",
        "EA0008-class."),
    13: ("seizure_frequency", "hygiene", "none", None, None, None, None,
        "Named type + fortnight. Ordinary extraction; fortnight=2 Week is encoding if model misses it."),
    14: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_attribute_encoding.py cluster-as-one",
        "cluster of seizures + date → NumberOfSeizures=1 During.",
        "General."),
    15: ("seizure_frequency", "encoding", "rewrite", 3,
        "sf_state_projection _change_attrs",
        "sf_state_projection",
        "infrequent since DrugChange → FrequencyChange + PointInTime.",
        "General."),
    16: ("seizure_frequency", "encoding", "rewrite", 3,
        "sf_state_projection last-event date recovery (candidate path)",
        "sf_state_projection widen last-event",
        "last event around Christmas 2017 → 0 + Since + Month 12 Year 2017.",
        "EA0011 Christmas wording."),
    17: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_attribute_encoding.py / guideline List 11",
        "completely under control → NumberOfSeizures=0 + Infrequent + DrugChange.",
        "Guideline List 11 'completely under control = 0'."),
    18: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Bare 'remains seizure free and is now driving' → no SF mention.",
        "Exact EA0006 sentence."),
    19: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Historical well-controlled without current frame → drop.",
        "Exact on EA0021 and EA0183."),
    20: ("seizure_frequency", "encoding", "rewrite", 3, None,
        "sf_state_projection widen last-event",
        "last seizures in teenage years → 0 + Since + Age 13–19.",
        "Exact EA0010. Prompt leak of the letter."),
    21: ("cross_family", "hygiene", "none", None, None, None, None,
        "Ordinary 2 per month. Test fixture."),
    22: ("prescription", "hygiene", "none", None, None, None, None,
        "Ordinary current regimen. Test fixture."),
    23: ("prescription", "already_code", "rewrite", None,
        "frequency_code", None,
        "twice a day → Frequency=2.",
        "EA0030 Keppra wording. Already in frequency_code."),
    24: ("prescription", "already_code", "add", None,
        "split_daily_dose_regimen", None,
        "mane/nocte split.",
        "General; example dose pair not found as exact fragment on dev140."),
    25: ("prescription", "scope", "drop", 4,
        "residual future-cue (not applied by default lens)",
        "conventions/prescription.py current-regimen drop",
        "Plan: start / if-further → drop.",
        "General."),
    26: ("diagnosis", "encoding", "rewrite", 3,
        "certainty repairs partial",
        "conventions/diagnosis.py certainty map",
        "probable → Certainty=4; text is the syndrome.",
        "General."),
    27: ("diagnosis", "encoding", "add", 5,
        "generic companion incomplete",
        "conventions/diagnosis.py heading expansion",
        "Temporal lobe epilepsy heading → subtype + generic epilepsy.",
        "Generic heading phrase; several letters use it."),
    28: ("diagnosis", "encoding", "none", 5,
        "conventions/diagnosis.py companion guard (partial)",
        "conventions/diagnosis.py",
        "SSFE heading renders only the subtype.",
        "Negative example for rule 15. Phrase occurs on EA0008/EA0010/EA0186."),
    29: ("diagnosis", "encoding", "rewrite", 3,
        "keeps intractable epilepsy surface",
        None,
        "Keep modifier in mention text.",
        "Exact EA0014 opening."),
    30: ("diagnosis", "encoding", "add", 5, None,
        "conventions/diagnosis.py heading expansion",
        "GTCS + possible JME; do not emit jerks.",
        "Possible-JME phrase also on EA0025/EA0026."),
    31: ("diagnosis", "encoding", "add", 5, None,
        "conventions/diagnosis.py heading expansion",
        "Split compound seizure-type heading.",
        "Heading occurs on EA0021/EA0127/EA0183."),
    32: ("diagnosis", "scope", "drop", 4,
        "_GENERAL_AND_COMPLEX_PARTIAL_EVIDENCE",
        "conventions/diagnosis.py",
        "Do not emit 'general seizures'.",
        "Exact EA0014 sentence."),
    33: ("diagnosis", "encoding", "rewrite", 3, None,
        "conventions/diagnosis.py certainty + span",
        "possible JME → text JME Certainty=3.",
        "General hedge encoding."),
    34: ("diagnosis", "encoding", "rewrite", 3,
        "DIAGNOSIS_SINGLE_SEIZURE_SURFACES",
        "conventions/diagnosis.py",
        "single focal seizure → text without 'single', DiagCategory=SingleSeizure.",
        "EA0016-class."),
    35: ("diagnosis", "scope", "drop", 4,
        "DIAGNOSIS_STANDALONE_NOISE",
        "conventions/diagnosis.py",
        "Jerks and flashing lights are not Diagnosis.",
        "General."),
    36: ("diagnosis", "scope", "drop", 4,
        "DIAGNOSIS_RESIDUAL_CONVENTION_NOISE",
        "conventions/diagnosis.py",
        "Anxiety/blackouts not Diagnosis; epilepsy negated.",
        "General."),
    37: ("investigations", "hygiene", "none", None, None, None, None,
        "Ordinary MRI/EEG results. Test fixture."),
    38: ("investigations", "scope", "drop", 4, None,
        "conventions/investigations.py ECG exclusion",
        "ECG is not a target.",
        "General."),
    39: ("investigations", "encoding", "rewrite", 3, None,
        "conventions/investigations.py EEG_Type guard",
        "Plain EEG abnormal; no EEG_Type.",
        "Exact EA0005 fragment."),
    40: ("investigations", "scope", "drop", 4,
        "planned-test regex",
        "conventions/investigations.py pending drop",
        "Requested future MRI → drop.",
        "General."),
    41: ("investigations", "scope", "drop", 4,
        "planned-test regex",
        "conventions/investigations.py pending drop",
        "Awaiting EEG appointment → drop.",
        "General. EA0154 is the live hole."),
    42: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Driving safety advice → drop.",
        "General."),
    43: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Risk of further seizures → drop.",
        "EA0016-class."),
    44: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Vague thought episodes with cadence → drop.",
        "Exact EA0018 sentence."),
    45: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Contextual episode cadence → drop.",
        "Exact EA0021 and EA0183."),
    46: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "NES/blackouts, no epileptic seizures → empty.",
        "General."),
    47: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Unlabelled events with counts → empty.",
        "General."),
    48: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "LOC episodes → empty.",
        "Exact EA0023 sentence."),
    49: ("seizure_frequency", "scope", "drop", 4, None,
        "sf ownership drop",
        "Light-triggered jerks → empty.",
        "EA0027 distinctive wording."),
}

# Distinctive example → letter paraphrase (not generic medical phrases).
EXAMPLE_OVERLAP_ALLOW: dict[int, list[str]] = {
    2: ["EA0002"],
    3: ["EA0002"],
    4: ["EA0004"],
    5: ["EA0006"],
    6: ["EA0006"],
    9: ["EA0004"],
    10: ["EA0007"],
    11: ["EA0006"],
    13: ["EA0011"],
    16: ["EA0011"],
    18: ["EA0006"],
    19: ["EA0021", "EA0183"],
    20: ["EA0010"],
    23: ["EA0030"],
    29: ["EA0014"],
    31: ["EA0021", "EA0127", "EA0183"],
    32: ["EA0014"],
    39: ["EA0005"],
    44: ["EA0018"],
    45: ["EA0021", "EA0183"],
    48: ["EA0023"],
    49: ["EA0027"],
}


def _flatten(item: str | tuple[str, ...]) -> str:
    return "".join(item) if isinstance(item, tuple) else str(item)


def _overlap(yes: bool, letter_ids: list[str], match_kind: str) -> dict[str, Any]:
    return {
        "yes": yes,
        "letter_ids": letter_ids,
        "match_kind": match_kind,
    }


def _item(
    *,
    item_id: str,
    source_file: str,
    source_kind: str,
    source_index: int | str,
    verbatim_span: str,
    family: str,
    class_: str,
    existing_module: str | None,
    proposed_module: str | None,
    gold_free_predicate_sketch: str | None,
    overlap: dict[str, Any],
    apply_action: str,
    phase: int | None,
    notes: str,
) -> dict[str, Any]:
    return {
        "id": item_id,
        "source_file": source_file,
        "source_kind": source_kind,
        "source_index": source_index,
        "verbatim_span": verbatim_span,
        "family": family,
        "class": class_,
        "existing_module": existing_module,
        "proposed_module": proposed_module,
        "gold_free_predicate_sketch": gold_free_predicate_sketch,
        "dev140_wording_overlap": overlap,
        "apply_action": apply_action,
        "phase": phase,
        "notes": notes,
    }


def _split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.])\s+", text.strip())
    return [p for p in parts if p]


def build_items() -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    dummy = ExectLetter(letter_id="EA0000", note_text="placeholder")
    payload = json.loads(build_full_prompt_input(dummy, prompt_version=PROMPT))

    items.append(
        _item(
            item_id="task-01",
            source_file=BUILDER_SRC,
            source_kind="task",
            source_index=1,
            verbatim_span=payload["task"],
            family="architecture",
            class_="junk",
            existing_module=None,
            proposed_module=None,
            gold_free_predicate_sketch=None,
            overlap=_overlap(False, [], "none"),
            apply_action="none",
            phase=None,
            notes="Mentions candidate_evidence_ledger. v11 task must drop ledger language.",
        )
    )
    architecture = payload["architecture"]
    for key, class_, notes in (
        ("name", "junk", "Internal architecture name. Decision 0015."),
        ("inspiration", "junk", "Gan structured-events discipline. Not a codebook item."),
        (
            "component_ownership",
            "junk",
            "Describes our pipeline. Ledger still misses EA0133 headings.",
        ),
    ):
        items.append(
            _item(
                item_id=f"architecture-{key}",
                source_file=BUILDER_SRC,
                source_kind="architecture",
                source_index=key,
                verbatim_span=str(architecture[key]),
                family="architecture",
                class_=class_,
                existing_module=None,
                proposed_module=None,
                gold_free_predicate_sketch=None,
                overlap=_overlap(False, [], "none"),
                apply_action="none",
                phase=None,
                notes=notes,
            )
        )

    items.append(
        _item(
            item_id="ledger-01",
            source_file=CONTENT_SRC,
            source_kind="candidate_evidence_ledger",
            source_index="mechanism",
            verbatim_span=(
                "candidate_evidence_ledger: per-letter sentence/dictionary cue rows "
                "used as attention scaffolding."
            ),
            family="architecture",
            class_="junk",
            existing_module="prompt_content.candidate_evidence_ledger_for_letter",
            proposed_module=None,
            gold_free_predicate_sketch=None,
            overlap=_overlap(False, [], "none"),
            apply_action="none",
            phase=None,
            notes="Still omits gold headings on EA0133. Do not migrate. Do not keep in v11.",
        )
    )

    for idx, text in enumerate(_decision_procedure(), start=1):
        hygiene = idx == 5
        items.append(
            _item(
                item_id=f"decision-{idx:02d}",
                source_file=CONTENT_SRC,
                source_kind="decision_procedure",
                source_index=idx,
                verbatim_span=text,
                family="architecture",
                class_="hygiene" if hygiene else "junk",
                existing_module=None,
                proposed_module=None,
                gold_free_predicate_sketch=None,
                overlap=_overlap(False, [], "none"),
                apply_action="none",
                phase=None,
                notes=(
                    "Exact-substring check is already rules 6–7. Keep that grain in v11; "
                    "drop the ledger walk."
                    if hygiene
                    else "Ledger keep/reject walk. Decision 0015 junk."
                ),
            )
        )

    for family, rows in _event_lane_guide().items():
        for idx, text in enumerate(rows, start=1):
            items.append(
                _item(
                    item_id=f"lane-{family}-{idx:02d}",
                    source_file=CONTENT_SRC,
                    source_kind="event_lane_guide",
                    source_index=f"{family}.{idx}",
                    verbatim_span=text,
                    family=family if family != "medication" else "prescription",
                    class_="junk",
                    existing_module=None,
                    proposed_module=None,
                    gold_free_predicate_sketch=None,
                    overlap=_overlap(False, [], "none"),
                    apply_action="none",
                    phase=None,
                    notes=(
                        "Lane labels restate scope/encoding items. Collapse into the "
                        "named predicate; do not keep the lane vocabulary in v11."
                    ),
                )
            )

    family_notes = {
        ("medication", 0): ("prescription", "hygiene", "v11 family job: find current ASM events."),
        ("medication", 1): ("prescription", "hygiene", "Closed attribute names, not the value table."),
        ("medication", 2): ("prescription", "hygiene", "Span altitude. Model selection."),
        ("diagnosis", 0): ("diagnosis", "hygiene", "v11 family job: named epileptic concepts."),
        ("diagnosis", 1): ("diagnosis", "hygiene", "Required Diagnosis attributes."),
        ("diagnosis", 2): ("diagnosis", "scope", "NES/vague symptoms. Code if gold-free (Phase 4)."),
        ("diagnosis", 3): ("diagnosis", "encoding", "Hedge in Certainty. Same as rules 12/19."),
        ("seizure_frequency", 0): ("seizure_frequency", "hygiene", "v11 family job: find current SF sentences."),
        ("seizure_frequency", 1): ("seizure_frequency", "scope", "Do not guess a rate; NES out. Encoding vs scope mix."),
        ("investigation", 0): ("investigations", "hygiene", "v11 family job: find completed tests."),
        ("investigation", 1): ("investigations", "scope", "Completed only. Phase 4 pending drop."),
    }
    for family, text in _family_guidance().items():
        for idx, sentence in enumerate(_split_sentences(text)):
            fam, class_, notes = family_notes[(family, idx)]
            apply = "drop" if class_ == "scope" else ("rewrite" if class_ == "encoding" else "none")
            phase = 4 if class_ == "scope" else (3 if class_ == "encoding" else None)
            items.append(
                _item(
                    item_id=f"guidance-{family}-{idx + 1:02d}",
                    source_file=CONTENT_SRC,
                    source_kind="family_guidance",
                    source_index=f"{family}.{idx + 1}",
                    verbatim_span=sentence,
                    family=fam,
                    class_=class_,
                    existing_module=None,
                    proposed_module=None,
                    gold_free_predicate_sketch=None,
                    overlap=_overlap(False, [], "none"),
                    apply_action=apply,
                    phase=phase,
                    notes=notes,
                )
            )

    schema = payload["output_schema"]["clinical_events"][0]
    schema_rows = [
        ("family", schema["family"], "hygiene", "Closed family names."),
        ("anchor_text", schema["anchor_text"], "hygiene", "Exact substring."),
        ("evidence", schema["evidence"], "hygiene", "Exact substring."),
        ("event_state", schema["event_state"], "hygiene", "Source-near scratchpad. Not a codebook."),
        ("mentions.entity", schema["mentions"][0]["entity"], "hygiene", "Closed entity names."),
        ("mentions.text", schema["mentions"][0]["text"], "hygiene", "Exact substring."),
        ("mentions.attributes", schema["mentions"][0]["attributes"], "hygiene", "Legal keys only."),
        ("confidence", schema["confidence"], "hygiene", "Closed confidence names."),
        ("rationale", schema["rationale"], "junk", "Style. Not a convention."),
    ]
    for key, span, class_, notes in schema_rows:
        items.append(
            _item(
                item_id=f"schema-{key.replace('.', '-')}",
                source_file=BUILDER_SRC,
                source_kind="schema_note",
                source_index=key,
                verbatim_span=str(span),
                family="cross_family",
                class_=class_,
                existing_module="contract.entities ENTITY_REGISTRY",
                proposed_module=None,
                gold_free_predicate_sketch=None,
                overlap=_overlap(False, [], "none"),
                apply_action="none",
                phase=None,
                notes=notes,
            )
        )

    vocab = _attribute_vocabulary()
    for entity, attrs in vocab.items():
        family = {
            "Prescription": "prescription",
            "Diagnosis": "diagnosis",
            "SeizureFrequency": "seizure_frequency",
            "Investigations": "investigations",
        }[entity]
        closed = {k: v for k, v in attrs.items() if isinstance(v, list)}
        items.append(
            _item(
                item_id=f"schema-vocab-{entity}",
                source_file=CONTENT_SRC,
                source_kind="schema_note",
                source_index=entity,
                verbatim_span=json.dumps(closed, sort_keys=True),
                family=family,
                class_="hygiene",
                existing_module="contract.entities ENTITY_REGISTRY",
                proposed_module=None,
                gold_free_predicate_sketch=None,
                overlap=_overlap(False, [], "none"),
                apply_action="none",
                phase=None,
                notes=(
                    "v11 may keep closed *names* of attributes. Value tables "
                    "(several=3, Certainty hedge) are code, not prompt."
                ),
            )
        )
    items.append(
        _item(
            item_id="schema-vocab-CUI",
            source_file=CONTENT_SRC,
            source_kind="schema_note",
            source_index="CUI",
            verbatim_span=vocab["Diagnosis"]["CUI"],
            family="cross_family",
            class_="hygiene",
            existing_module=None,
            proposed_module=None,
            gold_free_predicate_sketch=None,
            overlap=_overlap(False, [], "none"),
            apply_action="none",
            phase=None,
            notes="Do not invent CUI. Stay in v11.",
        )
    )

    rules = [_flatten(r) for r in _clinical_rules()]
    if len(rules) != 84:
        raise RuntimeError(f"expected 84 clinical rules, got {len(rules)}")
    if set(RULE_META) != set(range(1, 85)):
        raise RuntimeError("RULE_META must cover 1..84")
    for idx, span in enumerate(rules, start=1):
        family, class_, existing, proposed, predicate, apply, phase, notes = RULE_META[idx]
        items.append(
            _item(
                item_id=f"rule-{idx:02d}",
                source_file=RULE_SRC,
                source_kind="clinical_rule",
                source_index=idx,
                verbatim_span=span,
                family=family,
                class_=class_,
                existing_module=existing,
                proposed_module=proposed,
                gold_free_predicate_sketch=predicate,
                overlap=_overlap(False, [], "none"),
                apply_action=apply,
                phase=phase,
                notes=notes,
            )
        )

    examples = load_worked_examples()
    if len(examples) != 49:
        raise RuntimeError(f"expected 49 worked examples, got {len(examples)}")
    if set(EXAMPLE_META) != set(range(1, 50)):
        raise RuntimeError("EXAMPLE_META must cover 1..49")
    for idx, example in enumerate(examples, start=1):
        family, class_, apply, phase, existing, proposed, predicate, notes = EXAMPLE_META[idx]
        letters = EXAMPLE_OVERLAP_ALLOW.get(idx, [])
        overlap = (
            _overlap(True, letters, "dev140_paraphrase")
            if letters
            else _overlap(False, [], "none")
        )
        items.append(
            _item(
                item_id=f"example-{idx:02d}",
                source_file=EXAMPLE_SRC,
                source_kind="worked_example",
                source_index=idx,
                verbatim_span=str(example.get("note_fragment") or ""),
                family=family,
                class_=class_,
                existing_module=existing,
                proposed_module=proposed,
                gold_free_predicate_sketch=predicate,
                overlap=overlap,
                apply_action=apply,
                phase=phase,
                notes=notes,
            )
        )
    return items


def _decision_0040_map(items: list[dict[str, Any]]) -> dict[str, Any]:
    encoding_scope = [
        item
        for item in items
        if item["class"] in {"encoding", "scope", "already_code"}
        and item["source_kind"] in {"clinical_rule", "worked_example", "family_guidance"}
    ]
    by_action: dict[str, list[str]] = {"rewrite": [], "drop": [], "add": [], "none": []}
    for item in encoding_scope:
        by_action[item["apply_action"]].append(item["id"])
    return {
        "note": (
            "Decision 0040: rewrite of an emitted model mention is preferred; "
            "drop of an emitted mention is next; add of a new mention is heading "
            "split only, with fact_origin/component_owner distinct from the model. "
            "Do not import the standalone rules-only extractor."
        ),
        "rewrite_ids": by_action["rewrite"],
        "drop_ids": by_action["drop"],
        "add_ids": by_action["add"],
        "no_apply_ids": by_action["none"],
        "counts": {key: len(val) for key, val in by_action.items()},
    }


def main() -> None:
    letters = load_letters_for_split("dev")
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 dev letters, got {len(letters)}")
    items = build_items()
    classes = Counter(item["class"] for item in items)
    families = Counter(item["class"] for item in items if item["source_kind"] == "clinical_rule")
    example_overlap = [
        item["id"]
        for item in items
        if item["source_kind"] == "worked_example" and item["dev140_wording_overlap"]["yes"]
    ]
    artifact = {
        "schema_version": SCHEMA,
        "date": DATE,
        "prompt_version": PROMPT,
        "split": "dev140",
        "row_policy": "dev140_letter_text_for_example_overlap_only; test60_forbidden; gold_not_read_at_classify_time",
        "model_calls": 0,
        "campaign": "docs/plans/exect_prompt_convention_migration_2026-08-15.md",
        "guideline_source": (
            "docs/research/exectv2/annotation_guidelines_v9_extracted.md List 11"
        ),
        "sources": [RULE_SRC, EXAMPLE_SRC, CONTENT_SRC, BUILDER_SRC],
        "summary": {
            "n_items": len(items),
            "n_clinical_rules": 84,
            "n_worked_examples": 49,
            "by_class": dict(classes),
            "clinical_rules_by_class": dict(families),
            "worked_examples_with_dev140_paraphrase": example_overlap,
        },
        "decision_0040_map": _decision_0040_map(items),
        "items": items,
    }
    OUT_JSON.write_text(json.dumps(artifact, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT_JSON} items={len(items)} classes={dict(classes)}")
    print(f"dev140 paraphrase examples={example_overlap}")


if __name__ == "__main__":
    main()
