"""Cut `exectv2_split_v2.json` from v1: drop EA0159 from `test`.

Phase 0 of docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md.
`EA0159` (test) and `EA0160` (dev) are one of the source corpus's 4 disclosed
duplicate-letter pairs (Fonferko-Shadrach et al. 2024: "Four letters were
duplicated within the set to test for consistency in annotations") and are the
only pair split across the frozen dev/test boundary. Decision (user-confirmed
2026-07-01, Option A): drop `EA0159` from `test` rather than relocate it, since
its content is already represented in `dev` via `EA0160` and the other 3
duplicate pairs already land same-side. `v1` is left untouched (it is
referenced by `evidence_validity` language in existing registry rows and must
remain a stable historical record); this cuts a new, separately versioned
manifest.

Usage: uv run python experiments/exectv2_split_v2_cut.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPLITS_DIR = ROOT / "data" / "ExECTv2 (2025)" / "splits"
V1_PATH = SPLITS_DIR / "exectv2_split_v1.json"
V2_PATH = SPLITS_DIR / "exectv2_split_v2.json"
DROPPED_LETTER = "EA0159"


def main() -> None:
    v1 = json.loads(V1_PATH.read_text(encoding="utf-8"))

    test_ids = v1["splits"]["test"]["letter_ids"]
    assert DROPPED_LETTER in test_ids, f"{DROPPED_LETTER} not found in v1 test split"
    new_test_ids = [i for i in test_ids if i != DROPPED_LETTER]
    assert len(new_test_ids) == len(test_ids) - 1

    v2 = dict(v1)
    v2["name"] = "exectv2_split_v2"
    v2["created_date"] = "2026-07-01"
    v2["derived_from"] = "exectv2_split_v1"
    v2["fix_notes"] = (
        f"Dropped {DROPPED_LETTER} from test (Option A, user-confirmed 2026-07-01): "
        f"{DROPPED_LETTER} (test, v1) and EA0160 (dev, v1) are byte-identical letters, "
        "one of the source corpus's 4 disclosed duplicate-annotation-consistency-check "
        "pairs (Fonferko-Shadrach et al. 2024, DOI 10.1186/s13326-024-00316-z), and the "
        "only pair split across the dev/test boundary in v1. See "
        "docs/experiments/exectv2/exectv2_test60_split_dedupe_fix_2026-07-01.md and "
        "docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md."
    )
    v2["splits"] = dict(v1["splits"])
    v2["splits"]["test"] = {"count": len(new_test_ids), "letter_ids": new_test_ids}
    # dev is unchanged from v1 (EA0160 stays; it is same-side-harmless per the audit).

    V2_PATH.write_text(json.dumps(v2, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {V2_PATH.relative_to(ROOT)}")
    print(f"dev: {v2['splits']['dev']['count']} letters (unchanged)")
    print(f"test: {v2['splits']['test']['count']} letters (was {len(test_ids)}, dropped {DROPPED_LETTER})")


if __name__ == "__main__":
    main()
