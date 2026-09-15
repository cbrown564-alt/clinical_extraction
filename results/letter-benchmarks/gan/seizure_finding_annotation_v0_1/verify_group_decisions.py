"""Fictional membership checks; these do not test semantic correctness."""

import copy
import unittest

from expand_group_review import expand


class Decisions(unittest.TestCase):
    def setUp(self):
        self.groups = [
            {
                "group_id": "C01-coverage",
                "members": [{"member_id": "fictional/f1"}, {"member_id": "fictional/f2"}],
            }
        ]
        self.report = {
            "group_reviews": [
                {
                    "group_id": "C01-coverage",
                    "apply_to_all_members": True,
                    "outcome": "consistent",
                    "rule_ids": ["D01"],
                    "reason": "Fictional checked comparison.",
                    "exceptions": [],
                }
            ]
        }

    def test_explicit_decision_expands_exactly(self):
        self.report["group_reviews"][0]["exceptions"] = [
            {
                "member_ids": ["fictional/f2"],
                "outcome": "unresolved",
                "rule_ids": ["D12"],
                "reason": "Fictional source ambiguity.",
                "issue_ids": ["i1"],
            }
        ]
        result = expand(self.groups, self.report)[0]["comparisons"]
        self.assertEqual([c["member_ids"] for c in result], [["fictional/f1"], ["fictional/f2"]])
        self.assertEqual(result[1]["outcome"], "unresolved")

    def test_reject_missing_duplicate_unknown_group(self):
        for records in [
            [],
            self.report["group_reviews"] * 2,
            [{**self.report["group_reviews"][0], "group_id": "unknown"}],
        ]:
            with self.assertRaises(ValueError):
                expand(self.groups, {"group_reviews": records})

    def test_reject_unknown_duplicate_exception(self):
        for ids in [["missing"], ["fictional/f1", "fictional/f1"]]:
            r = copy.deepcopy(self.report)
            r["group_reviews"][0]["exceptions"] = [{"member_ids": ids}]
            with self.assertRaises(ValueError):
                expand(self.groups, r)

    def test_reject_implicit_or_incomplete_judgement(self):
        for key, value in [
            ("apply_to_all_members", False),
            ("reason", ""),
            ("rule_ids", []),
            ("outcome", "probably"),
        ]:
            r = copy.deepcopy(self.report)
            r["group_reviews"][0][key] = value
            with self.assertRaises(ValueError):
                expand(self.groups, r)

    def test_empty_group_preserves_explicit_search_decision(self):
        self.groups[0]["members"] = []
        self.report["group_reviews"][0]["reason"] = "Search found no fictional candidates."
        result = expand(self.groups, self.report)[0]["comparisons"]
        self.assertEqual(result[0]["member_ids"], [])
        self.assertIn("Search", result[0]["reason"])


if __name__ == "__main__":
    unittest.main()
