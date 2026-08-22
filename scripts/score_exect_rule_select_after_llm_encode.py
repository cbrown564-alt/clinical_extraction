#!/usr/bin/env python3
"""Replay accepted Select rules on saved Gemini later-stage encode rows."""

from __future__ import annotations

import argparse
import json

from clinical_extraction.paper.exect_rule_select_after_encode import (
    replay_rule_select_after_llm_encode,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", choices=("dev140", "test60"), required=True)
    args = parser.parse_args()
    artifact = replay_rule_select_after_llm_encode(args.split)
    print(
        json.dumps(
            {
                "split": artifact["split"],
                "row_policy": artifact["row_policy"],
                "encode_f1": artifact["encode_stop"]["four_family_headline_f1"],
                "select_f1": artifact["select_stop"]["four_family_headline_f1"],
                "select_action_count": artifact["select_stop"]["select_action_count"],
                "artifact_path": artifact["artifact_path"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
