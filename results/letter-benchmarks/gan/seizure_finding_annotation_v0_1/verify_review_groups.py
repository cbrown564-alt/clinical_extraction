"""Fictional mocked tests for build_review_groups.py.
No clinical data or real annotation outputs are read.
"""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from build_review_groups import build_review_groups, sha256_text


def make_test_data():
    note_1 = (
        "Patient reports 3 seizures per month. "
        "Last seizure occurred on May 12, 2026. Clustering noted."
    )
    sha_1 = sha256_text(note_1)
    src_1 = {
        "source_id": "src_001",
        "source_row_index": 1,
        "note_text": note_1,
        "source_sha256": sha_1,
        "batch": "batch_01",
    }
    ann_1 = {
        "source_id": "src_001",
        "source_row_index": 1,
        "source_sha256": sha_1,
        "guide_version": "seizure_finding_annotation_v0.3",
        "findings": [
            {
                "id": "f1",
                "evidence": "3 seizures per month",
                "measurement": {"type": "rate", "count": 3, "per": {"unit": "month", "value": 1}},
                "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
                "timing": "current",
            },
            {
                "id": "f2",
                "evidence": "Last seizure occurred on May 12, 2026",
                "measurement": {"type": "last_seizure", "occurred_at": "May 12, 2026"},
                "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
                "timing": "current",
            },
        ],
        "finding_context": [
            {"finding_id": "f1", "mentions": ["3 seizures per month"], "relations": []},
            {
                "finding_id": "f2",
                "mentions": ["Last seizure occurred on May 12, 2026"],
                "relations": [],
            },
        ],
        "source_checks": [
            {"evidence": "3 seizures per month", "finding_ids": ["f1"]},
            {"evidence": "Last seizure occurred on May 12, 2026", "finding_ids": ["f2"]},
        ],
        "issues": [],
    }

    note_2 = "No seizures since surgery. Patient also recalls 2 spells every week in childhood."
    sha_2 = sha256_text(note_2)
    src_2 = {
        "source_id": "src_002",
        "source_row_index": 2,
        "note_text": note_2,
        "source_sha256": sha_2,
        "batch": "batch_01",
    }
    ann_2 = {
        "source_id": "src_002",
        "source_row_index": 2,
        "source_sha256": sha_2,
        "guide_version": "seizure_finding_annotation_v0.3",
        "findings": [
            {
                "id": "f1",
                "evidence": "No seizures since surgery",
                "measurement": {"type": "seizure_free", "since": "surgery"},
                "event": {"type": "seizures", "scope": "unspecified", "seizure_status": "stated"},
                "timing": "current",
            }
        ],
        "finding_context": [
            {"finding_id": "f1", "mentions": ["No seizures since surgery"], "relations": []},
        ],
        "source_checks": [
            {"evidence": "No seizures since surgery", "finding_ids": ["f1"]},
            # Source candidate with no finding link containing lexical backstop word "every"
            {"evidence": "2 spells every week in childhood", "finding_ids": []},
        ],
        "issues": [],
    }
    return [src_1, src_2], [ann_1, ann_2]


class TestReviewGroups(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp_dir.name)
        self.sources, self.annotations = make_test_data()

        self.sources_path = self.dir / "sources.jsonl"
        self.annotations_path = self.dir / "annotations.jsonl"
        self.candidates_path = self.dir / "candidates.jsonl"
        self.out_dir = self.dir / "review_groups"

        self.sources_path.write_text(
            "".join(json.dumps(s) + "\n" for s in self.sources), encoding="utf-8"
        )
        self.annotations_path.write_text(
            "".join(json.dumps(a) + "\n" for a in self.annotations), encoding="utf-8"
        )

    def test_nested_duration_enums_enter_unusual_group(self):
        # Membership-only fixture: primary enums are shared, nested units differ.
        for index, row in enumerate(self.annotations):
            row["findings"] = row["findings"][:1]
            row["finding_context"] = row["finding_context"][:1]
            row["source_checks"] = []
            row["findings"][0]["measurement"] = {
                "type": "rate",
                "count": {"type": "number", "value": 2},
                "per": {"type": "number", "value": 1, "unit": ["day", "week"][index]},
            }
        self.annotations_path.write_text("".join(json.dumps(a) + "\n" for a in self.annotations))
        build_review_groups(
            self.sources_path, self.annotations_path, None, None, None, self.out_dir, 2
        )
        groups = [
            json.loads(line) for line in (self.out_dir / "groups.jsonl").read_text().splitlines()
        ]
        unusual = next(g for g in groups if g["group_id"] == "C07-unusual")
        member_ids = {m["member_id"] for m in unusual["members"]}
        self.assertTrue({"src_001/f1", "src_002/f1"}.issubset(member_ids))

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_two_fictional_sources_and_source_only_candidates(self):
        cand_records = [
            {
                "source_id": "src_002",
                "source_row_index": 2,
                "candidate_quote": "2 spells every week in childhood",
                "finding_ids": [],
            }
        ]
        self.candidates_path.write_text(
            "".join(json.dumps(c) + "\n" for c in cand_records), encoding="utf-8"
        )

        summary = build_review_groups(
            sources_path=self.sources_path,
            annotations_path=self.annotations_path,
            candidates_path=self.candidates_path,
            all_sources_path=None,
            patterns_arg=None,
            out_dir=self.out_dir,
            expected=2,
        )

        self.assertTrue((self.out_dir / "groups.jsonl").is_file())
        self.assertTrue((self.out_dir / "summary.json").is_file())
        self.assertEqual(summary["checked"], 0)
        self.assertEqual(summary["semantic_review_state"], "pending")
        self.assertEqual(summary["expected_sources"], 2)
        self.assertEqual(summary["sources_count"], 2)

        groups = [
            json.loads(line)
            for line in (self.out_dir / "groups.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        for g in groups:
            self.assertEqual(g["comparisons"], [])
            self.assertEqual(g["review_state"], "pending")
            for m in g["members"]:
                mid = m["member_id"]
                # Must be readable format: source_id/finding_id, source_id/issue_id,
                # source_id/source, or source_id/candidateNNN
                self.assertTrue(
                    mid.endswith("/source") or "/f" in mid or "/i" in mid or "/candidate" in mid,
                    f"Non-readable member ID: {mid}",
                )
                self.assertNotIn(" ", mid)
                self.assertLess(len(mid), 40)
                # Quote must be exact source slice or empty
                sid = m["source_id"]
                src = next(s for s in self.sources if s["source_id"] == sid)
                self.assertIn(m["candidate_quote"], src["note_text"])
                self.assertEqual(m["source_sha256"], src["source_sha256"])

    def test_missing_finding_enters_source_candidate_group(self):
        build_review_groups(
            sources_path=self.sources_path,
            annotations_path=self.annotations_path,
            candidates_path=None,
            all_sources_path=None,
            patterns_arg=None,
            out_dir=self.out_dir,
            expected=2,
        )
        groups = {
            g["group_id"]: g
            for g in [
                json.loads(line)
                for line in (self.out_dir / "groups.jsonl").read_text(encoding="utf-8").splitlines()
            ]
        }

        # Missing finding enters C03-candidates-without-findings
        self.assertIn("C03-candidates-without-findings", groups)
        c03_missing = groups["C03-candidates-without-findings"]["members"]
        self.assertTrue(
            any(
                m["member_id"] == "src_002/candidate002"
                and m["candidate_quote"] == "2 spells every week in childhood"
                for m in c03_missing
            )
        )

        # Also enters C05-potential-omissions
        self.assertIn("C05-potential-omissions", groups)
        c05_omissions = groups["C05-potential-omissions"]["members"]
        self.assertTrue(any(m["member_id"] == "src_002/candidate002" for m in c05_omissions))

    def test_every_finding_occurs_exactly_once_in_c03_inventory(self):
        build_review_groups(
            sources_path=self.sources_path,
            annotations_path=self.annotations_path,
            candidates_path=None,
            all_sources_path=None,
            patterns_arg=None,
            out_dir=self.out_dir,
            expected=2,
        )
        groups = [
            json.loads(line)
            for line in (self.out_dir / "groups.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        std_types = ["rate", "count", "cluster", "qualitative", "seizure_free", "last_seizure"]

        c03_finding_members = []
        for g in groups:
            if g["check_id"] == "C03" and g["group_id"].replace("C03-", "") in std_types:
                c03_finding_members.extend(g["members"])

        # 3 findings total: src_001/f1 (rate), src_001/f2 (last_seizure), src_002/f1 (seizure_free)
        self.assertEqual(len(c03_finding_members), 3)
        member_ids = [m["member_id"] for m in c03_finding_members]
        self.assertEqual(sorted(member_ids), ["src_001/f1", "src_001/f2", "src_002/f1"])
        self.assertEqual(len(member_ids), len(set(member_ids)))

    def test_nonexistent_quote_rejected(self):
        bad_ann = json.loads(json.dumps(self.annotations))
        bad_ann[0]["findings"][0]["evidence"] = "Invented phrase not in text"
        self.annotations_path.write_text(
            "".join(json.dumps(a) + "\n" for a in bad_ann), encoding="utf-8"
        )

        with self.assertRaises(ValueError) as ctx:
            build_review_groups(
                sources_path=self.sources_path,
                annotations_path=self.annotations_path,
                candidates_path=None,
                all_sources_path=None,
                patterns_arg=None,
                out_dir=self.out_dir,
                expected=2,
            )
        self.assertIn("not exact slice", str(ctx.exception))
        # Ensure no partial review groups were written
        self.assertFalse((self.out_dir / "groups.jsonl").exists())

    def test_duplicate_source_id_rejected(self):
        dup_sources = list(self.sources) + [self.sources[0]]
        self.sources_path.write_text(
            "".join(json.dumps(s) + "\n" for s in dup_sources), encoding="utf-8"
        )

        with self.assertRaises(ValueError) as ctx:
            build_review_groups(
                sources_path=self.sources_path,
                annotations_path=self.annotations_path,
                candidates_path=None,
                all_sources_path=None,
                patterns_arg=None,
                out_dir=self.out_dir,
                expected=2,
            )
        self.assertIn("Duplicate source_id", str(ctx.exception))
        self.assertFalse((self.out_dir / "groups.jsonl").exists())

    def test_duplicate_finding_id_rejected(self):
        bad_ann = json.loads(json.dumps(self.annotations))
        bad_ann[0]["findings"][1]["id"] = "f1"  # duplicate id f1
        self.annotations_path.write_text(
            "".join(json.dumps(a) + "\n" for a in bad_ann), encoding="utf-8"
        )

        with self.assertRaises(ValueError) as ctx:
            build_review_groups(
                sources_path=self.sources_path,
                annotations_path=self.annotations_path,
                candidates_path=None,
                all_sources_path=None,
                patterns_arg=None,
                out_dir=self.out_dir,
                expected=2,
            )
        self.assertIn("Duplicate finding id", str(ctx.exception))
        self.assertFalse((self.out_dir / "groups.jsonl").exists())

    def test_wrong_hash_rejected(self):
        bad_sources = json.loads(json.dumps(self.sources))
        bad_sources[0]["source_sha256"] = (
            "0000000000000000000000000000000000000000000000000000000000000000"
        )
        self.sources_path.write_text(
            "".join(json.dumps(s) + "\n" for s in bad_sources), encoding="utf-8"
        )

        with self.assertRaises(ValueError) as ctx:
            build_review_groups(
                sources_path=self.sources_path,
                annotations_path=self.annotations_path,
                candidates_path=None,
                all_sources_path=None,
                patterns_arg=None,
                out_dir=self.out_dir,
                expected=2,
            )
        self.assertIn("Hash mismatch", str(ctx.exception))
        self.assertFalse((self.out_dir / "groups.jsonl").exists())

    def test_identical_source_text_retains_separate_valid_source_ids(self):
        text = "Identical clinical summary: 1 seizure every week."
        sha = sha256_text(text)
        src_a = {
            "source_id": "src_dup_a",
            "source_row_index": 1,
            "note_text": text,
            "source_sha256": sha,
        }
        src_b = {
            "source_id": "src_dup_b",
            "source_row_index": 2,
            "note_text": text,
            "source_sha256": sha,
        }
        ann_a = {
            "source_id": "src_dup_a",
            "source_row_index": 1,
            "source_sha256": sha,
            "findings": [
                {"id": "f1", "evidence": "1 seizure every week", "measurement": {"type": "rate"}}
            ],
            "source_checks": [{"evidence": "1 seizure every week", "finding_ids": ["f1"]}],
        }
        ann_b = {
            "source_id": "src_dup_b",
            "source_row_index": 2,
            "source_sha256": sha,
            "findings": [
                {"id": "f1", "evidence": "1 seizure every week", "measurement": {"type": "rate"}}
            ],
            "source_checks": [{"evidence": "1 seizure every week", "finding_ids": ["f1"]}],
        }
        p_src = self.dir / "dup_sources.jsonl"
        p_ann = self.dir / "dup_ann.jsonl"
        p_out = self.dir / "dup_out"
        p_src.write_text(json.dumps(src_a) + "\n" + json.dumps(src_b) + "\n", encoding="utf-8")
        p_ann.write_text(json.dumps(ann_a) + "\n" + json.dumps(ann_b) + "\n", encoding="utf-8")

        build_review_groups(
            sources_path=p_src,
            annotations_path=p_ann,
            candidates_path=None,
            all_sources_path=None,
            patterns_arg=None,
            out_dir=p_out,
            expected=2,
        )
        groups = {
            g["group_id"]: g
            for g in [
                json.loads(line)
                for line in (p_out / "groups.jsonl").read_text(encoding="utf-8").splitlines()
            ]
        }

        self.assertIn("C02-identical_source-001", groups)
        m_ids = [m["member_id"] for m in groups["C02-identical_source-001"]["members"]]
        self.assertIn("src_dup_a/source", m_ids)
        self.assertIn("src_dup_b/source", m_ids)
        self.assertEqual(len(m_ids), 2)
        # Empty quote and valid source sha256
        for m in groups["C02-identical_source-001"]["members"]:
            self.assertEqual(m["candidate_quote"], "")
            self.assertEqual(m["source_sha256"], sha)

    def test_c08_respects_full_source_scope_and_retains_exact_snippets(self):
        # All sources includes a third source not in the primary 2-source set
        note_3 = "Patient recorded 4 seizure-days during last month."
        sha_3 = sha256_text(note_3)
        src_3 = {
            "source_id": "src_003_extra",
            "source_row_index": 3,
            "note_text": note_3,
            "source_sha256": sha_3,
        }
        all_sources = list(self.sources) + [src_3]
        all_sources_path = self.dir / "all_sources.jsonl"
        all_sources_path.write_text(
            "".join(json.dumps(s) + "\n" for s in all_sources), encoding="utf-8"
        )

        patterns = [
            {"id": "seizure-days-prop", "regex": r"(?i)seizure[ -]days?", "rule_ids": ["D08"]}
        ]
        pat_path = self.dir / "patterns.json"
        pat_path.write_text(json.dumps(patterns), encoding="utf-8")

        summary = build_review_groups(
            sources_path=self.sources_path,
            annotations_path=self.annotations_path,
            candidates_path=None,
            all_sources_path=all_sources_path,
            patterns_arg=str(pat_path),
            out_dir=self.out_dir,
            expected=2,
        )

        groups = {
            g["group_id"]: g
            for g in [
                json.loads(line)
                for line in (self.out_dir / "groups.jsonl").read_text(encoding="utf-8").splitlines()
            ]
        }
        self.assertIn("C08-seizure-days-prop", groups)
        c08_group = groups["C08-seizure-days-prop"]
        self.assertEqual(c08_group["semantic_review"], "PENDING")
        self.assertEqual(c08_group["scope"], "all_sources")
        self.assertEqual(summary["c08_source_count"], 3)

        # Match from extra source in all_sources is found and retains exact snippet
        m_extra = next(m for m in c08_group["members"] if m["source_id"] == "src_003_extra")
        self.assertIn("seizure-days", m_extra["candidate_quote"])
        self.assertIn(m_extra["candidate_quote"], note_3)
        self.assertEqual(m_extra["member_id"], "src_003_extra/candidate001")

    def test_missing_correction_patterns_means_c08_pending(self):
        build_review_groups(
            sources_path=self.sources_path,
            annotations_path=self.annotations_path,
            candidates_path=None,
            all_sources_path=None,
            patterns_arg=None,
            out_dir=self.out_dir,
            expected=2,
        )
        groups = {
            g["group_id"]: g
            for g in [
                json.loads(line)
                for line in (self.out_dir / "groups.jsonl").read_text(encoding="utf-8").splitlines()
            ]
        }
        self.assertIn("C08-pending", groups)
        self.assertEqual(groups["C08-pending"]["members"], [])
        self.assertEqual(groups["C08-pending"]["review_state"], "pending")
        self.assertEqual(groups["C08-pending"]["semantic_review"], "PENDING")

    def test_cli_execution_success_and_failure(self):
        script_path = Path(__file__).resolve().parent / "build_review_groups.py"
        # CLI Success
        res = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--sources",
                str(self.sources_path),
                "--annotations",
                str(self.annotations_path),
                "--out",
                str(self.out_dir),
                "--expected",
                "2",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, f"CLI stderr: {res.stderr}")
        self.assertTrue((self.out_dir / "groups.jsonl").is_file())

        # CLI Failure when expected mismatch (e.g. default 750 vs 2)
        fail_out = self.dir / "fail_out"
        res_fail = subprocess.run(
            [
                sys.executable,
                str(script_path),
                "--sources",
                str(self.sources_path),
                "--annotations",
                str(self.annotations_path),
                "--out",
                str(fail_out),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res_fail.returncode, 0)
        self.assertIn("Expected 750 sources, found 2", res_fail.stderr)
        self.assertFalse(fail_out.exists())

    def test_empty_source_candidate_inventory_is_valid(self):
        self.candidates_path.write_text(
            json.dumps({"source_id": "src_001", "candidate_quotes": []}) + "\n"
        )
        build_review_groups(
            self.sources_path,
            self.annotations_path,
            self.candidates_path,
            None,
            None,
            self.dir / "empty_candidates_out",
            expected=2,
        )

    def test_raw_source_backstop_finds_unlisted_claim(self):
        records = [json.loads(line) for line in self.annotations_path.read_text().splitlines()]
        for record in records:
            record["source_checks"] = []
        self.annotations_path.write_text("".join(json.dumps(r) + "\n" for r in records))
        out = self.dir / "raw_backstop_out"
        build_review_groups(
            self.sources_path, self.annotations_path, None, None, None, out, expected=2
        )
        groups = [json.loads(line) for line in (out / "groups.jsonl").read_text().splitlines()]
        missing = next(g for g in groups if g["group_id"] == "C03-candidates-without-findings")
        self.assertTrue(
            any("2 spells every week" in m["candidate_quote"] for m in missing["members"])
        )

    def test_wrong_annotation_row_index_rejected_before_output(self):
        records = [json.loads(line) for line in self.annotations_path.read_text().splitlines()]
        records[0]["source_row_index"] = 999
        self.annotations_path.write_text("".join(json.dumps(r) + "\n" for r in records))
        out = self.dir / "bad_index_out"
        with self.assertRaisesRegex(ValueError, "source_row_index mismatch"):
            build_review_groups(
                self.sources_path, self.annotations_path, None, None, None, out, expected=2
            )
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
