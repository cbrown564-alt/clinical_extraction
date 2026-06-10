"""Profile the ExECTv2 gold corpus into an auditable schema artifact.

Emits, per entity, every observed attribute key and its value set (with counts),
derived live from `load_letters()`.  The entity/attribute registry in
`tasks/epilepsy_phenotyping/exectv2/contract/entities.py` is hand-curated from
this output; `tests/test_exectv2_contract.py` re-derives the same schema and
asserts the registry stays in lockstep, so this script exists to *regenerate*
and human-audit the profile (e.g. after a gold-annotation change), not as the
test's source of truth.

Run from repo root:
    uv run python experiments/profile_exectv2_gold_schema.py
writes docs/research/exectv2_gold_schema_profile_<date>.json
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters

OUT_DIR = Path("docs/research")


def profile() -> dict[str, object]:
    entity_mentions: Counter[str] = Counter()
    entity_letters: defaultdict[str, set[str]] = defaultdict(set)
    attr_values: defaultdict[str, defaultdict[str, Counter[str]]] = defaultdict(
        lambda: defaultdict(Counter)
    )

    for letter in load_letters():
        for ann in letter.annotations:
            entity_mentions[ann.entity] += 1
            entity_letters[ann.entity].add(letter.letter_id)
            for key, value in ann.attributes.items():
                attr_values[ann.entity][key][value] += 1

    entities: dict[str, object] = {}
    for entity in sorted(entity_mentions, key=lambda e: -entity_mentions[e]):
        attributes: dict[str, object] = {}
        for attr in sorted(attr_values[entity]):
            counts = attr_values[entity][attr]
            attributes[attr] = {
                "distinct": len(counts),
                "total": sum(counts.values()),
                "values": dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))),
            }
        entities[entity] = {
            "mentions": entity_mentions[entity],
            "letters_with_ge1": len(entity_letters[entity]),
            "attributes": attributes,
        }

    return {"generated": date.today().isoformat(), "entities": entities}


def main() -> None:
    data = profile()
    out_path = OUT_DIR / f"exectv2_gold_schema_profile_{data['generated']}.json"
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    total = sum(e["mentions"] for e in data["entities"].values())  # type: ignore[index]
    print(f"wrote {out_path}")
    print(f"{len(data['entities'])} entities, {total} total mentions")
    for name, spec in data["entities"].items():  # type: ignore[union-attr]
        print(f"  {name:18s} {spec['mentions']:4d} mentions, {len(spec['attributes'])} attributes")


if __name__ == "__main__":
    main()
