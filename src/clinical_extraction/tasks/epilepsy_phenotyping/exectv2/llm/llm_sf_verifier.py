"""SeizureFrequency-focused verifier over the v0.5 structured key-entity draft."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import merge_rows, pending_items, read_completed
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    _has_blocking_parse_issue,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    score_frequency_state,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_sf_verifier_v0.4"
PIPELINE_FAMILY = "exectv2_llm_sf_verifier"
COMPONENT_OWNER = "llm_sf_verifier"


class ExECTv2SFVerifierSignature(dspy.Signature):
    """Review one clinical letter and a draft SeizureFrequency list."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, draft SF mentions, and rules."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., "
            "\"attributes\": {...}, \"evidence\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspySFVerifier(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2SFVerifierSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


def draft_mentions_by_letter(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    drafts: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        drafts[str(row["letter_id"])] = [
            {
                "text": str(m.get("text", "")),
                "attributes": dict(m.get("attributes") or {}),
                "evidence": str(m.get("evidence", "")),
                "confidence": str(m.get("confidence", "")),
                "rationale": str(m.get("rationale", "")),
            }
            for m in row.get("predicted_mentions", [])
            if m.get("entity") == SEIZURE_FREQUENCY.name
        ]
    return drafts


def read_draft_rows(path: Path | None) -> list[dict[str, Any]]:
    if path is None or not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def build_prompt_input(letter: ExectLetter, draft_mentions: Sequence[Mapping[str, Any]]) -> str:
    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Review the clinical letter and draft SeizureFrequency mentions from "
            "the single structured key-entity extractor. Return the final "
            "SeizureFrequency mentions only. You may keep, delete, edit, or add "
            "mentions, but every final mention must be supported by exact source "
            "evidence."
        ),
        "output_schema": {
            "mentions": [
                {
                    "text": "Clean seizure/event type anchor phrase owned by the verifier.",
                    "attributes": {
                        "NumberOfSeizures": "string count, including 0 for seizure-free",
                        "LowerNumberOfSeizures": "lower bound count",
                        "UpperNumberOfSeizures": "upper bound count",
                        "NumberOfTimePeriods": "period count",
                        "LowerNumberOfTimePeriods": "lower bound period count",
                        "UpperNumberOfTimePeriods": "upper bound period count",
                        "TimePeriod": "Day | Week | Month | Year",
                        "TimeSince_or_TimeOfEvent": "Since | During",
                        "FrequencyChange": (
                            "Decreased | Frequent | Increased | Infrequent | Same"
                        ),
                        "PointInTime": (
                            "Birthday | DrugChange | LastClinic | Last_Month | "
                            "Last_Week | Last_Year | Surgery"
                        ),
                        "DayDate": "day number",
                        "MonthDate": "month number",
                        "YearDate": "year number",
                        "AgeLower": "lower age",
                        "AgeUpper": "upper age",
                        "AgeUnit": "Year | Month",
                    },
                    "evidence": "Exact source substring supporting text and attributes.",
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the decision.",
                }
            ]
        },
        "draft_seizure_frequency_mentions": list(draft_mentions),
        "attribute_vocabulary": _attribute_vocabulary(),
        "clinical_rules": _clinical_rules(),
        "worked_examples": _worked_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _attribute_vocabulary() -> dict[str, Any]:
    spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
    attrs: dict[str, Any] = {}
    for attr in sorted(spec.legal_attributes):
        if attr in {"CUI", "CUIPhrase"}:
            attrs[attr] = "Do not emit this; deterministic projection fills it later."
        elif attr in spec.closed_vocab:
            attrs[attr] = sorted(spec.closed_vocab[attr])
        else:
            attrs[attr] = "string copied or normalized from the letter."
    return attrs


def _clinical_rules() -> list[str]:
    return [
        "Return only SeizureFrequency mentions. Do not emit Diagnosis or Prescription.",
        "Every final evidence value must be an exact substring of the letter.",
        (
            "Text may be a normalized clean seizure/event type anchor phrase even "
            "when the source has a typo. Evidence must remain exact. Example: "
            "source 'tonic chronic seizures' may have text 'tonic clonic seizures'."
        ),
        "Do not emit CUI or CUIPhrase; projection is a deterministic layer.",
        (
            "Clinical headline scoring cares about seizure/event type plus state: "
            "active-rate when a nonzero count/range is present, seizure-free when "
            "NumberOfSeizures is 0, and unknown when only FrequencyChange is present."
        ),
        (
            "Use the clean scored seizure anchor as text, not the numeric or temporal "
            "fragment. For generic seizure rates use text 'seizures' or 'seizure'; "
            "for 'a total of 3 in 2020' in a seizure paragraph use text 'seizures', "
            "not '3 in 2020'."
        ),
        (
            "When a sentence states a generic seizure state change such as "
            "'seizures have returned', emit text 'seizure' or 'seizures' with "
            "FrequencyChange='Increased'."
        ),
        (
            "When one evidence span contains two explicit seizure-free anchors, "
            "such as no further seizures since last clinic and since starting a "
            "drug, emit two generic seizure-free mentions with the same evidence "
            "but different PointInTime values."
        ),
        (
            "Apply a named-seizure-frequency gate. Emit SF only when the evidence "
            "itself gives a named seizure type, generic seizure(s), or seizure-free "
            "state together with a rate, count, last-event/seizure-free target, or "
            "frequency-change word. Do not infer SF from diagnosis text alone."
        ),
        (
            "Do not turn an active historical count into seizure-free just because "
            "the patient currently remains seizure free. Keep the historical active "
            "count and omit current seizure-free unless the source separately gives "
            "a seizure-free duration or point-in-time target annotated by the scheme."
        ),
        (
            "Do not emit a current generic 'seizure free' mention from bare phrases "
            "such as 'remains seizure free' unless the source gives an annotated "
            "duration, date, age range, or point-in-time target."
        ),
        (
            "Never use 'unknown' as NumberOfSeizures, LowerNumberOfSeizures, or "
            "UpperNumberOfSeizures. If there is no count, use a valid "
            "FrequencyChange category or omit the mention."
        ),
        (
            "In a 'last event X. Previous event Y' header, render the last-event "
            "seizure-free state only. Do not add the previous event as an active-rate "
            "mention."
        ),
        (
            "Do not emit a separate generic seizure active-rate for 'last had a "
            "seizure before this around a year ago'; that is a previous-event "
            "reference, not a rate."
        ),
        (
            "For 'several' use NumberOfSeizures='3'; for 'a few' use "
            "NumberOfSeizures='2'."
        ),
        (
            "For 'a few seizures per year', render generic seizures as "
            "NumberOfSeizures='2', NumberOfTimePeriods='1', TimePeriod='Year'."
        ),
        (
            "For every 3 to 4 weeks, render one seizure per 3-4 Week period: "
            "NumberOfSeizures='1', LowerNumberOfTimePeriods='3', "
            "UpperNumberOfTimePeriods='4', TimePeriod='Week'."
        ),
        (
            "Do not deduplicate separately supported SF mentions. If a seizure-type "
            "line and a later narrative repeat the same frequency statement, return "
            "both mentions with separate evidence."
        ),
        (
            "Do not emit SF for a single diagnostic event without ongoing frequency "
            "context, such as 'single focal seizure'."
        ),
        (
            "Do not emit SF for generic episodes, dizzy spells, or aura descriptions "
            "unless a named seizure type and frequency state are explicitly stated."
        ),
        (
            "Do not convert unlabelled 'episodes', 'events', 'blackouts', or 'loss "
            "of consciousness' counts into SeizureFrequency, even if nearby prose "
            "later says they may be seizures."
        ),
        (
            "Do not infer a named seizure type from an unlabelled episodes/events "
            "rate. If the rate sentence says only 'episodes' or 'events', omit it."
        ),
        (
            "Do not emit SF for 'continues to get' a named seizure type when there "
            "is no rate, count, seizure-free target, or frequency-change category."
        ),
        (
            "Do not emit SF for occasional jerks unless the source explicitly names "
            "myoclonic jerks or another scored seizure type."
        ),
        (
            "When the letter says focal seizures are completely under control after "
            "a drug change, render focal seizures with NumberOfSeizures='0' and "
            "PointInTime='DrugChange'."
        ),
        (
            "When the letter says seizures are significantly improved after a drug "
            "change without a count, render generic seizures with "
            "FrequencyChange='Infrequent' and PointInTime='DrugChange'."
        ),
        (
            "When the letter says a patient had a recent named seizure after years "
            "of seizure freedom, keep the recent named seizure as active-rate and "
            "do not replace it with the older seizure-free interval."
        ),
        (
            "When a named seizure-type sentence is followed by 'these seizures' "
            "with a count or range, use text 'seizures' for the generic counted "
            "state if the source wording does not repeat the named type."
        ),
        (
            "When a last-event phrase names focal to bilateral convulsive seizures, "
            "also render the component convulsive seizure seizure-free state if the "
            "letter explicitly supports it."
        ),
        (
            "When a sentence says a patient can get infrequent focal to bilateral "
            "convulsive seizures, render that named seizure type with "
            "FrequencyChange='Infrequent'."
        ),
        (
            "When a sentence says the last seizures were in the teenage years, "
            "render generic seizures as seizure-free since AgeLower='13', "
            "AgeUpper='19', AgeUnit='Year'; do not render the historical count as "
            "a current active-rate fact."
        ),
        (
            "If the evidence phrase is generic 'last seizures were in the teenage "
            "years', use text 'seizures' even when the following clause names a "
            "specific seizure type."
        ),
        "Return exactly one JSON object. No markdown code fences.",
    ]


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "note_fragment": (
                "Seizure type and frequency: seizures every 3 to 4 weeks. "
                "She has seizures every 3 to 4 weeks."
            ),
            "draft": [{"text": "seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "LowerNumberOfTimePeriods": "3",
                        "UpperNumberOfTimePeriods": "4",
                        "TimePeriod": "Week",
                    },
                    "evidence": "seizures every 3 to 4 weeks",
                    "confidence": "high",
                    "rationale": "The seizure-type line states the rate.",
                },
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "LowerNumberOfTimePeriods": "3",
                        "UpperNumberOfTimePeriods": "4",
                        "TimePeriod": "Week",
                    },
                    "evidence": "She has seizures every 3 to 4 weeks",
                    "confidence": "high",
                    "rationale": "The narrative repeats the same independent rate.",
                },
            ],
        },
        {
            "note_fragment": (
                "He had 2 generalised tonic clonic seizures in 2014. "
                "He remains seizure free and is now driving."
            ),
            "draft": [{"text": "seizure free"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "2 generalised tonic clonic seizures in 2014",
                    "confidence": "high",
                    "rationale": "The historical count is the frequency fact.",
                }
            ],
        },
        {
            "note_fragment": (
                "Unfortunately after the period of seizure freedom the seizures "
                "have returned."
            ),
            "draft": [],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {"FrequencyChange": "Increased"},
                    "evidence": "the seizures have returned",
                    "confidence": "medium",
                    "rationale": "Returned seizures are a generic increased-frequency state.",
                }
            ],
        },
        {
            "note_fragment": (
                "She has not had any further seizures since her last clinic "
                "appointment and since starting the lamotrigine."
            ),
            "draft": [{"text": "seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "PointInTime": "LastClinic",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": (
                        "not had any further seizures since her last clinic "
                        "appointment and since starting the lamotrigine"
                    ),
                    "confidence": "high",
                    "rationale": "The sentence explicitly gives last-clinic seizure freedom.",
                },
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "PointInTime": "DrugChange",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": (
                        "not had any further seizures since her last clinic "
                        "appointment and since starting the lamotrigine"
                    ),
                    "confidence": "high",
                    "rationale": (
                        "The same sentence also anchors seizure freedom to treatment "
                        "start."
                    ),
                },
            ],
        },
        {
            "note_fragment": (
                "Seizure type and frequency: 2 generalised tonic clonic seizures "
                "2014, absence like seizures 2014. As you know he had 2 "
                "generalised tonic clonic seizures in 2014."
            ),
            "draft": [{"text": "seizure free"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "2 generalised tonic clonic seizures 2014",
                    "confidence": "high",
                    "rationale": "The header states the historical GTC count.",
                },
                {
                    "text": "absence like seizures",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "absence like seizures 2014",
                    "confidence": "medium",
                    "rationale": "A named historical seizure type without count is one event.",
                },
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "2 generalised tonic clonic seizures in 2014",
                    "confidence": "high",
                    "rationale": "The narrative repeats the same supported GTC count.",
                },
            ],
        },
        {
            "note_fragment": (
                "He has had on average one seizure a year since the age of 17 "
                "but a total of 3 in 2020."
            ),
            "draft": [{"text": "3 in 2020"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "3",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2020",
                    },
                    "evidence": "a total of 3 in 2020",
                    "confidence": "high",
                    "rationale": "The count belongs to generic seizures, not the numeric phrase.",
                },
                {
                    "text": "seizure",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Year",
                        "AgeLower": "17",
                        "AgeUnit": "Year",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": "one seizure a year since the age of 17",
                    "confidence": "high",
                    "rationale": "The earlier clause also gives a generic active rate.",
                },
            ],
        },
        {
            "note_fragment": (
                "Seizure type and frequency: Generalised tonic clonic seizure-last "
                "event July 2016. Previous event December 2015."
            ),
            "draft": [{"text": "Previous event"}],
            "correct": [
                {
                    "text": "Generalised tonic clonic seizure",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "MonthDate": "7",
                        "YearDate": "2016",
                    },
                    "evidence": "Generalised tonic clonic seizure-last event July 2016",
                    "confidence": "high",
                    "rationale": "The previous event is not a separate active-rate fact.",
                }
            ],
        },
        {
            "note_fragment": (
                "Unfortunately he forgot to take carbamazepine last week and had a "
                "generalised tonic clonic seizure. He last had a seizure before "
                "this around a year ago."
            ),
            "draft": [{"text": "seizure before this"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizure",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "PointInTime": "Last_Week",
                        "TimeSince_or_TimeOfEvent": "During",
                    },
                    "evidence": "had a generalised tonic clonic seizure",
                    "confidence": "high",
                    "rationale": "The prior generic event is not a separate rate.",
                }
            ],
        },
        {
            "note_fragment": (
                "She has had a recent generalised tonic chronic seizure at home. "
                "Before the seizure she had been seizure free for 3 years."
            ),
            "draft": [{"text": "seizure free"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizure",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Year",
                    },
                    "evidence": "recent generalised tonic chronic seizure",
                    "confidence": "high",
                    "rationale": "The recent named seizure is the current active-rate fact.",
                }
            ],
        },
        {
            "note_fragment": (
                "It seems as if he is definitely having a few seizures per year."
            ),
            "draft": [{"text": "seizures", "attributes": {"FrequencyChange": "Frequent"}}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Year",
                    },
                    "evidence": "a few seizures per year",
                    "confidence": "high",
                    "rationale": "A few per year maps to two seizures per one year.",
                }
            ],
        },
        {
            "note_fragment": (
                "She did have a cluster of seizures in August, 2017 where she had "
                "6-9 seizures every week for 3 weeks."
            ),
            "draft": [{"text": "cluster of seizures"}],
            "correct": [
                {
                    "text": "cluster of seizures",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "MonthDate": "8",
                        "YearDate": "2017",
                        "TimeSince_or_TimeOfEvent": "During",
                    },
                    "evidence": "cluster of seizures in August, 2017",
                    "confidence": "high",
                    "rationale": "The cluster itself is one event.",
                },
                {
                    "text": "seizures",
                    "attributes": {
                        "LowerNumberOfSeizures": "6",
                        "UpperNumberOfSeizures": "9",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Week",
                        "MonthDate": "8",
                        "YearDate": "2017",
                        "TimeSince_or_TimeOfEvent": "During",
                    },
                    "evidence": "6-9 seizures every week for 3 weeks",
                    "confidence": "high",
                    "rationale": "The same sentence also gives a generic seizure rate.",
                },
            ],
        },
        {
            "note_fragment": (
                "His last seizures were in his teenage years where he probably had "
                "around 3 or 4 focal to bilateral convulsive seizures."
            ),
            "draft": [{"text": "focal to bilateral convulsive seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "AgeLower": "13",
                        "AgeUpper": "19",
                        "AgeUnit": "Year",
                    },
                    "evidence": "His last seizures were in his teenage years",
                    "confidence": "high",
                    "rationale": "Last seizures in teenage years is a seizure-free state.",
                }
            ],
        },
        {
            "note_fragment": (
                "Focal to bilateral convulsive seizures, last event around Christmas "
                "2017. His last one being around Christmas time in 2017."
            ),
            "draft": [{"text": "Focal to bilateral convulsive seizures"}],
            "correct": [
                {
                    "text": "Focal to bilateral convulsive seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "MonthDate": "12",
                        "YearDate": "2017",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": (
                        "Focal to bilateral convulsive seizures, last event around "
                        "Christmas 2017"
                    ),
                    "confidence": "high",
                    "rationale": "The header supplies one supported last-event state.",
                },
                {
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "MonthDate": "12",
                        "YearDate": "2017",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": "last one being around Christmas time in 2017",
                    "confidence": "medium",
                    "rationale": "The narrative supplies another supported last-event state.",
                },
            ],
        },
        {
            "note_fragment": (
                "Focal to bilateral convulsive seizures, last event around Christmas "
                "2017. He can get infrequent focal to bilateral convulsive seizures."
            ),
            "draft": [{"text": "Focal to bilateral convulsive seizures"}],
            "correct": [
                {
                    "text": "Focal to bilateral convulsive seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "MonthDate": "12",
                        "YearDate": "2017",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": (
                        "Focal to bilateral convulsive seizures, last event around "
                        "Christmas 2017"
                    ),
                    "confidence": "high",
                    "rationale": "The header states the last focal-to-bilateral event.",
                },
                {
                    "text": "convulsive seizure",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "YearDate": "2017",
                        "TimeSince_or_TimeOfEvent": "Since",
                    },
                    "evidence": "last convulsive seizure in 2017",
                    "confidence": "medium",
                    "rationale": "The component convulsive seizure is explicitly supported.",
                },
                {
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {"FrequencyChange": "Infrequent"},
                    "evidence": "infrequent focal to bilateral convulsive seizures",
                    "confidence": "medium",
                    "rationale": "Infrequent is a frequency-change state.",
                },
            ],
        },
        {
            "note_fragment": (
                "I think that the focal seizures are completely under control on "
                "lamotrigine 200 mg twice a day."
            ),
            "draft": [{"text": "focal seizures", "attributes": {"FrequencyChange": "Decreased"}}],
            "correct": [
                {
                    "text": "focal seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "PointInTime": "DrugChange",
                    },
                    "evidence": "focal seizures are completely under control",
                    "confidence": "medium",
                    "rationale": (
                        "Completely under control after medication change is "
                        "seizure-free."
                    ),
                }
            ],
        },
        {
            "note_fragment": (
                "This history is consistent with a single focal seizure secondary "
                "to a known stroke."
            ),
            "draft": [{"text": "single focal seizure"}],
            "correct": [],
        },
        {
            "note_fragment": (
                "She has been getting episodes around twice a week of an unusual "
                "thought. I think these are temporal lobe onset focal seizures."
            ),
            "draft": [{"text": "episodes", "attributes": {"NumberOfSeizures": "2"}}],
            "correct": [],
        },
        {
            "note_fragment": (
                "In the last 2 years he developed some minor seizures. The episodes "
                "last no longer than 3 minutes and occur 4 to 5 times a year."
            ),
            "draft": [{"text": "generalised tonic clonic seizures"}],
            "correct": [],
        },
        {
            "note_fragment": (
                "He has had around 7 episodes of loss of consciousness since the "
                "beginning of the year."
            ),
            "draft": [{"text": "episodes of loss of consciousness"}],
            "correct": [],
        },
        {
            "note_fragment": (
                "He has suffered around 10 events in total. He has not had any for "
                "the last 2 weeks."
            ),
            "draft": [{"text": "unwitnessed episodes of loss of consciousness"}],
            "correct": [],
        },
        {
            "note_fragment": (
                "Despite this she continues to get general and complex partial "
                "seizures."
            ),
            "draft": [{"text": "complex partial seizures"}],
            "correct": [],
        },
        {
            "note_fragment": "She still gets occasional jerks with flashing lights.",
            "draft": [{"text": "jerks with flashing lights"}],
            "correct": [],
        },
        {
            "note_fragment": (
                "There has been significant improvement since increasing the dose "
                "of lamotrigine. I think that the focal seizures are completely "
                "under control on the dose of lamotrigine."
            ),
            "draft": [{"text": "focal seizures"}],
            "correct": [
                {
                    "text": "seizures",
                    "attributes": {
                        "FrequencyChange": "Infrequent",
                        "PointInTime": "DrugChange",
                    },
                    "evidence": (
                        "significant improvement since increasing the dose of "
                        "lamotrigine"
                    ),
                    "confidence": "medium",
                    "rationale": "The drug-change improvement supports generic seizures.",
                },
                {
                    "text": "focal seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "PointInTime": "DrugChange",
                    },
                    "evidence": "focal seizures are completely under control",
                    "confidence": "high",
                    "rationale": "Focal seizures are controlled after the drug change.",
                },
            ],
        },
        {
            "note_fragment": (
                "She had approximately 3-4 generalised tonic chronic seizures per "
                "week from May to August. She also had very frequent myoclonic jerks."
            ),
            "draft": [{"text": "generalised tonic chronic seizures"}],
            "correct": [
                {
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "LowerNumberOfSeizures": "3",
                        "UpperNumberOfSeizures": "4",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Week",
                        "TimeSince_or_TimeOfEvent": "During",
                    },
                    "evidence": (
                        "3-4 generalised tonic chronic seizures per week from May "
                        "to August"
                    ),
                    "confidence": "high",
                    "rationale": "The source typo chronic is normalized to clonic.",
                },
                {
                    "text": "myoclonic jerks",
                    "attributes": {"FrequencyChange": "Frequent"},
                    "evidence": "very frequent myoclonic jerks",
                    "confidence": "high",
                    "rationale": "Very frequent is a frequency-change state.",
                },
            ],
        },
    ]


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    note_text: str,
) -> tuple[PredictedLetter, list[str]]:
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    spec = ENTITY_REGISTRY[SEIZURE_FREQUENCY.name]
    for mention in evidence_valid:
        attrs = dict(mention.attributes)
        for key in ("CUI", "CUIPhrase"):
            if key in attrs:
                attrs.pop(key)
                all_warnings.append(
                    f"{SEIZURE_FREQUENCY.name}: "
                    f"dropped_model_supplied_projection_attribute: {key!r}"
                )
        repaired_attrs, attr_warnings = repair_attributes(attrs, spec=spec)
        all_warnings.extend(f"{SEIZURE_FREQUENCY.name}: {warning}" for warning in attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=SEIZURE_FREQUENCY.name,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "pipeline_family": PIPELINE_FAMILY,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


def run_split(
    letters: Sequence[ExectLetter],
    *,
    draft_rows: Sequence[Mapping[str, Any]] = (),
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    program = DspySFVerifier()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    drafts = draft_mentions_by_letter(draft_rows)
    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [r for r in existing_rows if r.get("letter_id") in requested]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        draft_mentions = drafts.get(letter.letter_id, [])
        prompt_input_json = build_prompt_input(letter, draft_mentions)
        raw_output = ""
        call_error: str | None = None
        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
        )
        mentions = extraction.mentions if extraction else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            note_text=letter.note_text,
        )
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "prompt_version": PROMPT_VERSION,
                "pipeline_family": PIPELINE_FAMILY,
                "model": model,
                "mode": mode,
                "draft_mentions": list(draft_mentions),
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_draft_mentions": len(draft_mentions),
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": len(predicted_letter.mentions),
                "n_evidence_invalid": len(mentions) - len(predicted_letter.mentions),
                "predicted_mentions": [_mention_to_row(m) for m in predicted_letter.mentions],
                "gold_mentions": [
                    {"text": a.text, "attributes": dict(a.attributes)}
                    for a in letter.entities(SEIZURE_FREQUENCY.name)
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows)
    return rows, metadata


def summarize_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"examples": 0}
    gold_letters = _reconstruct_gold_letters(rows)
    pred_letters = _reconstruct_pred_letters(rows)
    phrase = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        PHRASE_ONLY,
    )
    semantic = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        semantic_config_for(SEIZURE_FREQUENCY.name),
    )
    benchmark = score_entity(
        gold_letters,
        pred_letters,
        SEIZURE_FREQUENCY.name,
        benchmark_config_for(SEIZURE_FREQUENCY.name),
    )
    source_near = source_near_diagnostic(
        gold_letters,
        pred_letters,
        [SEIZURE_FREQUENCY.name],
        semantic_config_for,
    ).per_entity[SEIZURE_FREQUENCY.name]
    frequency = score_frequency_state(gold_letters, pred_letters)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    return {
        "examples": len(rows),
        "call_failures": sum(bool(r.get("call_error")) for r in rows),
        "parse_failures": sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows),
        "n_draft_mentions": sum(int(r.get("n_draft_mentions", 0)) for r in rows),
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": sum(int(r.get("n_mentions_scored", 0)) for r in rows),
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            (n_mentions_raw - n_evidence_invalid) / n_mentions_raw if n_mentions_raw else 1.0
        ),
        "phrase_only": phrase.model_dump(),
        "semantic": semantic.model_dump(),
        "benchmark": benchmark.model_dump(),
        "source_near": source_near.model_dump(),
        "clinical_recovery": {
            "seizure_frequency": frequency.clinical_headline.model_dump(),
            "active_rate": frequency.active_rate.model_dump(),
            "seizure_free": frequency.seizure_free.model_dump(),
            "unknown": frequency.unknown.model_dump(),
            "target_headline_f1": 0.8,
        },
    }


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    summary = metadata.get("summary", {})
    clinical = summary.get("clinical_recovery", {}).get("seizure_frequency", {})
    source_near = summary.get("source_near", {})
    lines = [
        "# ExECTv2 SeizureFrequency Verifier",
        "",
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version')}`",
        f"- Pipeline family: `{metadata.get('pipeline_family')}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {metadata.get('n_letters')}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Draft SF mentions: {summary.get('n_draft_mentions', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored: {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0):.4f}",
        "",
        "## SeizureFrequency Clinical-Recovery Headline",
        "",
        "| Target F1 | F1 | P | R | TP | FP | FN |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 0.80 | {clinical.get('f1', 0):.3f} | "
            f"{clinical.get('precision', 0):.3f} | {clinical.get('recall', 0):.3f} | "
            f"{clinical.get('tp', 0)} | {clinical.get('fp', 0)} | "
            f"{clinical.get('fn', 0)} |"
        ),
        "",
        "## Source-Near Diagnostic",
        "",
        (
            f"- Overlap F1={source_near.get('overlap', {}).get('f1', 0):.3f} "
            f"R={source_near.get('overlap', {}).get('recall', 0):.3f}"
        ),
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _mention_to_row(mention: PredictedMention) -> dict[str, Any]:
    return {
        "entity": mention.entity,
        "text": mention.text,
        "attributes": dict(mention.attributes),
        "evidence": mention.evidence,
        "confidence": mention.confidence,
        "rationale": mention.rationale,
    }


def _reconstruct_gold_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=SEIZURE_FREQUENCY.name,
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                )
                for m in row.get("gold_mentions", [])
            ),
        )
        for row in rows
    ]


def _reconstruct_pred_letters(rows: Sequence[dict[str, Any]]) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=SEIZURE_FREQUENCY.name,
                    text=str(m["text"]),
                    attributes={str(k): str(v) for k, v in dict(m.get("attributes") or {}).items()},
                    evidence=str(m.get("evidence", "")),
                    confidence=str(m.get("confidence", "medium")),
                    rationale=str(m.get("rationale", "")),
                )
                for m in row.get("predicted_mentions", [])
            ),
        )
        letters.append(to_exect_letter(pred))
    return letters


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    if jsonl_path:
        write_jsonl(rows, jsonl_path)
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "pipeline_family": PIPELINE_FAMILY,
        "model": model,
        "mode": mode,
        "split": split,
        "n_letters": total,
        "summary": summarize_rows(rows),
    }
    if report_path:
        write_report(rows, metadata, report_path, jsonl_path=jsonl_path or Path(""))
    summary = metadata["summary"]
    print(
        json.dumps(
            {
                "processed": len(rows),
                "total": total,
                "call_failures": summary.get("call_failures", 0),
                "parse_failures": summary.get("parse_failures", 0),
                "n_mentions_scored": summary.get("n_mentions_scored", 0),
            },
            sort_keys=True,
        ),
        flush=True,
    )
