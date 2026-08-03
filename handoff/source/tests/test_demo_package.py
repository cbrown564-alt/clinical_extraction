from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import demo_viz


def test_demo_fixtures_are_self_contained_and_renderable() -> None:
    deep = demo_viz.load_json("deep_letter.json")
    glance = demo_viz.load_json("glance_results.json")
    notes = demo_viz.load_jsonl("glance_notes.jsonl")
    findings = demo_viz.load_json("findings_letter.json")

    assert deep["id"] == "TEACH-GAN-01"
    assert deep["result"]["value"] == "1 per month"
    assert deep["model_first"]["value"] == "7 per year"
    assert deep["result"]["evidence"] in deep["text"]
    assert len(deep["stages"]) == 5
    assert len(notes) == 3
    assert [row["id"] for row in glance["rows"]] == [note["id"] for note in notes]
    assert findings["result"]["diagnoses"]
    assert findings["result"]["prescriptions"]

    html = "".join(
        [
            demo_viz.mode_banner(prepared=True),
            demo_viz.cli_cheatsheet(),
            demo_viz.letter_html(deep["text"], evidence=deep["result"]["evidence"]),
            demo_viz.result_card(deep["result"]),
            demo_viz.stage_stepper(deep["stages"]),
            demo_viz.punchline_compare(deep["model_first"], deep["result"]),
            demo_viz.batch_table(glance["rows"]),
            demo_viz.findings_cards(findings["result"]),
            demo_viz.files_footer(),
        ]
    )
    assert "ce-demo" in html
    assert "1 per month" in html
    assert "typical_over_ytd" in html


def test_demo_notebook_exists_and_mentions_prepared_path() -> None:
    notebook = json.loads((ROOT / "demo.ipynb").read_text(encoding="utf-8"))
    sources = "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])
    assert "demo_viz" in sources
    assert "RUN_LIVE" in sources
    assert "deep_letter.json" in sources
    assert "findings_letter.json" in sources
