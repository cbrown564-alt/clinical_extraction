"""Model-facing GLiNER2 schemas for the adapted ``minimal`` and ``expanded`` conditions.

GLiNER2 cannot generate text, so neither locked schema can be replicated exactly:

* ``minimal`` asks for the native Purist band directly (one classification head) and
  one evidence span, instead of a free-text label in the Gan grammar plus a quotation.
* ``expanded`` adds a span-anchored ``seizure_frequency_finding`` structure to the same
  forward pass. Measurement values are returned as note spans and normalised later by
  format-only code (``normalize.py``); nested unions become flat fields and choices.

Label names are plain language because GLiNER scores label text against the note.
Descriptions follow the Purist band boundaries in ``labels.map_purist``.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal

Condition = Literal["minimal", "expanded"]
CONDITIONS: tuple[Condition, ...] = ("minimal", "expanded")

ANSWER_TASK = "current_seizure_frequency"
EVIDENCE_ENTITY = "current seizure frequency evidence"
FINDING = "seizure_frequency_finding"

# Model-facing label -> (native Purist category, description).
PURIST_LABELS: dict[str, tuple[str, str]] = {
    "currently seizure-free": (
        "currently_no_seizure",
        "The patient is currently seizure-free or no current seizures are reported.",
    ),
    "seizure frequency unknown": (
        "seizure_freq_unknown",
        "The current seizure frequency cannot be established, or the letter gives no "
        "seizure-frequency information.",
    ),
    "about once a year or less": (
        "seizure_freq_1_per_yr",
        "Seizures continue at up to about one per year.",
    ),
    "about once every six months": (
        "seizure_freq_1_per_6mon",
        "Seizures continue at about one every six months.",
    ),
    "between once every six months and once a month": (
        "seizure_freq_more1per6mon_less1mon",
        "More than one seizure per six months but fewer than one per month.",
    ),
    "about once a month": (
        "seizure_freq_1_per_mon",
        "About one seizure per month.",
    ),
    "more than monthly but less than weekly": (
        "seizure_freq_more1mon_less1week",
        "More than one seizure per month but fewer than one per week.",
    ),
    "about once a week": (
        "seizure_freq_1_per_week",
        "About one seizure per week.",
    ),
    "more than weekly but less than daily": (
        "seizure_freq_more1week_less1day",
        "More than one seizure per week but fewer than one per day.",
    ),
    "daily or more": (
        "seizure_freq_1ormore_daily",
        "One or more seizures per day.",
    ),
}
LABEL_TO_PURIST = {label: purist for label, (purist, _) in PURIST_LABELS.items()}
PURIST_TO_LABEL = {purist: label for label, purist in LABEL_TO_PURIST.items()}

EVIDENCE_DESCRIPTION = (
    "The exact wording in the letter that states the patient's current seizure frequency "
    "or current seizure-free status."
)

KINDS = [
    "rate",
    "observed_count",
    "cluster",
    "seizure_free",
    "last_event",
    "median_interval",
    "qualitative",
]
PHASES = ["ongoing", "superseded", "past_or_unclear"]
SCOPES = ["overall", "named", "combined", "unspecified"]
COUNTED_UNITS = [
    "individual_seizure",
    "seizure_day",
    "seizure_night",
    "cluster",
    "cluster_day",
    "not_applicable",
    "status_episode",
]
STATUSES = ["stated", "uncertain"]
LEVELS = ["occasional", "frequent", "not_applicable"]

# A choice field returns the model's highest-scoring choice rather than null.
CHOICE_THRESHOLD = 0.0

# (field, dtype, choices, description). ``evidence`` is first and anchors each record.
FINDING_FIELDS: list[tuple[str, str, list[str] | None, str]] = [
    (
        "evidence",
        "str",
        None,
        "Exact wording stating how often, how many, how long without, or when last the "
        "patient's seizures occurred.",
    ),
    ("event", "str", None, "The letter's words for the counted seizures or events."),
    ("quantity", "str", None, "The stated number, range or bound of events or clusters."),
    ("per", "str", None, "The time unit of a rate or cadence, such as per month or weekly."),
    (
        "window",
        "str",
        None,
        "The window, date or since-anchor the finding refers to, or a seizure-free duration.",
    ),
    ("seizures_per_cluster", "str", None, "The number of seizures within each cluster."),
    ("restriction", "str", None, "A stated limit on which events were counted."),
    ("kind", "str", KINDS, "The measurement kind of the finding."),
    ("phase", "str", PHASES, "Whether the finding describes the patient now."),
    ("scope", "str", SCOPES, "Which seizures the finding counts."),
    ("counted_unit", "str", COUNTED_UNITS, "What one counted unit is."),
    ("status", "str", STATUSES, "Uncertain only when the letter questions the events."),
    ("level", "str", LEVELS, "A qualitative level when no number is given."),
]


def answer_labels() -> dict[str, str]:
    return {label: description for label, (_, description) in PURIST_LABELS.items()}


def schema_dict(condition: Condition) -> dict[str, Any]:
    """Library-neutral description of the schema; hashed into run identities."""
    if condition not in CONDITIONS:
        raise ValueError("Unknown condition")
    result: dict[str, Any] = {
        "classification": {
            "task": ANSWER_TASK,
            "labels": answer_labels(),
        },
        "entities": {EVIDENCE_ENTITY: {"description": EVIDENCE_DESCRIPTION, "dtype": "str"}},
    }
    if condition == "expanded":
        result["structure"] = {
            "name": FINDING,
            "fields": [
                {
                    "name": n,
                    "dtype": d,
                    "choices": c,
                    "description": desc,
                    "threshold": CHOICE_THRESHOLD if c else None,
                }
                for n, d, c, desc in FINDING_FIELDS
            ],
        }
    return result


def schema_sha256(condition: Condition) -> str:
    encoded = json.dumps(schema_dict(condition), sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(encoded).hexdigest()


def build(model: Any, condition: Condition, structure_mode: str | None = None) -> Any:
    """GLiNER2 ``Schema`` for one forward pass holding every task of the condition.

    ``structure_mode`` None keeps the library's legacy record decoding; "natural"
    anchors each record on its evidence span, as fine-tuning data does.
    """
    spec = schema_dict(condition)
    schema = model.create_schema()
    schema.classification(ANSWER_TASK, spec["classification"]["labels"])
    schema.entities(spec["entities"])
    if condition == "expanded":
        builder = (
            schema.structure(FINDING, mode="natural", anchor="evidence")
            if structure_mode == "natural"
            else schema.structure(FINDING)
        )
        for name, dtype, choices, description in FINDING_FIELDS:
            builder = builder.field(
                name,
                dtype=dtype,
                choices=choices,
                description=description,
                threshold=CHOICE_THRESHOLD if choices else None,
            )
    return schema
