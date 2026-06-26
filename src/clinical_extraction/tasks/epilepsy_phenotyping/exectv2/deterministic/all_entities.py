"""First deterministic all-entity baseline for ExECTv2.

This module composes the mature SeizureFrequency deterministic extractor with
high-precision rules for the first structured entities named in the GPT-first
strategy: Prescription, Investigations, and Diagnosis. It is intentionally a
transparent floor and candidate source, not a benchmark-complete solution.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    DIAGNOSIS_SURFACE_FORMS,
    PRESCRIPTION_CONCEPT_BY_PHRASE,
    PRESCRIPTION_SURFACE_FORMS,
    BenchmarkConcept,
    attach_benchmark_concept,
    birth_history_concept,
    diagnosis_concept,
    epilepsy_cause_concept,
    investigation_concept,
    onset_concept,
    patient_history_concept,
    when_diagnosed_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    BIRTH_HISTORY,
    DIAGNOSIS,
    EPILEPSY_CAUSE,
    INVESTIGATIONS,
    ONSET,
    PATIENT_HISTORY,
    PRESCRIPTION,
    SEIZURE_FREQUENCY,
    WHEN_DIAGNOSED,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import normalize_phrase

from .mention_identity import dedupe_mentions, match_span
from .pipeline import extract_seizure_frequency
from .rule_metadata import Portability, RuleGroup

ACTIVE_DETERMINISTIC_ENTITIES: tuple[str, ...] = (
    PRESCRIPTION.name,
    INVESTIGATIONS.name,
    DIAGNOSIS.name,
    ONSET.name,
    WHEN_DIAGNOSED.name,
    BIRTH_HISTORY.name,
    EPILEPSY_CAUSE.name,
    PATIENT_HISTORY.name,
    SEIZURE_FREQUENCY.name,
)

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    DRUG_SURFACE_ALIASES, resolve_drug_surface,
)

_OWNER_PREFIX = "deterministic"
_MEDICATION_LEXICON = PRESCRIPTION_CONCEPT_BY_PHRASE
_MEDICATION_PATTERN = re.compile(
    r"\b("
    + "|".join(
        re.escape(name)
        for name in sorted(
            [*PRESCRIPTION_SURFACE_FORMS, *DRUG_SURFACE_ALIASES],
            key=len,
            reverse=True,
        )
    )
    + r")\b",
    re.IGNORECASE,
)
_DOSE_PATTERN = re.compile(
    r"\b(\d+(?:\.\d+)?)\s*(mg|mgs|mgms|milligrams?|milligrammes?|g|grams?)\b",
    re.IGNORECASE,
)
_FREQUENCY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:prn|p\.r\.n\.|as\s+required|when\s+required|as\s+needed|"
            r"rescue|for\s+seizure\s+clusters?)\b",
            re.IGNORECASE,
        ),
        "As_Required",
    ),
    (
        re.compile(
            r"\b(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+aday|"
            r"twice\s+daily|twice\s+today)\b",
            re.IGNORECASE,
        ),
        "2",
    ),
    (
        re.compile(
            r"\b(?:od|o\.d\.|once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|"
            r"nightly|morning|afternoon|evening|am|pm|at\s+night|"
            r"in\s+the\s+(?:morning|afternoon|night|evening)|on|nokte)\b",
            re.IGNORECASE,
        ),
        "1",
    ),
    (re.compile(r"\b(?:tds|t\.d\.s\.|tid|three\s+times\s+(?:a\s+)?day)\b", re.IGNORECASE), "3"),
)
_PRESCRIPTION_NEGATIVE_CONTEXT = re.compile(
    r"\b(?:previously|prior|past|trial(?:s|led)?|tried|not\s+previously\s+taken|"
    r"has\s+not\s+previously\s+taken|discontinued|stopped|withdrawn|allerg(?:y|ic))\b",
    re.IGNORECASE,
)
_PRESCRIPTION_PLAN_CONTEXT = re.compile(
    r"\b(?:commence|start(?:ing)?|increase|increasing|titrate|titration|reduce|"
    r"reducing|target\s+dose|consider|future|option|every\s+(?:two\s+)?weeks|"
    r"every\s+fortnight|until)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_FUTURE_LEFT_CONTEXT = re.compile(
    r"\b(?:should\s+be\s+increased|so\s+that\s+(?:he|she|they)\s+is\s+on|"
    r"suggest\s+adding|suggested\s+adding|suggest\s+introducing|"
    r"suggested\s+introducing|to\s+start\s+treatment\s+with)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_WEIGHT_BASED_CONTEXT = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g|grams?)\s*/?\s*kg(?:\s*/?\s*day)?\b",
    re.IGNORECASE,
)
_PRESCRIPTION_ACTIVE_CONTEXT = re.compile(
    r"\b(?:current|currently|medications?\b:?|antiepileptic|anti-epileptic|"
    r"anti\s+convulsant|anticonvulsant|taking|takes|on|prescribed|regimen|"
    r"continue|remains\s+on|is\s+on|she\s+is\s+on|he\s+is\s+on|rescue)\b",
    re.IGNORECASE,
)
_DOSE_CONNECTOR = re.compile(r"(?:[/,+&]|\band\b|\bplus\b|\bthen\b)\s*$", re.IGNORECASE)
_TRAILING_CONNECTOR = re.compile(r"\s+(?:and|as well as|plus)$", re.IGNORECASE)
_LEFT_DOSE_BEFORE_MEDICATION = re.compile(
    r"(?P<dose>\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|milligrams?|milligrammes?|g|grams?))"
    r"(?:\s+(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+daily|od|o\.d\.|"
    r"once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|nightly|am|pm))?"
    r"\s+of\s+$",
    re.IGNORECASE,
)

_DIAGNOSIS_PATTERN = re.compile(
    r"\b("
    + "|".join(re.escape(name) for name in sorted(DIAGNOSIS_SURFACE_FORMS, key=len, reverse=True))
    + r")\b",
    re.IGNORECASE,
)

_INVESTIGATION_PATTERN = re.compile(r"\b(EEGs?|MRI|CT)(?:\s+(?:brain|scan|head))?\b", re.IGNORECASE)
_RESULT_NORMAL = re.compile(r"\b(?:normal|negative|unremarkable)\b", re.IGNORECASE)
_RESULT_ABNORMAL = re.compile(
    r"\b(?:abnormal|abnormalities|lesion|infarct|sclerosis|dysplasia|"
    r"spike\s+and\s+wave|polyspikes?|epileptiform)\b",
    re.IGNORECASE,
)
_RESULT_UNKNOWN = re.compile(
    r"\b(?:do\s+not\s+have|don't\s+have|not\s+have|not\s+seen|"
    r"await(?:ing)?|pending|unknown|unavailable)\b.{0,80}\b(?:results?|reports?)\b|"
    r"\b(?:results?|reports?)\b.{0,80}\b(?:do\s+not\s+have|don't\s+have|"
    r"not\s+available|unavailable|unknown|pending)\b",
    re.IGNORECASE,
)
_EEG_TYPE_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bsleep\s*deprived\b", re.IGNORECASE), "SleepDeprived"),
    (re.compile(r"\bvideo\s*telemetry\b", re.IGNORECASE), "VideoTelemetry"),
)
_ONSET_AGE_PATTERN = re.compile(
    r"\b(?P<phrase>epilepsy|seizures?)\s+"
    r"(?:first\s+)?(?:started|began|commenced|presented)\s+"
    r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+|when\s+\w+\s+was\s+)?"
    r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
    re.IGNORECASE,
)
_ONSET_SINCE_AGE_PATTERN = re.compile(
    r"\b(?P<phrase>epilepsy|seizures?)\s+"
    r"(?:since|from)\s+(?:the\s+)?(?:age\s+of\s+|age\s+)?"
    r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
    re.IGNORECASE,
)
_ONSET_DURATION_PATTERN = re.compile(
    r"\b(?P<phrase>epilepsy|seizures?)\s+"
    r"(?:first\s+)?(?:started|began|commenced|presented)\s+"
    r"(?:around|approximately|about)?\s*"
    r"(?P<count>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
    r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
    r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b\s+"
    r"(?P<unit>years?|months?)\s+ago\b",
    re.IGNORECASE,
)
_WHEN_DIAGNOSED_TEXT = "epileps"
_WHEN_DIAGNOSED_AGE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\bdiagnosed\s+with\s+epilepsy\s+"
        r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+)?"
        r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bepilepsy\s+was\s+(?:first\s+)?diagnosed\s+"
        r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+)?"
        r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdiagnosis\s+of\s+epilepsy\b.{0,80}?\bwas\s+diagnosed\s+"
        r"(?:at\s+)?(?:the\s+)?(?:age\s+of\s+|age\s+)?"
        r"(?P<age>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\b",
        re.IGNORECASE,
    ),
)
_WHEN_DIAGNOSED_DURATION_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        r"\bdiagnosed\s+with\s+epilepsy\s+(?:around|approximately|about)?\s*"
        r"(?P<count>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\s+"
        r"(?P<unit>years?|months?)\s+ago\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bdiagnosis\s+of\s+epilepsy\s+was\s+made\s+"
        r"(?:around|approximately|about)?\s*"
        r"(?P<count>\d{1,2}|one|two|three|four|five|six|seven|eight|nine|ten|"
        r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|"
        r"nineteen|twenty|twenty[-\s]one|twenty[-\s]two)\s+"
        r"(?P<unit>years?|months?)\s+ago\b",
        re.IGNORECASE,
    ),
)
_MONTHS: dict[str, str] = {
    "january": "1",
    "jan": "1",
    "february": "2",
    "feb": "2",
    "march": "3",
    "mar": "3",
    "april": "4",
    "apr": "4",
    "may": "5",
    "june": "6",
    "jun": "6",
    "july": "7",
    "jul": "7",
    "august": "8",
    "aug": "8",
    "september": "9",
    "sep": "9",
    "sept": "9",
    "october": "10",
    "oct": "10",
    "november": "11",
    "nov": "11",
    "december": "12",
    "dec": "12",
}
_MONTH_PATTERN = "|".join(sorted(_MONTHS, key=len, reverse=True))
_WHEN_DIAGNOSED_DATE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(
        rf"\b(?:diagnosed\s+with\s+epilepsy|epilepsy\s+was\s+diagnosed|"
        rf"diagnosis\s+of\s+(?:his\s+|her\s+)?epilepsy)\s+"
        rf"(?:in\s+|was\s+made\s+in\s+|at\s+the\s+time\s+of\s+)?"
        rf"(?:(?P<month>{_MONTH_PATTERN})\s+)?(?P<year>20\d{{2}}|19\d{{2}})\b",
        re.IGNORECASE,
    ),
)
_BIRTH_HISTORY_RULES: tuple[
    tuple[re.Pattern[str], str, str, dict[str, str]],
    ...
] = (
    (re.compile(r"\bborn\s+normally\b", re.IGNORECASE), "born-normally", "born normally", {}),
    (
        re.compile(r"\bbirth\s+was\s+normal\b", re.IGNORECASE),
        "birth-was-normal",
        "birth was normal",
        {},
    ),
    (re.compile(r"\bnormal\s+birth\b", re.IGNORECASE), "normal-birth", "normal birth", {}),
    (re.compile(r"\bnormal\s+delivery\b", re.IGNORECASE), "normal-delivery", "normal delivery", {}),
    (
        re.compile(r"\bno\s+problems\s+when\s+\w+\s+was\s+born\b", re.IGNORECASE),
        "no-problems-when-he-was-born",
        "born normally",
        {},
    ),
    (re.compile(r"\bfull[-\s]term\b", re.IGNORECASE), "full-term", "full term", {}),
    (
        re.compile(r"\bborn\s+prematurely\s+at\s+32\s+weeks\b", re.IGNORECASE),
        "born-prematurely-at-32-weeks",
        "born prematurely at 32 weeks",
        {"PrematureBirth": "32to<37_ModerateToLatePreterm"},
    ),
    (
        re.compile(r"\bborn\s+slightly\s+premature(?:ly)?\b", re.IGNORECASE),
        "born-slightly-premature",
        "born slightly premature",
        {"PrematureBirth": "34to<37_LatePretermBirth"},
    ),
    (
        re.compile(r"\bborn\s+prematurely\b", re.IGNORECASE),
        "born-prematurely",
        "born prematurely",
        {"PrematureBirth": "34to<37_LatePretermBirth"},
    ),
    (
        re.compile(r"\bperinatal\s+insult\b", re.IGNORECASE),
        "perinatal-insult",
        "perinatal insult",
        {},
    ),
    (
        re.compile(r"\bperinatal\s+trauma\b", re.IGNORECASE),
        "perinatal-trauma",
        "perinatal trauma",
        {},
    ),
    (
        re.compile(r"\bperinatal\s+injury\b", re.IGNORECASE),
        "perinatal-injury",
        "perinatal injury",
        {},
    ),
    (
        re.compile(r"\bperinatal\s+hypoxia\b", re.IGNORECASE),
        "perinatal-hypoxia",
        "perinatal hypoxia",
        {},
    ),
    (
        re.compile(r"\bhypoxia\s+during\s+a\s+difficult\s+birth\b", re.IGNORECASE),
        "hypoxia-during-a-difficult-birth.",
        "hypoxia during a difficult birth",
        {},
    ),
    (
        re.compile(r"\bspecial\s+care\s+baby\s+unit\b", re.IGNORECASE),
        "Special-care-baby-Unit",
        "special care baby unit",
        {},
    ),
)
_EPILEPSY_CAUSE_RULES: tuple[
    tuple[re.Pattern[str], str, str],
    ...
] = (
    (re.compile(r"\bperinatal\s+insult\b", re.IGNORECASE), "perinatal-insult", "perinatal insult"),
    (re.compile(r"\bstroke\b", re.IGNORECASE), "stroke", "stroke"),
    (
        re.compile(r"\btraumatic\s+brain\s+injury\b", re.IGNORECASE),
        "traumatic-brain-injury",
        "traumatic brain injury",
    ),
    (re.compile(r"\bbrain\s+surgery\b", re.IGNORECASE), "brain-surgery", "brain surgery"),
    (re.compile(r"\bcerebral\s+abcess\b", re.IGNORECASE), "cerebral-abcess", "cerebral abcess"),
    (re.compile(r"\bmeningitis\b", re.IGNORECASE), "meningitis", "meningitis"),
    (re.compile(r"\bmeningioma\b", re.IGNORECASE), "meningioma-", "meningioma"),
    (re.compile(r"\bmeasles\b", re.IGNORECASE), "easle", "measles"),
    (
        re.compile(r"\btuberous\s+sclerosis\b", re.IGNORECASE),
        "Tuberous-sclerosis",
        "tuberous sclerosis",
    ),
    (
        re.compile(r"\bperinatal\s+trauma\b", re.IGNORECASE),
        "perinatal-trauma",
        "perinatal trauma",
    ),
    (
        re.compile(r"\bhypoxia\s+during\s+a\s+difficult\s+birth\b", re.IGNORECASE),
        "hypoxia-during-a-difficult-birth.",
        "hypoxia during a difficult birth",
    ),
    (
        re.compile(r"\bherpes\s+encephalitis\b", re.IGNORECASE),
        "herpes-encephalitis",
        "herpes encephalitis",
    ),
    (re.compile(r"\bencephalitis\b", re.IGNORECASE), "encephalitis", "encephalitis"),
    (
        re.compile(r"\bneurocysticercosis\b", re.IGNORECASE),
        "neurocysticercosis",
        "neurocysticercosis",
    ),
    (
        re.compile(r"\bischaemic\s+damage\b", re.IGNORECASE),
        "ischaemic-damage",
        "ischaemic damage",
    ),
)
_PATIENT_HISTORY_RULES: tuple[
    tuple[re.Pattern[str], str, str],
    ...
] = (
    (
        re.compile(r"\bfebrile\s+convulsions?\b", re.IGNORECASE),
        "febrile-convulsions",
        "febrile convulsions",
    ),
    (re.compile(r"\bfebrile\s+seizures?\b", re.IGNORECASE), "febrile-seizures", "febrile seizures"),
    (re.compile(r"\bmyoclonic\s+jerks?\b", re.IGNORECASE), "myoclonic-jerks", "myoclonic jerks"),
    (re.compile(r"\babsences?\b", re.IGNORECASE), "absences", "absences"),
    (re.compile(r"\banxiety\b", re.IGNORECASE), "anxiety", "anxiety"),
    (re.compile(r"\bdepression\b", re.IGNORECASE), "depression", "depression"),
    (re.compile(r"\bmigraines?\b", re.IGNORECASE), "migraine", "migraine"),
    (
        re.compile(r"\bdissociative\s+seizures?\b", re.IGNORECASE),
        "dissociative-seizures",
        "dissociative seizures",
    ),
    (
        re.compile(r"\bnon[-\s]epileptic\s+psychogenic\s+seizures?\b", re.IGNORECASE),
        "non-epileptic-psychogenic-seizures",
        "non epileptic psychogenic seizures",
    ),
    (
        re.compile(r"\bnon[-\s]epileptic\s+attacks?\b", re.IGNORECASE),
        "non-epileptic-attacks",
        "non epileptic attacks",
    ),
    (
        re.compile(r"\btransient\s+loss\s+of\s+consciousness\b", re.IGNORECASE),
        "transient-loss-of-consciousness",
        "transient loss of consciousness",
    ),
    (
        re.compile(r"\bloss\s+of\s+consciousness\b", re.IGNORECASE),
        "loss-of-consciousness",
        "loss of consciousness",
    ),
    (re.compile(r"\bdiabetes\b", re.IGNORECASE), "diabetes", "diabetes"),
    (re.compile(r"\bgliosis\b", re.IGNORECASE), "gliosis", "gliosis"),
    (
        re.compile(r"\bcortical\s+dysplasia\b", re.IGNORECASE),
        "cortical-dysplasia",
        "cortical dysplasia",
    ),
    (
        re.compile(
            r"\b(?:severe\s+|minor\s+)?head\s+injury"
            r"(?:\s+due\s+to\s+an?\s+RTA)?(?:\s+in\s+\d{4})?\b",
            re.IGNORECASE,
        ),
        "head-injury",
        "head injury",
    ),
    (
        re.compile(r"\btraumatic\s+brain\s+injury(?:\s+in\s+\d{4})?\b", re.IGNORECASE),
        "traumatic-brain-injury",
        "traumatic brain injury",
    ),
    (re.compile(r"\bviral\s+meningitis\b", re.IGNORECASE), "meningitis", "viral meningitis"),
    (re.compile(r"\bmeningitis\b", re.IGNORECASE), "meningitis", "meningitis"),
    (
        re.compile(r"\bviral\s+encephalitis\b", re.IGNORECASE),
        "viral-encephalitis",
        "viral encephalitis",
    ),
    (re.compile(r"\bencephalitis\b", re.IGNORECASE), "encephalitis", "encephalitis"),
    (re.compile(r"\bbrain\s+surgery\b", re.IGNORECASE), "brain-surgery", "brain surgery"),
    (
        re.compile(r"\bcerebral\s+ab(?:s|c)cess\b", re.IGNORECASE),
        "cerebral-abcess",
        "cerebral abcess",
    ),
    (re.compile(r"\bhypertension\b", re.IGNORECASE), "hypertension", "hypertension"),
    (
        re.compile(r"\blearning\s+disabilit(?:y|ies)\b", re.IGNORECASE),
        "learning-disabilities",
        "learning disabilities",
    ),
    (
        re.compile(r"\blearning\s+difficult(?:y|ies)\b", re.IGNORECASE),
        "learning-difficulties",
        "learning difficulties",
    ),
    (re.compile(r"\b(?:stroke|CVA)\b", re.IGNORECASE), "stroke", "stroke"),
    (re.compile(r"\bsyncope\b", re.IGNORECASE), "syncope", "syncope"),
    (re.compile(r"\bphotosensitivity\b", re.IGNORECASE), "photosensitivity", "photosensitivity"),
    (
        re.compile(r"\btuberous\s+sclerosis\b", re.IGNORECASE),
        "tuberous-sclerosis",
        "tuberous sclerosis",
    ),
    (re.compile(r"\bmeasles\b", re.IGNORECASE), "measles", "measles"),
    (
        re.compile(r"\bneurocysticercosis\b", re.IGNORECASE),
        "neurocysticercosis",
        "neurocysticercosis",
    ),
    (re.compile(r"\bmeningioma\b", re.IGNORECASE), "meningioma", "meningioma"),
    (
        re.compile(r"\bclusters?\s+of\s+seizures?\b", re.IGNORECASE),
        "cluster-of-seizures",
        "cluster of seizures",
    ),
    (re.compile(r"\bmyoclonus\b", re.IGNORECASE), "myoclonus", "myoclonus"),
)
_NEGATED_PATIENT_HISTORY = re.compile(
    r"\b(?:no|without|denies|denied)\s+(?:prior\s+|past\s+)?(?:history\s+of\s+)?"
    r"[^.:\n;]{0,90}$",
    re.IGNORECASE,
)
_HISTORY_CONTEXT = re.compile(
    r"\b(?:past\s+medical\s+history|past\s+history|history\s+of|comorbidit(?:y|ies)|"
    r"background|diagnos(?:e|i)s|summary|known\s+to\s+suffer|suffered|had|"
    r"with|includes?)\b",
    re.IGNORECASE,
)
_NUMBER_WORDS: dict[str, str] = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "twenty one": "21",
    "twenty-one": "21",
    "twenty two": "22",
    "twenty-two": "22",
}

def extract_deterministic_all9(letter: ExectLetter) -> PredictedLetter:
    """Extract the active deterministic baseline entities from one letter."""

    sf_prediction = extract_seizure_frequency(letter)
    mentions = (
        *_extract_diagnoses(letter.note_text),
        *_extract_investigations(letter.note_text),
        *_extract_onsets(letter.note_text),
        *_extract_when_diagnosed(letter.note_text),
        *_extract_birth_history(letter.note_text),
        *_extract_epilepsy_causes(letter.note_text),
        *_extract_patient_history(letter.note_text),
        *_extract_prescriptions(letter.note_text),
        *sf_prediction.mentions,
    )
    mentions = dedupe_mentions(mentions)
    counts = {
        entity: sum(1 for mention in mentions if mention.entity == entity)
        for entity in ACTIVE_DETERMINISTIC_ENTITIES
    }
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=mentions,
        diagnostics={
            "architecture_track": "rules_only",
            "rule_set": "deterministic_all9_v0_active_structured_plus_sf",
            "active_entities": ACTIVE_DETERMINISTIC_ENTITIES,
            "entity_counts": counts,
            "sf_diagnostics": sf_prediction.diagnostics,
            "rule_families": _rule_family_summary(),
        },
    )


def run_all9_on_letters(letters: Sequence[ExectLetter]) -> list[PredictedLetter]:
    """Run the deterministic active all-entity baseline over letters."""

    return [extract_deterministic_all9(letter) for letter in letters]


def _extract_prescriptions(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    medication_matches = tuple(_MEDICATION_PATTERN.finditer(text))
    for index, match in enumerate(medication_matches):
        if _is_parenthetical_alias(text, match):
            continue
        surface = match.group(1)
        entry = _MEDICATION_LEXICON[resolve_drug_surface(surface)]
        evidence = _prescription_context(text, match, medication_matches[index + 1 :])
        if not _is_prescription_context(text, match, evidence):
            continue
        for attrs, phrase_text in _prescription_attribute_sets(surface, entry, evidence):
            mentions.append(
                PredictedMention(
                    entity=PRESCRIPTION.name,
                    text=phrase_text,
                    attributes=attrs,
                    evidence=evidence,
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "prescription_regimen",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
    return tuple(mentions)


def _prescription_attribute_sets(
    surface: str,
    entry: BenchmarkConcept,
    evidence: str,
) -> tuple[tuple[dict[str, str], str], ...]:
    dose_matches = tuple(_DOSE_PATTERN.finditer(evidence))
    base_attrs = attach_benchmark_concept({}, entry, canonical_key="DrugName")
    rescue_range = re.search(r"\b\d+\s*-\s*\d+\s*(?:mg|mgs|mgms)\b", evidence, re.IGNORECASE)
    if rescue_range and _frequency_from_text(evidence) == "As_Required":
        return (({**base_attrs, "Frequency": "As_Required"}, surface),)
    if not dose_matches:
        frequency = _frequency_from_text(evidence)
        if frequency == "As_Required":
            if _future_plan_before_medication(evidence):
                return ()
            return (({**base_attrs, "Frequency": frequency}, surface),)
        return ()

    slash_schedule_default = "/" in evidence and len(dose_matches) > 1

    items: list[tuple[dict[str, str], str]] = []
    for dose_index, dose in enumerate(dose_matches):
        if evidence[dose.end() : dose.end() + 4].lower().startswith("/kg"):
            continue
        if _PRESCRIPTION_WEIGHT_BASED_CONTEXT.search(evidence):
            continue
        local_right = (
            dose_matches[dose_index + 1].start()
            if dose_index + 1 < len(dose_matches)
            else len(evidence)
        )
        between = evidence[dose.end() : local_right]
        prior_dose_region = evidence[dose_matches[0].end() : dose.start()]
        if dose_index > 0 and _PRESCRIPTION_PLAN_CONTEXT.search(prior_dose_region):
            break
        if dose_index > 0 and not _is_continuing_same_medication_dose(evidence, dose.start()):
            break
        frequency = (
            _frequency_from_text(between)
            or _frequency_from_text(evidence[dose.end() :])
            or ("1" if slash_schedule_default else None)
        )
        if not frequency:
            continue
        unit = _canonical_dose_unit(dose.group(2))
        attrs = {
            **base_attrs,
            "DrugDose": dose.group(1),
            "DoseUnit": unit,
            "Frequency": frequency,
        }
        phrase_text = _trim_planned_regimen_tail(
            _dose_phrase_text(surface, evidence, dose, between)
        )
        if _is_planned_dose_phrase(phrase_text):
            continue
        items.append((attrs, phrase_text))

    return tuple(items)


def _dose_phrase_text(
    surface: str,
    evidence: str,
    dose: re.Match[str],
    between: str,
) -> str:
    left = evidence[: dose.start()]
    if normalize_phrase(surface) in normalize_phrase(left):
        start = max(0, left.lower().rfind(surface.lower()))
    else:
        start = 0
    end = dose.end() + len(between)
    return evidence[start:end].strip(" ,;")


def _trim_planned_regimen_tail(text: str) -> str:
    trimmed = re.split(
        r"\s*(?:\((?:to|please|increase|increasing|reduce|reducing)\b|"
        r"\bincreasing\s+by\b|\breducing\s+by\b)",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return trimmed.strip(" ,;")


def _canonical_dose_unit(unit: str) -> str:
    lowered = unit.lower()
    if lowered.startswith("g"):
        return "g"
    return "mg"


def _is_continuing_same_medication_dose(evidence: str, dose_start: int) -> bool:
    between = evidence[:dose_start]
    last_med = max(
        (match.start() for match in _MEDICATION_PATTERN.finditer(between)),
        default=-1,
    )
    connector_region = between[last_med + 1 if last_med != -1 else 0 :]
    return bool(
        _DOSE_CONNECTOR.search(connector_region)
        or "/" in connector_region[-16:]
        or _frequency_from_text(connector_region[-32:]) is not None
    )


def _is_planned_dose_phrase(phrase_text: str) -> bool:
    lowered = phrase_text.lower()
    if re.search(r"\b\w+\s+to\s+\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g)\b", lowered):
        return True
    if re.search(r"\bshould\s+be\s+\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g)\b", lowered):
        return True
    if re.search(r"\b(?:is\s+)?increased\s+to\s+\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g)\b", lowered):
        return True
    if "increasing after" in lowered or "in steps of" in lowered or "as per plan" in lowered:
        return True
    if "increasing by" in lowered and "," not in lowered:
        return True
    return False


def _is_parenthetical_alias(text: str, match: re.Match[str]) -> bool:
    left = text[max(0, match.start() - 24) : match.start()]
    right = text[match.end() : match.end() + 2]
    if "(" not in left or ")" not in right:
        return False
    return bool(_MEDICATION_PATTERN.search(left))


def _prescription_context(
    text: str,
    match: re.Match[str],
    following_matches: Sequence[re.Match[str]],
) -> str:
    start = _prescription_context_start(text, match)
    tail = text[start:]
    stop = len(tail)
    for separator in ("\n\n", "\n-", "\n", "."):
        idx = tail.find(separator)
        if idx != -1:
            stop = min(stop, idx)
    for next_match in following_matches:
        if next_match.start() <= match.end():
            continue
        if _is_parenthetical_alias(text, next_match):
            continue
        stop = min(stop, next_match.start() - start)
        break
    return _TRAILING_CONNECTOR.sub("", tail[:stop].strip(" ,;")).strip(" ,;")


def _prescription_context_start(text: str, match: re.Match[str]) -> int:
    left = text[max(0, match.start() - 50) : match.start()]
    dose_before = _LEFT_DOSE_BEFORE_MEDICATION.search(left)
    if dose_before:
        return match.start() - (len(left) - dose_before.start("dose"))
    return match.start()


def _is_prescription_context(text: str, match: re.Match[str], evidence: str) -> bool:
    local_left = text[max(0, match.start() - 180) : match.start()]
    sentence_left = text[max(0, text.rfind(".", 0, match.start()) + 1) : match.start()]
    if _PRESCRIPTION_NEGATIVE_CONTEXT.search(sentence_left) and not _active_after_negative_context(
        sentence_left
    ):
        return False
    has_complete_regimen = bool(
        _DOSE_PATTERN.search(evidence)
        and (
            _frequency_from_text(evidence)
            or ("/" in evidence and len(_DOSE_PATTERN.findall(evidence)) > 1)
        )
    )
    has_prn_rescue = _frequency_from_text(evidence) == "As_Required"
    if not (has_complete_regimen or has_prn_rescue):
        return False

    first_dose = _DOSE_PATTERN.search(evidence)
    pre_dose = evidence[: first_dose.start()] if first_dose else evidence
    planned_left = re.search(
        r"\b(?:start(?:ing)?|commence|increase|increasing|titrate|reduce|reducing|"
        r"target|maintenance\s+of|to|by)\s*$",
        local_left,
        re.IGNORECASE,
    )
    planned_prefix = re.search(
        r"\b(?:starting\s+at|commence|start|increase\s+to|titrate|target\s+dose|by)\b",
        pre_dose,
        re.IGNORECASE,
    )
    planned_increment = re.search(
        r"\b(?:increasing|reduce|reducing)\s+by\b|\bevery\s+(?:two\s+)?weeks\b|\bevery\s+fortnight\b",
        evidence,
        re.IGNORECASE,
    )
    active_left = _PRESCRIPTION_ACTIVE_CONTEXT.search(local_left)
    if _PRESCRIPTION_FUTURE_LEFT_CONTEXT.search(local_left):
        return False
    if planned_prefix or planned_left:
        return False
    if planned_increment and not active_left:
        return False
    return True


def _active_after_negative_context(text: str) -> bool:
    negative = list(_PRESCRIPTION_NEGATIVE_CONTEXT.finditer(text))
    if not negative:
        return False
    return _PRESCRIPTION_ACTIVE_CONTEXT.search(text[negative[-1].end() :]) is not None


def _future_plan_before_medication(evidence: str) -> bool:
    first_med = _MEDICATION_PATTERN.search(evidence)
    if first_med is None:
        return False
    return _PRESCRIPTION_FUTURE_LEFT_CONTEXT.search(evidence[: first_med.start()]) is not None


def _legacy_extract_prescriptions(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    for match in _MEDICATION_PATTERN.finditer(text):
        surface = match.group(1)
        entry = _MEDICATION_LEXICON[normalize_phrase(surface)]
        evidence = _right_context_until_separator(text, match.start())
        attrs = attach_benchmark_concept({}, entry, canonical_key="DrugName")
        dose = _DOSE_PATTERN.search(evidence)
        if dose:
            attrs["DrugDose"] = dose.group(1)
            attrs["DoseUnit"] = _canonical_dose_unit(dose.group(2))
        frequency = _frequency_from_text(evidence)
        if frequency:
            attrs["Frequency"] = frequency
        phrase_text = _prescription_phrase_text(surface, evidence, attrs)
        mentions.append(
            PredictedMention(
                entity=PRESCRIPTION.name,
                text=phrase_text,
                attributes=attrs,
                evidence=evidence,
                component_owner=_owner(
                    "prescription_medication",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
    return tuple(mentions)


def _prescription_phrase_text(surface: str, evidence: str, attrs: dict[str, str]) -> str:
    if "DrugDose" in attrs or "Frequency" in attrs:
        return evidence
    return surface


def _extract_investigations(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    for match in _INVESTIGATION_PATTERN.finditer(text):
        modality = _canonical_modality(match.group(1))
        evidence = _sentence_window(text, match.start(), match.end())
        result = _investigation_result(evidence)
        attrs = {f"{modality}_Performed": "Yes"}
        if result:
            attrs[f"{modality}_Results"] = result
        if modality == "EEG":
            eeg_type = _eeg_type(evidence)
            if eeg_type:
                attrs["EEG_Type"] = eeg_type
        concept = investigation_concept(modality, result)
        if concept:
            attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=INVESTIGATIONS.name,
                text=modality,
                attributes=attrs,
                evidence=evidence,
                evidence_span=match_span(match),
                component_owner=_owner(
                    "investigation_result",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
    return tuple(mentions)


def _extract_onsets(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, attr_builder, rule_id in (
        (_ONSET_AGE_PATTERN, _onset_age_attrs, "onset_epilepsy_age"),
        (_ONSET_SINCE_AGE_PATTERN, _onset_age_attrs, "onset_epilepsy_age"),
        (_ONSET_DURATION_PATTERN, _onset_duration_attrs, "onset_epilepsy_duration"),
    ):
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            phrase = _canonical_onset_phrase(match.group("phrase"))
            concept = onset_concept(phrase)
            if concept is None:
                continue
            attrs = attr_builder(match)
            attrs.update({"Certainty": "5", "Negation": "Affirmed"})
            attrs = attach_benchmark_concept(attrs, concept)
            mentions.append(
                PredictedMention(
                    entity=ONSET.name,
                    text=phrase,
                    attributes=attrs,
                    evidence=match.group(0),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        rule_id,
                        RuleGroup.TEMPORAL_ANCHOR,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _extract_when_diagnosed(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for patterns, attr_builder, rule_id in (
        (_WHEN_DIAGNOSED_AGE_PATTERNS, _when_diagnosed_age_attrs, "when_diagnosed_age"),
        (
            _WHEN_DIAGNOSED_DURATION_PATTERNS,
            _when_diagnosed_duration_attrs,
            "when_diagnosed_duration",
        ),
        (_WHEN_DIAGNOSED_DATE_PATTERNS, _when_diagnosed_date_attrs, "when_diagnosed_date"),
    ):
        for pattern in patterns:
            for match in pattern.finditer(text):
                if any(_overlaps(match.span(), span) for span in occupied):
                    continue
                attrs = attr_builder(match)
                attrs.update({"Certainty": "5", "Negation": "Affirmed"})
                attrs = attach_benchmark_concept(attrs, when_diagnosed_concept())
                mentions.append(
                    PredictedMention(
                        entity=WHEN_DIAGNOSED.name,
                        text=_WHEN_DIAGNOSED_TEXT,
                        attributes=attrs,
                        evidence=match.group(0),
                        evidence_span=match_span(match),
                        component_owner=_owner(
                            rule_id,
                            RuleGroup.TEMPORAL_ANCHOR,
                            Portability.CLINICAL_EPILEPSY,
                            Portability.BENCHMARK_FORMAT,
                        ),
                    )
                )
                occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _extract_birth_history(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, mention_text, concept_phrase, extra_attrs in _BIRTH_HISTORY_RULES:
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            concept = birth_history_concept(concept_phrase)
            if concept is None:
                continue
            attrs = {"Certainty": "5", "Negation": "Affirmed", **extra_attrs}
            attrs = attach_benchmark_concept(attrs, concept)
            mentions.append(
                PredictedMention(
                    entity=BIRTH_HISTORY.name,
                    text=mention_text,
                    attributes=attrs,
                    evidence=match.group(0),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "birth_history",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _extract_epilepsy_causes(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, mention_text, concept_phrase in _EPILEPSY_CAUSE_RULES:
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            if not _is_cause_context(text, match):
                continue
            concept = epilepsy_cause_concept(concept_phrase)
            if concept is None:
                continue
            attrs = attach_benchmark_concept(
                {"Certainty": "5", "Negation": "Affirmed"},
                concept,
            )
            mentions.append(
                PredictedMention(
                    entity=EPILEPSY_CAUSE.name,
                    text=mention_text,
                    attributes=attrs,
                    evidence=match.group(0),
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "epilepsy_cause",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _extract_patient_history(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for pattern, mention_text, concept_phrase in _PATIENT_HISTORY_RULES:
        for match in pattern.finditer(text):
            if any(_overlaps(match.span(), span) for span in occupied):
                continue
            if not _is_patient_history_context(text, match):
                continue
            concept = patient_history_concept(concept_phrase)
            if concept is None:
                continue
            evidence = _patient_history_evidence(text, match)
            attrs = _patient_history_attrs(text, match, evidence)
            attrs = attach_benchmark_concept(attrs, concept)
            mentions.append(
                PredictedMention(
                    entity=PATIENT_HISTORY.name,
                    text=mention_text,
                    attributes=attrs,
                    evidence=evidence,
                    evidence_span=match_span(match),
                    component_owner=_owner(
                        "patient_history",
                        RuleGroup.ANCHOR_PHRASE,
                        Portability.CLINICAL_EPILEPSY,
                        Portability.BENCHMARK_FORMAT,
                    ),
                )
            )
            occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _extract_diagnoses(text: str) -> tuple[PredictedMention, ...]:
    mentions: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    matches = sorted(
        _DIAGNOSIS_PATTERN.finditer(text),
        key=lambda m: m.end() - m.start(),
        reverse=True,
    )
    for match in matches:
        if any(_overlaps(match.span(), span) for span in occupied):
            continue
        if _is_diagnosis_phrase_inside_onset_statement(text, match):
            continue
        if _is_diagnosis_phrase_inside_cause_statement(text, match):
            continue
        phrase = match.group(1)
        concept = diagnosis_concept(phrase)
        if concept is None:
            continue
        attrs = {
            "DiagCategory": concept.canonical,
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        attrs = attach_benchmark_concept(attrs, concept)
        mentions.append(
            PredictedMention(
                entity=DIAGNOSIS.name,
                text=phrase,
                attributes=attrs,
                evidence=phrase,
                evidence_span=match_span(match),
                component_owner=_owner(
                    "deterministic_diagnosis_phrase",
                    RuleGroup.ANCHOR_PHRASE,
                    Portability.CLINICAL_EPILEPSY,
                    Portability.BENCHMARK_FORMAT,
                ),
            )
        )
        occupied.append(match.span())
    mentions.sort(key=lambda mention: text.lower().find(mention.evidence.lower()))
    return tuple(mentions)


def _frequency_from_text(text: str) -> str | None:
    for pattern, value in _FREQUENCY_PATTERNS:
        if pattern.search(text):
            return value
    return None


def _investigation_result(text: str) -> str | None:
    if _RESULT_UNKNOWN.search(text):
        return "Unknown"
    if _RESULT_ABNORMAL.search(text):
        return "Abnormal"
    if _RESULT_NORMAL.search(text):
        return "Normal"
    return None


def _eeg_type(text: str) -> str | None:
    for pattern, value in _EEG_TYPE_PATTERNS:
        if pattern.search(text):
            return value
    if re.search(
        r"\b(?:standard|routine)\s+EEG\b|\bsingle\s+burst\s+of\s+"
        r"(?:generalised|generalized)?\s*spike\s+and\s+wave\b",
        text,
        re.IGNORECASE,
    ):
        return "Standard"
    return None


def _onset_age_attrs(match: re.Match[str]) -> dict[str, str]:
    return {"Age": _number_value(match.group("age")), "AgeUnit": "Year"}


def _onset_duration_attrs(match: re.Match[str]) -> dict[str, str]:
    return {
        "NumberOfTimePeriods": _number_value(match.group("count")),
        "TimePeriod": "Month" if match.group("unit").lower().startswith("month") else "Year",
    }


def _when_diagnosed_age_attrs(match: re.Match[str]) -> dict[str, str]:
    return {"Age": _number_value(match.group("age")), "AgeUnit": "Year"}


def _when_diagnosed_duration_attrs(match: re.Match[str]) -> dict[str, str]:
    return {
        "NumberOfTimePeriods": _number_value(match.group("count")),
        "TimePeriod": "Month" if match.group("unit").lower().startswith("month") else "Year",
    }


def _when_diagnosed_date_attrs(match: re.Match[str]) -> dict[str, str]:
    attrs = {"YearDate": match.group("year")}
    month = match.groupdict().get("month")
    if month:
        attrs["MonthDate"] = _MONTHS[month.lower()]
    return attrs


def _patient_history_attrs(
    text: str,
    match: re.Match[str],
    evidence: str,
) -> dict[str, str]:
    attrs = _patient_history_temporal_attrs(evidence)
    if _is_patient_history_negated(text, match):
        return {**attrs, "Certainty": "1", "Negation": "Negated"}
    return {**attrs, "Certainty": "5", "Negation": "Affirmed"}


def _patient_history_temporal_attrs(evidence: str) -> dict[str, str]:
    age_range = re.search(
        r"\b(?:ages?|age\s+of)\s+(?P<low>\d{1,2})\s+(?:and|to|-)\s+(?P<high>\d{1,2})"
        r"\s*(?P<unit>months?|years?)?\b",
        evidence,
        re.IGNORECASE,
    )
    if age_range:
        return {
            "AgeLower": age_range.group("low"),
            "AgeUpper": age_range.group("high"),
            "AgeUnit": _temporal_unit(age_range.group("unit")),
        }
    age = re.search(
        r"\b(?:at\s+)?(?:the\s+)?age\s+of\s+(?P<age>\d{1,2})\s*"
        r"(?P<unit>months?|years?)?\b",
        evidence,
        re.IGNORECASE,
    )
    if age:
        return {
            "Age": age.group("age"),
            "AgeUnit": _temporal_unit(age.group("unit")),
        }
    duration = re.search(
        r"\b(?:for|last|past)\s+(?P<count>\d{1,2})\s+(?P<unit>months?|years?)\b",
        evidence,
        re.IGNORECASE,
    )
    if duration:
        return {
            "NumberOfTimePeriods": duration.group("count"),
            "TimePeriod": _temporal_unit(duration.group("unit")),
        }
    year = re.search(r"\b(?P<year>20\d{2}|19\d{2})\b", evidence)
    if year:
        return {"YearDate": year.group("year")}
    if re.search(r"\bsurgery\b", evidence, re.IGNORECASE):
        return {"PointInTime": "Surgery"}
    return {}


def _temporal_unit(value: str | None) -> str:
    if value and value.lower().startswith("month"):
        return "Month"
    return "Year"


def _number_value(value: str) -> str:
    normalized = value.lower().replace("-", " ").strip()
    return _NUMBER_WORDS.get(normalized, value)


def _canonical_onset_phrase(value: str) -> str:
    lowered = value.lower()
    if lowered.startswith("seizure"):
        return "seizures"
    return "epilepsy"


def _is_diagnosis_phrase_inside_onset_statement(text: str, match: re.Match[str]) -> bool:
    right = text[match.end() : match.end() + 48]
    return bool(
        re.match(
            r"\s+(?:first\s+)?(?:started|began|commenced|presented|since|from)\b",
            right,
            re.IGNORECASE,
        )
    )


def _is_diagnosis_phrase_inside_cause_statement(text: str, match: re.Match[str]) -> bool:
    right = text[match.end() : match.end() + 64]
    return bool(
        re.match(
            r"\s+(?:is\s+)?(?:secondary\s+to|caused\s+by|due\s+to)\b",
            right,
            re.IGNORECASE,
        )
    )


def _is_cause_context(text: str, match: re.Match[str]) -> bool:
    window = _sentence_window(text, match.start(), match.end())
    return bool(
        re.search(
            r"\b(?:epilepsy|seizures?|secondary\s+to|caused\s+by|due\s+to|"
            r"cause\s+of|reason\s+for|previous|probable)\b",
            window,
            re.IGNORECASE,
        )
    )


def _is_patient_history_context(text: str, match: re.Match[str]) -> bool:
    window = _sentence_window(text, match.start(), match.end())
    right = text[match.end() : match.end() + 80]
    if _is_patient_history_negated(text, match):
        return True
    if _HISTORY_CONTEXT.search(window):
        return True
    if re.search(r"\b(?:at\s+the\s+age|age\s+of|in\s+\d{4})\b", right, re.IGNORECASE):
        return True
    return False


def _is_patient_history_negated(text: str, match: re.Match[str]) -> bool:
    left = text[max(0, match.start() - 110) : match.start()]
    return bool(_NEGATED_PATIENT_HISTORY.search(left))


def _patient_history_evidence(text: str, match: re.Match[str]) -> str:
    sentence = _sentence_window(text, match.start(), match.end())
    relative_start = match.start() - _sentence_start(text, match.start())
    local_right = sentence[relative_start:]
    temporal_tail = re.match(
        r"[^.;\n]{0,80}?\b(?:in\s+\d{4}|at\s+the\s+age\s+of\s+\d{1,2}"
        r"(?:\s+(?:and|to|-)\s+\d{1,2})?|for\s+\d{1,2}\s+(?:months?|years?))\b",
        local_right,
        re.IGNORECASE,
    )
    if temporal_tail:
        return temporal_tail.group(0).strip(" ,;")
    return match.group(0)


def _sentence_start(text: str, start: int) -> int:
    return max(text.rfind(".", 0, start), text.rfind("\n", 0, start)) + 1


def _canonical_modality(surface: str) -> str:
    upper = surface.upper()
    if upper.startswith("EEG"):
        return "EEG"
    if upper.startswith("MRI"):
        return "MRI"
    return "CT"


def _right_context_until_separator(text: str, start: int) -> str:
    tail = text[start:]
    stop = len(tail)
    for separator in (" and ", ";", "\n", "."):
        idx = tail.find(separator)
        if idx != -1:
            stop = min(stop, idx)
    return tail[:stop].strip(" ,;")


def _sentence_window(text: str, start: int, end: int) -> str:
    left = max(text.rfind(".", 0, start), text.rfind("\n", 0, start))
    right_candidates = [idx for idx in (text.find(".", end), text.find("\n", end)) if idx != -1]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1 : right].strip(" ,;")


def _overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def _owner(
    rule_id: str,
    group: RuleGroup,
    portability: Portability,
    *extra_portability: Portability,
) -> str:
    parts = [_OWNER_PREFIX, rule_id, group.value, portability.value]
    parts.extend(item.value for item in extra_portability)
    return ":".join(parts)


def _rule_family_summary() -> dict[str, dict[str, str]]:
    return {
        "prescription_medication": {
            "entity": PRESCRIPTION.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "phrase_scope_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "investigation_result": {
            "entity": INVESTIGATIONS.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "diagnosis_phrase": {
            "entity": DIAGNOSIS.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "onset_epilepsy_age": {
            "entity": ONSET.name,
            "group": RuleGroup.TEMPORAL_ANCHOR.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "onset_epilepsy_duration": {
            "entity": ONSET.name,
            "group": RuleGroup.TEMPORAL_ANCHOR.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "when_diagnosed": {
            "entity": WHEN_DIAGNOSED.name,
            "group": RuleGroup.TEMPORAL_ANCHOR.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "phrase_scope_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "birth_history": {
            "entity": BIRTH_HISTORY.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "epilepsy_cause": {
            "entity": EPILEPSY_CAUSE.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
        "patient_history": {
            "entity": PATIENT_HISTORY.name,
            "group": RuleGroup.ANCHOR_PHRASE.value,
            "portability": Portability.CLINICAL_EPILEPSY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
            "temporal_attributes": Portability.CLINICAL_EPILEPSY.value,
        },
        "seizure_frequency": {
            "entity": SEIZURE_FREQUENCY.name,
            "group": "see deterministic.pipeline diagnostics",
            "portability": Portability.SEIZURE_FREQUENCY.value,
            "cui_projection": Portability.BENCHMARK_FORMAT.value,
        },
    }
