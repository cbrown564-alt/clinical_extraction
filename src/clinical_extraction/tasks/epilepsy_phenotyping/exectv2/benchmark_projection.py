"""Shared benchmark-format projection helpers for ExECTv2.

This module owns finite CUI/CUIPhrase lookup for the active ExECTv2 entity
engines. The lookup is intentionally benchmark-format projection: it attaches
ontology-shaped attributes after a clinical fact has already been selected, and
it returns no projection for unknown phrases rather than guessing.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    resolve_drug_surface,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    assign_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
@dataclass(frozen=True)
class BenchmarkConcept:
    """Benchmark-facing concept projection for one extracted clinical mention."""

    canonical: str
    cui: str
    cui_phrase: str


_PRESCRIPTION_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (BenchmarkConcept("lamotrigine", "C0064636", "lamotrigine"), ("lamotrigine",)),
    (BenchmarkConcept("lamictal", "C0678180", "lamictal"), ("lamictal",)),
    (BenchmarkConcept("levetiracetam", "C0377265", "levetiracetam"), ("levetiracetam",)),
    (BenchmarkConcept("keppra", "C0876060", "keppra"), ("keppra",)),
    (
        BenchmarkConcept("sodium-valproate", "C0037567", "sodium-valproate"),
        (
            "sodium valproate",
            "sodium-valproate",
            "sodiumvalproate",
            "valproate",
            "episenta",
        ),
    ),
    (BenchmarkConcept("epilim", "C0591451", "epilim"), ("epilim", "eplim")),
    (
        BenchmarkConcept("epilim-chrono", "C0591452", "epilim-chrono"),
        ("epilim chrono", "epilim-chrono"),
    ),
    (BenchmarkConcept("carbamazepine", "C0006949", "carbamazepine"), ("carbamazepine",)),
    (BenchmarkConcept("tegretol", "C0700087", "tegretol"), ("tegretol", "tegretaol")),
    (
        BenchmarkConcept("zonisamide", "C0078844", "zonisamide"),
        ("zonisamide", "zobisamide", "zonismaide"),
    ),
    (BenchmarkConcept("clobazam", "C0055891", "clobazam"), ("clobazam",)),
    (
        BenchmarkConcept("brivaracetam", "C1699861", "brivaracetam"),
        ("brivaracetam", "brivitiracetam", "brivetiracetam"),
    ),
    (BenchmarkConcept("topiramate", "C0076829", "topiramate"), ("topiramate",)),
    (BenchmarkConcept("perampanel", "C2698764", "perampanel"), ("perampanel",)),
    (BenchmarkConcept("phenytoin", "C0031507", "phenytoin"), ("phenytoin",)),
    (
        BenchmarkConcept("phenobarbital", "C0031412", "phenobarbitone"),
        ("phenobarbital", "phenobarbitone"),
    ),
    (
        BenchmarkConcept("eslicarbazepine", "C2725260", "eslicarbazepine"),
        ("eslicarbazepine", "eslicarbazepine acetate", "eslicarbazepineacetate"),
    ),
    (BenchmarkConcept("oxcarbazepine", "C0069751", "oxcarbazepine"), ("oxcarbazepine",)),
    (BenchmarkConcept("lacosamide", "C0893761", "lacosamide"), ("lacosamide",)),
    (BenchmarkConcept("midazolam", "C0026056", "midazolam"), ("midazolam",)),
    (BenchmarkConcept("pregabalin", "C0657912", "pregabalin"), ("pregabalin",)),
    (BenchmarkConcept("gabapentin", "C0060926", "gabapentin"), ("gabapentin",)),
    (
        BenchmarkConcept("carbamazepine", "C0006949", "carbamazepine"),
        ("carbamazapine", "carbmazapine"),
    ),
)
PRESCRIPTION_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _PRESCRIPTION_ENTRIES
    for variant in variants
}
PRESCRIPTION_SURFACE_FORMS: tuple[str, ...] = tuple(
    variant for _concept, variants in _PRESCRIPTION_ENTRIES for variant in variants
)

_DIAGNOSIS_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (BenchmarkConcept("Epilepsy", "C0014544", "epilepsy"), ("epilepsy",)),
    (BenchmarkConcept("Epilepsy", "C0014547", "focal epilepsy"), ("focal epilepsy",)),
    (
        BenchmarkConcept("Epilepsy", "C0014547", "focal-onset epilepsy"),
        ("focal-onset epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014556", "temporal lobe epilepsy"),
        ("temporal lobe epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0270853", "juvenile myoclonic epilepsy"),
        ("juvenile myoclonic epilepsy", "jme"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014544", "symptomatic epilepsy"),
        ("symptomatic epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014547", "symptomatic structural focal epilepsy"),
        ("symptomatic structural focal epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014547", "localisation-related-epilepsy"),
        ("localisation related epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0472349", "symptomatic-focal-epilepsy"),
        ("symptomatic focal epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0494475", "generalised-tonic-clonic-seizures"),
        (
            "generalised tonic clonic seizures",
            "generalised tonic clonic seizure",
            "generalized tonic clonic seizures",
            "tonic clonic seizures",
            "tonic clonic convulsion",
            "grand mal",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0270844", "generalised-tonic-seizures"),
        ("generalised tonic seizures",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0751495", "focal-seizures"),
        ("focal seizures", "focal seizure"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0877017", "focal-to-bilateral-convulsive-seizures"),
        (
            "focal to bilateral convulsive seizures",
            "focal to bilateral convulsive seizure",
            "bilateral convulsive seizures",
            "bilateral convulsive seizure",
            "secondary generalised tonic clonic seizures",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0270834", "focal-seizures-with-altered-awareness"),
        (
            "focal seizures with altered awareness",
            "focal impaired awareness seizures",
            "dyscognitive seizures",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0149958", "complex-partial-seizures"),
        ("complex partial seizures", "complex partial seizure"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0270838", "secondary-generalised-seizures"),
        (
            "secondary generalised seizures",
            "secondary generalised seizure",
            "secondarily generalised seizures",
            "secondary generalisation",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0234533", "generalised-seizures"),
        ("generalised seizures",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0016399", "focal-motor-seizures"),
        ("focal motor seizures", "focal motor seizure", "partial motor seizures"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C4317109", "epileptic-seizures"),
        ("epileptic seizures", "epileptic seizure"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0038220", "status-epilepticus"),
        ("status epilepticus",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C4317123", "myoclonic-seizures"),
        ("myoclonic seizures",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0748605", "nocturnal-seizures"),
        ("nocturnal seizures",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0234974", "simple-partial-seizures"),
        ("simple partial seizures",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0270850", "primary-generalised-epilepsy"),
        ("primary generalised epilepsy", "genetic generalised epilepsy"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014548", "generalised-epilepsy"),
        ("generalised epilepsy",),
    ),
    (
        BenchmarkConcept(
            "Epilepsy",
            "C0393697",
            "epilepsy-with-generalised-tonic-clonic-seizures-alone",
        ),
        (
            "epilepsy with generalised tonic clonic seizures alone",
            "epilepsy with generalised tonic clonic seizure alone",
            "epilepsy with generalised tonic clonic seizures on awakening",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0393691", "occipital-lobe-epilepsy"),
        ("occipital lobe epilepsy", "occipital lobe seizures"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0393690", "parietal-lobe-epilepsy"),
        ("parietal lobe epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C4317339", "juvenile-absence-epilepsy"),
        ("juvenile absence epilepsy",),
    ),
    (
        BenchmarkConcept("Epilepsy", "C1096063", "intractable-epilepsy"),
        (
            "intractable epilepsy",
            "refractory epilepsies",
            "drug resistant epilepsy",
            "drug refractory epilepsy",
            "drug refractory epilepsies",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0085541", "frontal-lobe-epilepsy"),
        ("frontal lobe epilepsy", "frontal lobe onset seizure", "frontal lobe seizures"),
    ),
    (
        BenchmarkConcept("Epilepsy", "C0014556", "temporal-lobe-seizure"),
        (
            "temporal lobe seizure",
            "temporal lobe seizures",
            "temporal lobe onset seizure",
        ),
    ),
    (
        BenchmarkConcept("Epilepsy", "C4316903", "absence-seizures"),
        ("absence seizures", "typical absences"),
    ),
)
_DIAGNOSIS_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _DIAGNOSIS_ENTRIES
    for variant in variants
}
_DIAGNOSIS_DIAGNOSTIC_ONLY_RESIDUALS: frozenset[str] = frozenset(
    normalize_phrase(phrase)
    for phrase in (
        "generalised",
        "secondary",
        "focal",
        "drug",
        "symptomatic",
        "occipital",
        "temporal",
        "epileptic",
    )
)
DIAGNOSIS_SURFACE_FORMS: tuple[str, ...] = tuple(
    variant for _concept, variants in _DIAGNOSIS_ENTRIES for variant in variants
)

_INVESTIGATION_CONCEPT_BY_RESULT: dict[tuple[str, str | None], BenchmarkConcept] = {
    ("EEG", "Abnormal"): BenchmarkConcept("EEG", "C0151611", "eeg abnormal"),
    ("EEG", "Normal"): BenchmarkConcept("EEG", "C0744602", "eeg normal"),
    ("EEG", "Unknown"): BenchmarkConcept("EEG", "C0013819", "EEG"),
    ("MRI", "Normal"): BenchmarkConcept("MRI", "C0436481", "mri normal"),
    ("MRI", "Abnormal"): BenchmarkConcept("MRI", "C1319851", "mri abnormal"),
    ("CT", "Normal"): BenchmarkConcept("CT", "C0560017", "ct normal"),
    ("CT", "Abnormal"): BenchmarkConcept("CT", "C0436539", "ct abnormal"),
    ("CT", "Unknown"): BenchmarkConcept("CT", "C3515741", "ct-unknown"),
    ("EEG", None): BenchmarkConcept("EEG", "C0013819", "EEG"),
    ("MRI", None): BenchmarkConcept("MRI", "C0436539", "MRI"),
    ("CT", None): BenchmarkConcept("CT", "C0040405", "CT"),
}
_ONSET_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase("epilepsy"): BenchmarkConcept("epilepsy", "C0014544", "epilepsy"),
    normalize_phrase("seizures"): BenchmarkConcept("seizures", "C0036572", "seizures"),
    normalize_phrase("seizure"): BenchmarkConcept("seizure", "C0036572", "seizures"),
}
_WHEN_DIAGNOSED_CONCEPT = BenchmarkConcept("epilepsy", "C0014544", "epilepsy")
_BIRTH_HISTORY_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (
        BenchmarkConcept("born-normally", "C3665337", "born-normally"),
        ("born normally", "birth normal", "normal birth"),
    ),
    (BenchmarkConcept("birth-was-normal", "C3665337", "birth-was-normal"), ("birth was normal",)),
    (BenchmarkConcept("normal", "C3665337", "normal"), ("normal delivery",)),
    (BenchmarkConcept("term", "C0233324", "term"), ("full term", "full-term")),
    (
        BenchmarkConcept("born-prematurely", "C0151526", "born-prematurely"),
        ("born prematurely",),
    ),
    (
        BenchmarkConcept("late-preterm-birth", "C3829315", "late-preterm-birth"),
        ("born slightly premature", "born slightly prematurely"),
    ),
    (
        BenchmarkConcept(
            "moderate-to-late-preterm-birth",
            "C4054482",
            "moderate-to-late-preterm-birth",
        ),
        ("born prematurely at 32 weeks", "32 weeks"),
    ),
    (
        BenchmarkConcept("perinatal-insult", "C0005604", "perinatal-insult"),
        ("perinatal insult",),
    ),
    (
        BenchmarkConcept("perinatal-injury", "C0456798", "perinatal-injury"),
        ("perinatal trauma", "perinatal injury"),
    ),
    (
        BenchmarkConcept("perinatal-hypoxia", "C0559478", "perinatal-hypoxia"),
        ("perinatal hypoxia",),
    ),
    (
        BenchmarkConcept("hypoxia-during-birth", "C0559478", "hypoxia-during-birth"),
        ("hypoxia during a difficult birth", "hypoxia during birth"),
    ),
    (
        BenchmarkConcept("special-care-baby-unit", "C0583275", "special-care-baby-unit"),
        ("special care baby unit",),
    ),
)
_BIRTH_HISTORY_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _BIRTH_HISTORY_ENTRIES
    for variant in variants
}
_EPILEPSY_CAUSE_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (
        BenchmarkConcept("perinatal-insult", "C0005604", "perinatal-insult"),
        ("perinatal insult",),
    ),
    (BenchmarkConcept("strokes", "C0038454", "strokes"), ("stroke",)),
    (
        BenchmarkConcept("traumatic-brain-injury", "C0876926", "traumatic-brain-injury"),
        ("traumatic brain injury",),
    ),
    (BenchmarkConcept("brain-surgery", "C0195775", "brain-surgery"), ("brain surgery",)),
    (BenchmarkConcept("cerebral-abscess", "C1510428", "cerebral-abscess"), ("cerebral abcess",)),
    (BenchmarkConcept("meningitis", "C0025289", "meningitis"), ("meningitis",)),
    (BenchmarkConcept("cranial-meningioma", "C0349604", "cranial-meningioma"), ("meningioma",)),
    (BenchmarkConcept("Measles", "C0025007", "Measles"), ("measles",)),
    (
        BenchmarkConcept("Tuberous-sclerosis", "C0041341", "Tuberous-sclerosis"),
        ("tuberous sclerosis",),
    ),
    (
        BenchmarkConcept("perinatal-trauma", "C0456798", "perinatal-trauma"),
        ("perinatal trauma",),
    ),
    (
        BenchmarkConcept("hypoxia-during-birth", "C0559478", "hypoxia-during-birth"),
        (
            "hypoxia during birth",
        ),
    ),
    (
        BenchmarkConcept("herpes-encephalitis", "C0276226", "herpes-encephalitis"),
        ("herpes encephalitis",),
    ),
    (BenchmarkConcept("encephalitis", "C0014038", "encephalitis"), ("encephalitis",)),
    (
        BenchmarkConcept("neurocysticercosis", "C0338437", "neurocysticercosis"),
        ("neurocysticercosis",),
    ),
    (BenchmarkConcept("brain", "C1456496", "brain"), ("ischaemic damage", "ischemic damage")),
)
_EPILEPSY_CAUSE_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _EPILEPSY_CAUSE_ENTRIES
    for variant in variants
}
_EPILEPSY_CAUSE_BOUNDARY_CONTROL_RESIDUALS: frozenset[str] = frozenset(
    normalize_phrase(phrase)
    for phrase in (
        "erinatal insult",
        "traumatic brain injury 2005",
        "easle",
        "hypoxia during a difficult birth.",
        "neurocysticercosis.",
    )
)
_PATIENT_HISTORY_ENTRIES: tuple[tuple[BenchmarkConcept, tuple[str, ...]], ...] = (
    (BenchmarkConcept("seizures", "C0036572", "seizures"), ("seizures", "seizure")),
    (
        BenchmarkConcept("febrile-seizures", "C0009952", "febrile-seizures"),
        ("febrile seizures", "febrile-seizures", "febrile seizure"),
    ),
    (
        BenchmarkConcept("febrile-convulsions", "C0009952", "febrile-convulsions"),
        ("febrile convulsions", "febrile-convulsions", "febrile convulsion"),
    ),
    (BenchmarkConcept("anxiety", "C0003467", "anxiety"), ("anxiety",)),
    (BenchmarkConcept("depression", "C0011570", "depression"), ("depression",)),
    (BenchmarkConcept("migraine", "C0149931", "migraine"), ("migraine", "migraines")),
    (
        BenchmarkConcept("myoclonic-jerks", "C0027066", "myoclonic-jerks"),
        ("myoclonic jerks", "myoclonic-jerks"),
    ),
    (
        BenchmarkConcept("absences", "C0563606", "absences"),
        ("absences", "absence like seizure", "absence like seizures"),
    ),
    (
        BenchmarkConcept("dissociative-seizures", "C0349245", "dissociative-seizures"),
        (
            "dissociative seizures",
            "dissociative-seizures",
            "dissociative seizure",
            "dissociative (non epileptic) seizures",
        ),
    ),
    (
        BenchmarkConcept(
            "non-epileptic-psychogenic-seizures",
            "C1142430",
            "non-epileptic-psychogenic-seizures",
        ),
        ("non epileptic psychogenic seizures", "non-epileptic psychogenic seizures"),
    ),
    (
        BenchmarkConcept("non-epileptic-attacks", "C3495874", "non-epileptic-attacks"),
        ("non epileptic attacks", "non-epileptic attacks"),
    ),
    (
        BenchmarkConcept(
            "transient-loss-of-consciousness",
            "C4087400",
            "transient-loss-of-consciousness",
        ),
        ("transient loss of consciousness", "transient-loss-of-consciousness"),
    ),
    (
        BenchmarkConcept("loss-of-consciousness", "C0041657", "loss-of-consciousness"),
        (
            "loss of consciousness",
            "loss-of-consciousness",
            "episodes of loss of consciousness",
            "episode of loss of consciousness",
            "loss of consciousnes",
        ),
    ),
    (BenchmarkConcept("diabetes", "C0011849", "diabetes"), ("diabetes",)),
    (
        BenchmarkConcept("type-1-diabetes", "C0011854", "type-1-diabetes"),
        ("type 1 diabetes", "insulin dependent diabetes"),
    ),
    (BenchmarkConcept("gliosis", "C0017639", "gliosis"), ("gliosis",)),
    (
        BenchmarkConcept("cortical-dysplasia", "C0431380", "cortical-dysplasia"),
        ("cortical dysplasia", "cortical-dysplasia"),
    ),
    (
        BenchmarkConcept("head-injury", "C0497301", "head-injury"),
        (
            "head injury",
            "minor head injury",
            "severe head injury",
            "head injuries",
            "significant head injury",
        ),
    ),
    (
        BenchmarkConcept("traumatic-brain-injury", "C0876926", "traumatic-brain-injury"),
        ("traumatic brain injury",),
    ),
    (BenchmarkConcept("meningitis", "C0025289", "meningitis"), ("meningitis", "viral meningitis")),
    (
        BenchmarkConcept("viral-encephalitis", "C0243010", "viral-encephalitis"),
        ("viral encephalitis",),
    ),
    (BenchmarkConcept("encephalitis", "C0014038", "encephalitis"), ("encephalitis",)),
    (BenchmarkConcept("brain-surgery", "C0195775", "brain-surgery"), ("brain surgery",)),
    (
        BenchmarkConcept("cerebral-abscess", "C1510428", "cerebral-abscess"),
        ("cerebral abscess", "cerebral abcess"),
    ),
    (
        BenchmarkConcept("hypertension", "C0020538", "hypertension"),
        ("hypertension", "hypertensions"),
    ),
    (
        BenchmarkConcept("learning-disabilities", "C0751265", "learning-disabilities"),
        ("learning disabilities", "learning disability"),
    ),
    (
        BenchmarkConcept("learning-difficulties", "C0424939", "learning-difficulties"),
        ("learning difficulties", "learning difficulty"),
    ),
    (BenchmarkConcept("stroke", "C0038454", "stroke"), ("stroke", "cva")),
    (BenchmarkConcept("syncope", "C0039070", "syncope"), ("syncope",)),
    (BenchmarkConcept("photosensitivity", "C3552821", "photosensitivity"), ("photosensitivity",)),
    (
        BenchmarkConcept("tuberous-sclerosis", "C0041341", "tuberous-sclerosis"),
        ("tuberous sclerosis",),
    ),
    (BenchmarkConcept("measles", "C0025007", "measles"), ("measles",)),
    (
        BenchmarkConcept("neurocysticercosis", "C0338437", "neurocysticercosis"),
        ("neurocysticercosis",),
    ),
    (BenchmarkConcept("meningioma", "C0349604", "meningioma"), ("meningioma",)),
    (
        BenchmarkConcept("cluster-of-seizures", "C3203523", "cluster-of-seizures"),
        (
            "cluster of seizures",
            "cluster-of-seizures",
            "cluster of seizure",
            "cluster of three seizures",
            "clusters of seizures",
        ),
    ),
    (BenchmarkConcept("myoclonus", "C0027066", "myoclonus"), ("myoclonus",)),
    (BenchmarkConcept("jerks", "C0231530", "jerks"), ("jerks",)),
    (
        BenchmarkConcept(
            "altered-awareness-and-consciousness",
            "C0234428",
            "altered-awareness-and-consciousness",
        ),
        ("altered awareness",),
    ),
    (BenchmarkConcept("déjà-vu", "C0011194", "déjà-vu"), ("déjà vu",)),
    (BenchmarkConcept("hemiparesis", "C0018989", "hemiparesis"), ("hemiparesis",)),
)
_PATIENT_HISTORY_CONCEPT_BY_PHRASE: dict[str, BenchmarkConcept] = {
    normalize_phrase(variant): concept
    for concept, variants in _PATIENT_HISTORY_ENTRIES
    for variant in variants
}


def prescription_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark medication concept for ``phrase`` if known."""

    key = normalize_phrase(phrase)
    concept = PRESCRIPTION_CONCEPT_BY_PHRASE.get(key)
    if concept is not None:
        return concept
    resolved = normalize_phrase(resolve_drug_surface(phrase))
    if resolved != key:
        return PRESCRIPTION_CONCEPT_BY_PHRASE.get(resolved)
    return None


def diagnosis_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark diagnosis concept for ``phrase`` if known."""

    normalized = normalize_phrase(phrase)
    if normalized in _DIAGNOSIS_DIAGNOSTIC_ONLY_RESIDUALS:
        return None
    return _DIAGNOSIS_CONCEPT_BY_PHRASE.get(normalized)


def investigation_concept(modality: str, result: str | None) -> BenchmarkConcept | None:
    """Return the benchmark investigation concept for a modality/result pair."""

    return _INVESTIGATION_CONCEPT_BY_RESULT.get((modality.upper(), result))


def onset_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark onset concept for a source-near onset phrase."""

    return _ONSET_CONCEPT_BY_PHRASE.get(normalize_phrase(phrase))


def when_diagnosed_concept() -> BenchmarkConcept:
    """Return the benchmark epilepsy concept used for diagnosis-timing mentions."""

    return _WHEN_DIAGNOSED_CONCEPT


def birth_history_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark birth-history concept for ``phrase`` if known."""

    return _BIRTH_HISTORY_CONCEPT_BY_PHRASE.get(normalize_phrase(phrase))


def epilepsy_cause_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark epilepsy-cause concept for ``phrase`` if known."""

    normalized = normalize_phrase(phrase)
    if normalized in _EPILEPSY_CAUSE_BOUNDARY_CONTROL_RESIDUALS:
        return None
    return _EPILEPSY_CAUSE_CONCEPT_BY_PHRASE.get(normalized)


def patient_history_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark patient-history concept for ``phrase`` if known."""

    return _PATIENT_HISTORY_CONCEPT_BY_PHRASE.get(normalize_phrase(phrase))


def seizure_frequency_concept(phrase: str) -> BenchmarkConcept | None:
    """Return the benchmark seizure-frequency concept for ``phrase`` if known."""

    cui = assign_cui(phrase)
    if cui is None:
        return None
    return BenchmarkConcept(phrase, cui, phrase)


def attach_benchmark_concept(
    attributes: Mapping[str, str],
    concept: BenchmarkConcept,
    *,
    canonical_key: str | None = None,
) -> dict[str, str]:
    """Attach CUI attributes and, optionally, the concept canonical value."""

    projected = dict(attributes)
    if canonical_key is not None and not str(projected.get(canonical_key, "")).strip():
        projected[canonical_key] = concept.canonical
    projected.update({"CUI": concept.cui, "CUIPhrase": concept.cui_phrase})
    return projected


def project_cuis(prediction: PredictedLetter) -> PredictedLetter:
    """Attach known active-entity CUIs to a prediction without changing phrases."""

    mentions = tuple(_project_mention_cui(mention) for mention in prediction.mentions)
    projected_count = sum(
        1
        for before, after in zip(prediction.mentions, mentions, strict=True)
        if "CUI" not in before.attributes and "CUI" in after.attributes
    )
    diagnostics = dict(prediction.diagnostics)
    diagnostics["cui_projected_mentions"] = projected_count
    return PredictedLetter(
        letter_id=prediction.letter_id,
        mentions=mentions,
        diagnostics=diagnostics,
    )


def _project_mention_cui(mention: PredictedMention) -> PredictedMention:
    if "CUI" in mention.attributes:
        return mention

    concept = _concept_for_mention(mention)
    if concept is None:
        return mention

    canonical_key = _canonical_key_for_entity(mention.entity)
    return PredictedMention(
        entity=mention.entity,
        text=mention.text,
        attributes=attach_benchmark_concept(
            mention.attributes,
            concept,
            canonical_key=canonical_key,
        ),
        evidence=mention.evidence,
        evidence_span=mention.evidence_span,
        rationale=mention.rationale,
        confidence=mention.confidence,
        uncertainty_flags=mention.uncertainty_flags,
        component_owner=mention.component_owner,
    )


def _concept_for_mention(mention: PredictedMention) -> BenchmarkConcept | None:
    if mention.entity == PRESCRIPTION.name:
        drug_name = mention.attributes.get("DrugName")
        return prescription_concept(drug_name or mention.text)
    if mention.entity == DIAGNOSIS.name:
        return diagnosis_concept(mention.text)
    if mention.entity == INVESTIGATIONS.name:
        modality = _investigation_modality_from_attributes(mention.attributes) or mention.text
        result = _investigation_result_from_attributes(mention.attributes, modality)
        return investigation_concept(modality, result)
    if mention.entity == ONSET.name:
        return onset_concept(mention.text)
    if mention.entity == WHEN_DIAGNOSED.name:
        return when_diagnosed_concept()
    if mention.entity == BIRTH_HISTORY.name:
        return birth_history_concept(mention.text)
    if mention.entity == EPILEPSY_CAUSE.name:
        return epilepsy_cause_concept(mention.text)
    if mention.entity == PATIENT_HISTORY.name:
        return patient_history_concept(mention.text)
    if mention.entity == SEIZURE_FREQUENCY.name:
        return seizure_frequency_concept(mention.text)
    return None


def _canonical_key_for_entity(entity: str) -> str | None:
    if entity == PRESCRIPTION.name:
        return "DrugName"
    if entity == DIAGNOSIS.name:
        return "DiagCategory"
    return None


def _investigation_modality_from_attributes(attributes: Mapping[str, str]) -> str | None:
    for modality in ("EEG", "MRI", "CT"):
        if attributes.get(f"{modality}_Performed") == "Yes" or f"{modality}_Results" in attributes:
            return modality
    return None


def _investigation_result_from_attributes(
    attributes: Mapping[str, str],
    modality: str,
) -> str | None:
    canonical = modality.upper()
    result = attributes.get(f"{canonical}_Results")
    return result if result in {"Normal", "Abnormal", "Unknown"} else None
