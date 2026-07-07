"""Predeclaration -> kill-criterion -> verdict -> propagation ledger.

Sibling to ``core/registry.py`` (run provenance), not an extension of it:
``RunRegistryEntry`` is a frozen dataclass with ``Literal`` unions that reject
unknown values, built for indexing run *artifacts*, not for tracking the
lifecycle of an investigative *hypothesis* (has anyone already tested this
against this family? what did it conclude? what did it correct downstream?).
That lifecycle previously existed only as prose status-banners hand-inserted
into docs -- this makes it a queryable file. Mirrors ``core/registry.py``'s
read/write shape (full-rewrite sorted by id) for consistency.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

HypothesisVerdict = Literal["CONFIRMED", "REFUTED", "PARTIAL", "OPEN"]
HYPOTHESIS_VERDICTS: frozenset[str] = frozenset({"CONFIRMED", "REFUTED", "PARTIAL", "OPEN"})


@dataclass(frozen=True)
class HypothesisEntry:
    """One tested (or open) hypothesis about why an entity family's F1 is what it is."""

    hypothesis_id: str
    family: str  # an ExECTv2 KEY_FAMILIES entry, or "cross_family"
    statement: str
    predeclaration_doc: str
    kill_criterion: str
    verdict: HypothesisVerdict
    date: str
    owner: str
    evidence_run_ids: tuple[str, ...] = ()
    evidence_docs: tuple[str, ...] = ()
    downstream_corrections: tuple[str, ...] = ()
    notes: str = ""

    def to_json_record(self) -> dict[str, Any]:
        self.validate()
        return {
            "hypothesis_id": self.hypothesis_id,
            "family": self.family,
            "statement": self.statement,
            "predeclaration_doc": self.predeclaration_doc,
            "kill_criterion": self.kill_criterion,
            "verdict": self.verdict,
            "date": self.date,
            "owner": self.owner,
            "evidence_run_ids": list(self.evidence_run_ids),
            "evidence_docs": list(self.evidence_docs),
            "downstream_corrections": list(self.downstream_corrections),
            "notes": self.notes,
        }

    def validate(self) -> None:
        if self.verdict not in HYPOTHESIS_VERDICTS:
            raise ValueError(f"verdict must be one of {sorted(HYPOTHESIS_VERDICTS)}")
        required = {
            "hypothesis_id": self.hypothesis_id,
            "family": self.family,
            "statement": self.statement,
            "predeclaration_doc": self.predeclaration_doc,
            "kill_criterion": self.kill_criterion,
            "date": self.date,
            "owner": self.owner,
        }
        missing = [name for name, value in required.items() if not value.strip()]
        if missing:
            raise ValueError(f"hypothesis entry missing required field(s): {', '.join(missing)}")


def hypothesis_entry_from_json_record(record: Mapping[str, Any]) -> HypothesisEntry:
    entry = HypothesisEntry(
        hypothesis_id=_required_str(record, "hypothesis_id"),
        family=_required_str(record, "family"),
        statement=_required_str(record, "statement"),
        predeclaration_doc=_required_str(record, "predeclaration_doc"),
        kill_criterion=_required_str(record, "kill_criterion"),
        verdict=_verdict(record),
        date=_required_str(record, "date"),
        owner=_required_str(record, "owner"),
        evidence_run_ids=_string_tuple(record.get("evidence_run_ids", ())),
        evidence_docs=_string_tuple(record.get("evidence_docs", ())),
        downstream_corrections=_string_tuple(record.get("downstream_corrections", ())),
        notes=record.get("notes", "") or "",
    )
    entry.validate()
    return entry


def load_hypothesis_registry(path: Path) -> list[HypothesisEntry]:
    """Load newline-delimited hypothesis-registry entries."""

    if not path.exists():
        return []
    entries: list[HypothesisEntry] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(hypothesis_entry_from_json_record(json.loads(line)))
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError(f"invalid hypothesis record at {path}:{line_number}: {exc}") from exc
    return entries


def write_hypothesis_registry(entries: Sequence[HypothesisEntry], path: Path) -> None:
    """Write newline-delimited hypothesis-registry entries sorted by id."""

    ids = [entry.hypothesis_id for entry in entries]
    duplicates = sorted({hid for hid in ids if ids.count(hid) > 1})
    if duplicates:
        raise ValueError(f"duplicate hypothesis_id(s): {', '.join(duplicates)}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(entries, key=lambda entry: entry.hypothesis_id)
    lines = [
        json.dumps(entry.to_json_record(), ensure_ascii=False, sort_keys=True) for entry in ordered
    ]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def _required_str(record: Mapping[str, Any], field_name: str) -> str:
    value = record.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string")
    return value


def _verdict(record: Mapping[str, Any]) -> HypothesisVerdict:
    value = _required_str(record, "verdict")
    if value not in HYPOTHESIS_VERDICTS:
        raise ValueError(f"verdict must be one of: {', '.join(sorted(HYPOTHESIS_VERDICTS))}")
    return cast(HypothesisVerdict, value)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list | tuple):
        raise ValueError("expected a list of strings")
    if not all(isinstance(item, str) for item in value):
        raise ValueError("expected a list of strings")
    return tuple(value)
