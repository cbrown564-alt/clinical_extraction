"""Pure-HTML helpers for the supervisor handoff demo notebook."""

from __future__ import annotations

import html
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEMO_DIR = ROOT / "examples" / "demo"

_STYLE = """
<style>
.ce-demo {
  --ink: #1c2430;
  --muted: #5c6b7a;
  --line: #d5dde6;
  --panel: #f4f7f8;
  --accent: #0f6a6a;
  --accent-soft: #d7efef;
  --warn: #8a5a12;
  --warn-soft: #f7e7c6;
  --ok: #1f6b3a;
  --bad: #8a2f2f;
  font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
  color: var(--ink);
  line-height: 1.45;
  margin: 0.4rem 0 1.2rem;
}
.ce-demo * { box-sizing: border-box; }
.ce-demo h3, .ce-demo h4 { margin: 0 0 0.55rem; font-weight: 600; letter-spacing: -0.01em; }
.ce-demo p { margin: 0.35rem 0; color: var(--muted); }
.ce-demo .ce-banner {
  display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap;
  padding: 0.85rem 1rem; border: 1px solid var(--line); background: var(--panel);
}
.ce-demo .ce-pill {
  display: inline-block; padding: 0.15rem 0.55rem; border: 1px solid var(--line);
  background: #fff; font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase;
}
.ce-demo .ce-pill.ok { border-color: #b7d7c2; background: #e8f6ec; color: var(--ok); }
.ce-demo .ce-pill.live { border-color: #b7d0d0; background: var(--accent-soft); color: var(--accent); }
.ce-demo .ce-letter {
  background: linear-gradient(165deg, #f8fbfa 0%, #eef3f6 100%);
  border-left: 4px solid var(--accent); padding: 1.1rem 1.25rem; white-space: pre-wrap;
  font-family: "IBM Plex Serif", Georgia, serif; font-size: 1.02rem; color: var(--ink);
}
.ce-demo .ce-mark {
  background: var(--warn-soft); color: var(--warn); padding: 0 0.15rem;
  box-decoration-break: clone;
}
.ce-demo .ce-card {
  border: 1px solid var(--line); padding: 1rem 1.1rem; background: #fff;
}
.ce-demo .ce-answer {
  font-size: 1.85rem; font-weight: 650; letter-spacing: -0.03em; margin: 0.2rem 0 0.7rem;
}
.ce-demo .ce-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.55rem; }
.ce-demo .ce-chip {
  font-size: 0.78rem; padding: 0.18rem 0.5rem; border: 1px solid var(--line); background: var(--panel);
}
.ce-demo .ce-chip.good { background: #e8f6ec; border-color: #b7d7c2; color: var(--ok); }
.ce-demo .ce-chip.bad { background: #f8e8e8; border-color: #e0b4b4; color: var(--bad); }
.ce-demo .ce-meta { font-size: 0.9rem; color: var(--muted); }
.ce-demo .ce-steps { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 0.45rem; }
.ce-demo .ce-step {
  border: 1px solid var(--line); padding: 0.65rem 0.55rem; background: #fff; min-height: 5.5rem;
}
.ce-demo .ce-step.changed { border-color: #9ecaca; background: #f3fbfb; }
.ce-demo .ce-step .n { font-size: 0.72rem; color: var(--muted); letter-spacing: 0.06em; text-transform: uppercase; }
.ce-demo .ce-step .t { font-weight: 600; margin: 0.2rem 0; }
.ce-demo .ce-step .s { font-size: 0.82rem; color: var(--muted); }
.ce-demo .ce-detail {
  margin-top: 0.65rem; border-top: 1px solid var(--line); padding-top: 0.65rem;
}
.ce-demo .ce-detail-item { margin: 0.45rem 0; padding: 0.55rem 0.7rem; background: var(--panel); }
.ce-demo .ce-compare {
  display: grid; grid-template-columns: 1fr auto 1fr; gap: 0.75rem; align-items: stretch;
}
.ce-demo .ce-arrow {
  align-self: center; text-align: center; color: var(--accent); font-weight: 700; font-size: 1.4rem;
}
.ce-demo .ce-table { width: 100%; border-collapse: collapse; font-size: 0.92rem; }
.ce-demo .ce-table th, .ce-demo .ce-table td {
  border-bottom: 1px solid var(--line); text-align: left; padding: 0.55rem 0.4rem; vertical-align: top;
}
.ce-demo .ce-table th { color: var(--muted); font-weight: 600; font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; }
.ce-demo .ce-bars { display: flex; gap: 0.35rem; margin: 0.7rem 0 0.2rem; }
.ce-demo .ce-bar { height: 0.55rem; flex: 1; background: #dfe7ea; }
.ce-demo .ce-bar.ok { background: #3f9a63; }
.ce-demo .ce-bar.partial { background: #c4922c; }
.ce-demo .ce-bar.error { background: #b45454; }
.ce-demo .ce-families { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.55rem; }
.ce-demo .ce-family { border: 1px solid var(--line); padding: 0.7rem 0.8rem; background: #fff; }
.ce-demo .ce-family h4 { font-size: 0.78rem; letter-spacing: 0.05em; text-transform: uppercase; color: var(--muted); }
.ce-demo .ce-family .v { font-size: 1.05rem; font-weight: 600; margin: 0.25rem 0; }
.ce-demo .ce-cli {
  display: grid; gap: 0.35rem; font-family: ui-monospace, "Cascadia Mono", Consolas, monospace;
  font-size: 0.84rem; background: #18212b; color: #e7eef5; padding: 0.9rem 1rem;
}
.ce-demo .ce-cli span { color: #8fd0c8; }
@media (max-width: 860px) {
  .ce-demo .ce-steps, .ce-demo .ce-compare, .ce-demo .ce-families { grid-template-columns: 1fr; }
  .ce-demo .ce-arrow { transform: rotate(90deg); }
}
</style>
"""


def _esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _wrap(body: str) -> str:
    return f"{_STYLE}<div class='ce-demo'>{body}</div>"


def show(html_fragment: str) -> Any:
    """Display HTML in a notebook, or return the fragment when IPython is absent."""
    try:
        from IPython.display import HTML, display
    except ImportError:
        return html_fragment
    display(HTML(html_fragment))
    return None


def load_json(name: str) -> Any:
    return json.loads((DEMO_DIR / name).read_text(encoding="utf-8"))


def load_jsonl(name: str) -> list[dict[str, Any]]:
    path = DEMO_DIR / name
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def mode_banner(*, prepared: bool = True) -> str:
    pill = "prepared" if prepared else "live"
    klass = "ok" if prepared else "live"
    detail = (
        "No model call. Synthetic fixtures only."
        if prepared
        else "Uses your .env endpoint. Notes leave this process through that route."
    )
    return _wrap(
        f"<div class='ce-banner'><span class='ce-pill {klass}'>{_esc(pill)}</span>"
        f"<div><h3 style='margin:0'>Handoff demo</h3><p style='margin:0'>{_esc(detail)}</p></div></div>"
    )


def cli_cheatsheet() -> str:
    rows = [
        ("check", "Probe endpoint with one synthetic note"),
        ("seizure-frequency --input … --output …", "Current seizure-frequency workflow"),
        ("clinical-findings --input … --output …", "Four-family findings workflow"),
        ("show-config", "Print non-secret resolved settings"),
    ]
    body = "".join(
        f"<div><span>python run.py {_esc(cmd)}</span>  # {_esc(note)}</div>" for cmd, note in rows
    )
    return _wrap(f"<h3>Same steps as the CLI</h3><div class='ce-cli'>{body}</div>")


def letter_html(text: str, evidence: str | None = None, *, title: str = "Letter") -> str:
    rendered = _esc(text)
    if evidence:
        needle = _esc(evidence)
        if needle and needle in rendered:
            rendered = rendered.replace(
                needle, f"<mark class='ce-mark'>{needle}</mark>", 1
            )
    return _wrap(f"<h3>{_esc(title)}</h3><div class='ce-letter'>{rendered}</div>")


def _result_card_body(result: Mapping[str, Any], *, title: str = "Result") -> str:
    value = result.get("value", "—")
    kind = result.get("kind", "")
    evidence = result.get("evidence", "")
    exact = bool(result.get("evidence_exact"))
    owner = result.get("first_prediction_owner", "")
    changes = list(result.get("deterministic_changes") or [])
    exact_chip = (
        "<span class='ce-chip good'>evidence exact</span>"
        if exact
        else "<span class='ce-chip bad'>evidence not exact</span>"
    )
    change_note = (
        f"<p class='ce-meta'>Deterministic changes: {_esc(len(changes))}</p>"
        if changes
        else "<p class='ce-meta'>No deterministic label change recorded.</p>"
    )
    return (
        f"<div class='ce-card'><h3>{_esc(title)}</h3>"
        f"<div class='ce-answer'>{_esc(value)}</div>"
        f"<div class='ce-chips'>"
        f"<span class='ce-chip'>kind {_esc(kind)}</span>"
        f"<span class='ce-chip'>owner {_esc(owner)}</span>"
        f"{exact_chip}</div>"
        f"<p class='ce-meta'>Evidence: {_esc(evidence) or '—'}</p>"
        f"{change_note}</div>"
    )


def result_card(result: Mapping[str, Any], *, title: str = "Result") -> str:
    return _wrap(_result_card_body(result, title=title))


def stage_stepper(stages: Sequence[Mapping[str, Any]]) -> str:
    tiles = []
    details = []
    for index, stage in enumerate(stages, start=1):
        changed = bool(stage.get("changed"))
        klass = "changed" if changed else ""
        tiles.append(
            "<div class='ce-step "
            f"{klass}'><div class='n'>Step {index}</div>"
            f"<div class='t'>{_esc(stage.get('title'))}</div>"
            f"<div class='s'>{_esc(stage.get('summary'))}</div></div>"
        )
        if changed:
            details.append(
                "<div class='ce-detail-item'><strong>"
                f"{_esc(stage.get('title'))}</strong>"
                f"<div class='ce-meta'>{_esc(stage.get('detail'))}</div></div>"
            )
    detail_block = (
        f"<div class='ce-detail'><h4>Changed stages</h4>{''.join(details)}</div>"
        if details
        else ""
    )
    return _wrap(
        f"<h3>Pipeline stages</h3><div class='ce-steps'>{''.join(tiles)}</div>{detail_block}"
    )


def punchline_compare(before: Mapping[str, Any], after: Mapping[str, Any]) -> str:
    return _wrap(
        "<h3>Why rules mattered on this letter</h3>"
        "<div class='ce-compare'>"
        f"<div>{_result_card_body(before, title='Model first choice')}</div>"
        "<div class='ce-arrow'>→</div>"
        f"<div>{_result_card_body(after, title='After named repair')}</div>"
        "</div>"
        "<p>Repair <code>typical_over_ytd</code> prefers the stated typical monthly "
        "pattern over the year-to-date count.</p>"
    )


def batch_table(rows: Sequence[Mapping[str, Any]]) -> str:
    body_rows = []
    statuses: list[str] = []
    for row in rows:
        status = str(row.get("status", "ok"))
        statuses.append(status)
        result = row.get("result") or {}
        body_rows.append(
            "<tr>"
            f"<td>{_esc(row.get('id'))}</td>"
            f"<td>{_esc(result.get('value', '—'))}</td>"
            f"<td>{_esc(result.get('kind', ''))}</td>"
            f"<td>{_esc(status)}</td>"
            "</tr>"
        )
    bars = "".join(f"<div class='ce-bar {_esc(status)}'></div>" for status in statuses)
    return _wrap(
        "<h3>Glance batch</h3>"
        f"<div class='ce-bars' title='one bar per note'>{bars}</div>"
        "<table class='ce-table'><thead><tr>"
        "<th>id</th><th>answer</th><th>kind</th><th>status</th>"
        "</tr></thead><tbody>"
        f"{''.join(body_rows)}</tbody></table>"
    )


def findings_cards(result: Mapping[str, Any]) -> str:
    families = (
        ("diagnoses", "Diagnosis"),
        ("seizure_frequencies", "Seizure frequency"),
        ("prescriptions", "Prescription"),
        ("investigations", "Investigations"),
    )
    cards = []
    for key, label in families:
        items = list(result.get(key) or [])
        if not items:
            value = "—"
            evidence = ""
        else:
            value = items[0].get("value", "—")
            evidence = items[0].get("evidence", "")
            if len(items) > 1:
                value = f"{value} (+{len(items) - 1})"
        cards.append(
            "<div class='ce-family'><h4>"
            f"{_esc(label)}</h4><div class='v'>{_esc(value)}</div>"
            f"<div class='ce-meta'>{_esc(evidence) or 'No evidence'}</div></div>"
        )
    return _wrap(f"<h3>Four-family findings</h3><div class='ce-families'>{''.join(cards)}</div>")


def files_footer(*, output_name: str = "results.jsonl") -> str:
    return _wrap(
        "<h3>Where results go</h3>"
        f"<p>The CLI writes each note as one JSONL row to <code>{_esc(output_name)}</code>. "
        "Default rows include the public result only. Optional "
        "<code>--trace-output</code> adds private prompts and raw model content.</p>"
        "<p>Field meanings: <code>docs/OUTPUTS.md</code>.</p>"
    )
