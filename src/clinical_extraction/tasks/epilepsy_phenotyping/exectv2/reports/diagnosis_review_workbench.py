"""Generate a self-contained local Diagnosis review workbench."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_TEMPLATE = Path(__file__).with_name("templates") / "diagnosis_review_workbench.html"


def build_review_workbench(
    *,
    audit_jsonl: Path,
    summary_json: Path,
    out_html: Path,
    template_path: Path = DEFAULT_TEMPLATE,
) -> Path:
    """Embed audit rows and provenance into one offline HTML file."""

    rows = [
        json.loads(line)
        for line in audit_jsonl.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    summary: dict[str, Any] = json.loads(summary_json.read_text(encoding="utf-8"))
    expected = summary.get("union", {}).get("review_row_count")
    if expected is not None and expected != len(rows):
        raise ValueError(f"audit row count mismatch: summary={expected}, jsonl={len(rows)}")

    template = template_path.read_text(encoding="utf-8")
    rendered = template.replace(
        "__AUDIT_DATA__",
        _safe_embedded_json(rows),
    ).replace(
        "__AUDIT_SUMMARY__",
        _safe_embedded_json(summary),
    )
    if rendered == template or "__AUDIT_DATA__" in rendered or "__AUDIT_SUMMARY__" in rendered:
        raise ValueError("review workbench template is missing an embed placeholder")

    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(rendered, encoding="utf-8")
    return out_html


def _safe_embedded_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

