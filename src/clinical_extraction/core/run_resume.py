"""Resume support for incremental experiment runners (task-neutral).

A foundational runner requirement: a long live run (an LLM sweep over hundreds
of records, a slow local model) must survive interruption — a crash, a killed
background process, a powered-off machine — without re-spending the work already
done. Every runner that writes a per-record checkpoint artifact can resume from
it with these helpers.

The contract is deliberately small:

* Runners checkpoint a newline-delimited JSON artifact where each row carries a
  stable per-record key (``letter_id``, ``source_row_index``, ...) and the
  checkpoint always contains every record processed so far (a full rewrite, not
  an append) — so any checkpoint is a valid, self-consistent prefix.
* On resume, ``read_completed`` returns the already-finished rows and their key
  set; the runner skips those records, processes only the remainder, and
  ``merge_rows`` stitches old + new back into the requested order.

No row is recomputed and none is lost or duplicated, regardless of where the
previous run stopped.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path
from typing import Any, TypeVar

T = TypeVar("T")

DEFAULT_KEY = "letter_id"


def read_completed(
    path: Path | str | None,
    *,
    key: str = DEFAULT_KEY,
) -> tuple[list[dict[str, Any]], set[str]]:
    """Load completed rows and their key set from a checkpoint artifact.

    Returns ``([], set())`` when ``path`` is None or does not yet exist (the
    first, non-resumed run). A row missing the key is kept in the rows list but
    contributes nothing to the completed-key set, so it is reprocessed.
    """
    if path is None:
        return [], set()
    p = Path(path)
    if not p.exists():
        return [], set()
    rows: list[dict[str, Any]] = []
    with p.open(encoding="utf-8-sig") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    completed = {str(r[key]) for r in rows if isinstance(r, dict) and r.get(key) is not None}
    return rows, completed


def pending_items(
    items: Sequence[T],
    completed: set[str],
    key_of: Callable[[T], str],
) -> list[T]:
    """Return the items whose key is not already completed, in input order."""
    return [item for item in items if str(key_of(item)) not in completed]


def merge_rows(
    rows: Iterable[dict[str, Any]],
    order: Sequence[str],
    *,
    key: str = DEFAULT_KEY,
) -> list[dict[str, Any]]:
    """Deduplicate rows by key (last write wins) and reorder to ``order``.

    ``order`` is the full sequence of requested keys (e.g. every letter_id in the
    split). Rows whose key is not in ``order`` are appended at the end in first-
    seen order, so nothing is silently dropped.
    """
    by_key: dict[str, dict[str, Any]] = {}
    extras: list[dict[str, Any]] = []
    for row in rows:
        k = row.get(key)
        if k is None:
            extras.append(row)
        else:
            by_key[str(k)] = row
    ordered = [by_key[k] for k in order if k in by_key]
    seen = set(order)
    ordered.extend(row for k, row in by_key.items() if k not in seen)
    ordered.extend(extras)
    return ordered
