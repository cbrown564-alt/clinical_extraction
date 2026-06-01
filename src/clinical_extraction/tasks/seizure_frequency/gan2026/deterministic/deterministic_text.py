from __future__ import annotations

import re


def normalize_note_text(note_text: str) -> str:
    return re.sub(r"\s+", " ", note_text)


def clean_evidence(evidence: str) -> str:
    return evidence.strip(" .;:\n\t")


def fallback_evidence(note_text: str) -> str:
    first_sentence = re.split(r"(?<=[.!?])\s+", note_text.strip(), maxsplit=1)[0]
    return first_sentence[:240] if first_sentence else ""


def exact_evidence(note_text: str, evidence: str) -> str:
    if evidence in note_text:
        return evidence
    pattern = r"\s+".join(re.escape(part) for part in evidence.split())
    match = re.search(pattern, note_text)
    if match:
        return note_text[match.start() : match.end()].strip(" .;:\n\t")
    return evidence
