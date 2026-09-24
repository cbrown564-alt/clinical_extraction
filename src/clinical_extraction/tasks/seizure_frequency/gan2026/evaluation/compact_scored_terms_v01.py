"""Conservative scored concepts for the R9 compact development comparison.

Literal source labels and restrictions remain in the raw reference and response.
This projection scores only named seizure concepts and qualifiers defined here.
It never uses a diagnosis elsewhere in the note to fill a missing event type.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any

VERSION = "compact_scored_terms_v01"


def words(value: str | None) -> str:
    value = unicodedata.normalize("NFKC", value or "").lower()
    value = value.replace("–", "-").replace("—", "-").replace("‑", "-").replace("−", "-")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value)).strip()


def event_types(label: str) -> tuple[str, ...]:
    """Map explicit type words; unclassified descriptions have no scored type."""
    text = words(label)
    found: set[str] = set()
    if re.search(r"\bstatus epilepticus\b|\bstatus episodes?\b", text):
        found.add("status_epilepticus")
    if re.search(
        r"\bfocal to bilateral\b|\bsecondary generalis|\btonic clonic\b.*\bfocal onset\b",
        text,
    ):
        found.add("focal_to_bilateral_tonic_clonic")
    elif re.search(r"\bgeneralised tonic clonic\b|\bgeneralized tonic clonic\b|\bgtcs?\b", text):
        found.add("generalised_tonic_clonic")
    elif re.search(r"\btonic clonic\b|\btcs?\b", text):
        found.add("tonic_clonic_unclassified")
    if re.search(r"\bmyoclonic absence\b", text):
        found.add("myoclonic_absence")
    elif re.search(r"\babsence(s| seizure| episode)?\b|\bpetit mal\b", text) and not re.search(
        r"\babsence like\b|\bdescribed as absences\b", text
    ):
        found.add("absence")
    if (
        re.search(r"\bfocal\b|\bcomplex partial\b|\bsimple partial\b", text)
        and "focal_to_bilateral_tonic_clonic" not in found
    ):
        if re.search(r"\bcomplex partial\b|\bimpaired (awareness|consciousness)\b", text):
            if re.search(r"\bprogress\w* (?:on occasion )?to (?:focal )?impaired\b", text):
                found.add("focal_preserved_to_impaired")
            elif re.search(r"\b(focal aware|simple partial)\b", text):
                found.update(("focal_preserved", "focal_impaired"))
            else:
                found.add("focal_impaired")
        elif re.search(
            r"\bsimple partial\b|\b(aware|preserved awareness|preserved consciousness)\b", text
        ):
            found.add("focal_preserved")
        else:
            found.add("focal_unclassified")
    elif "focal_to_bilateral_tonic_clonic" in found and re.search(r"\bor\b|\band\b", text):
        if re.search(r"\bfocal aware\b|\bsimple partial\b", text):
            found.add("focal_preserved")
        if re.search(r"\bfocal impaired (awareness|consciousness)\b|\bcomplex partial\b", text):
            found.add("focal_impaired")
    if (
        re.search(r"\bmyoclon(ic|us)\b|\bmyoclonic jerks?\b", text)
        and "myoclonic_absence" not in found
    ):
        found.add("myoclonic")
    if re.search(r"\batonic\b", text):
        found.add("atonic")
    elif re.search(r"\bdrop attacks?\b|\bdrop events?\b", text):
        found.add("drop_attack")
    if re.search(r"\bepileptic spasms?\b", text):
        found.add("epileptic_spasm")
    if re.search(r"\bauras?\b", text) and "focal_preserved" not in found:
        found.add("aura")
    if re.search(r"\btonic seizures?\b|\btonic events?\b", text) and not any(
        "tonic_clonic" in code for code in found
    ):
        found.add("tonic")
    has_generalised_label = re.search(
        r"\bgenerali[sz]ed (?:seizures?|convulsions?|events?|episodes?)\b", text
    )
    if has_generalised_label and not any(code.startswith("generalised_") for code in found):
        found.add("generalised_unclassified")
    return tuple(sorted(found))


def event_key(event: dict[str, Any]) -> tuple[str, tuple[str, ...]]:
    scope = event["scope"]
    if scope in {"overall", "unspecified"}:
        return scope, ()
    types = event_types(event["label"])
    # A combined population with fewer than two recognised types cannot be
    # represented faithfully by the finite dictionary. Keep it literal until
    # source adjudication rather than equating different mixtures.
    if scope == "combined" and len(types) < 2:
        return scope, ("unmapped_combination:" + words(event["label"]),)
    return scope, types


def restriction_key(finding: dict[str, Any]) -> tuple[str, ...]:
    """Score only restrictions that limit the counted or observed population.

    The coded terms are intentionally narrow. Other literal modifiers remain
    inspectable in the raw record and exact evidence without receiving credit.
    """
    raw = words(finding.get("restriction"))
    label = words(finding["event"]["label"])
    codes: set[str] = set()
    population = raw + " " + label
    if "device" in population or "smartwatch" in population or "wearable" in population:
        codes.add("device_observed")
    if re.search(
        r"\bwitnessed\b|\bobserved by\b|\bnoticed by\b|\bbrought to attention by\b",
        population,
    ):
        codes.add("witnessed")
    if re.search(r"\bdiary\b|\bapp entries\b|\bpersonal event log\b", population):
        codes.add("diary_recorded")
    if re.search(r"\breported\b|\brecognised (?:as seizures?|by the patient)\b", raw + " " + label):
        codes.add("reported_or_recognised")
    if re.search(r"\brecorded\b|\bdocumented\b|\bnoted\b", raw) and not codes:
        codes.add("recorded")
    if re.search(
        r"\b(nocturnal|night time|nighttime|during sleep|in sleep|from sleep|"
        r"while asleep|at night|out of sleep)\b",
        population,
    ):
        codes.add("during_sleep")
    if re.search(r"\b(daytime|while awake|during the day)\b", population):
        codes.add("while_awake")
    if re.search(r"\b(longest|maximum) seizure free\b", raw):
        codes.add("longest_seizure_free_gap")
    if re.search(r"\b(within|in)\b.*\b(menses|menstrual|peri period)\b", raw):
        codes.add("within_menstrual_window")
    if re.search(r"\boutside\b.*\b(perimenstrual|peri period|menses|menstrual)\b", raw):
        codes.add("outside_menstrual_window")
    if re.search(r"\bdefinite (?:seizure )?events? only\b", raw):
        codes.add("definite_events_only")
    if re.search(r"\bin bad weeks\b", raw):
        codes.add("bad_weeks_only")
    if re.search(r"\bon (?:ambulatory )?eeg\b|\belectrographic\b", population):
        codes.add("electrographic_only")
    return tuple(sorted(codes))
