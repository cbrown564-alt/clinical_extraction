"""Render a standalone HTML inspection report: gold vs. prediction for the
EXECT-V2 SeizureFrequency task, for every dev140 letter.

Purpose (see ``docs/experiments/exectv2/seizure_frequency/``): give a human a way
to inspect *every* letter in detail, per schema attribute and per scoring
component, and see the prediction-transformation chain (closed-vocab validation,
format canonicalization, state projection, key construction) the scorer applies
before deciding right/wrong -- so it is legible where the model gets it right and
where it gets it wrong.

Computation is delegated entirely to
``clinical_extraction.tasks.epilepsy_phenotyping.exectv2.sf_inspection`` -- the
same module the live Observatory endpoint (``GET /exectv2/sf-inspection``) and
the frontend ``/exectv2-sf-inspection`` route consume. The faithfulness gate
(re-scores all 140 letters and aborts unless the aggregate F1 reproduces the
published 0.9338 / 0.8602 / 0.9244 within 1e-4) runs inside the builder, so this
report and the served payload can never drift.

This offline HTML is retained as a fallback for environments without the
frontend running; the frontend route is the primary surface.

Usage:
  python scripts/render_exectv2_sf_inspection_html.py
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.sf_inspection import (
    COMPONENT_ORDER,
    build_sf_inspection_payload,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
DATESTR = "20260708"
OUTPUT_HTML = EXPERIMENTS / f"exectv2_sf_inspection_dev140_{DATESTR}.html"


# ---------------------------------------------------------------------------
# HTML escaping helpers.
# ---------------------------------------------------------------------------
def esc(text: Any) -> str:
    return html.escape(str(text), quote=True)


def _fmt(value: str) -> str:
    return esc(value) if value else "—"


# ---------------------------------------------------------------------------
# Render: header scorecard.
# ---------------------------------------------------------------------------
def _scorecard_html(scorecard: dict[str, dict[str, Any]]) -> str:
    rows = []
    for name in COMPONENT_ORDER:
        s = scorecard[name]
        rows.append(
            f"<tr><td class='comp'>{esc(name)}</td>"
            f"<td>{s['f1']:.4f}</td><td>{s['precision']:.4f}</td><td>{s['recall']:.4f}</td>"
            f"<td>{s['tp']}</td><td>{s['fp']}</td><td>{s['fn']}</td></tr>"
        )
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# Render: Layer A (schema attributes) for one letter.
# ---------------------------------------------------------------------------
def _attr_table_html(pairs: list[dict[str, Any]]) -> str:
    if not pairs:
        return "<p class='empty'>No SeizureFrequency mentions (gold or prediction) for this letter.</p>"

    header = (
        "<p class='layer-note'><b>Layer A — schema attributes.</b> "
        "Gold↔prediction pairs use the scorer's max-cardinality phrase-overlap matcher. "
        "For each predicted attribute the chain shown is: "
        "<b>raw</b> → <b>closed-vocab validity</b> → <b>canonicalized</b> (quote/whitespace strip; "
        "lowercase only for DrugName/DoseUnit) → compared to gold's canonicalized value. "
        "Out-of-vocab or unexpected attributes are flagged.</p>"
    )
    return header + "".join(_attr_pair_html(p) for p in pairs)


def _attr_pair_html(pair: dict[str, Any]) -> str:
    label = pair["label"]
    side_cls = pair["side"]
    phrase_row = (
        f"<tr class='phrase-row'><td class='attr'>text (normalized)</td>"
        f"<td>{esc(pair['gold_phrase'])} → {esc(pair['gold_normalized'])}</td>"
        f"<td class='raw'>{esc(pair['pred_phrase'])}</td>"
        f"<td class='valid ok'>—</td>"
        f"<td class='canon'>{esc(pair['pred_normalized'])}</td>"
        f"<td class='match {_match_cls(pair['phrase_match'])}'>{_match_sym(pair['phrase_match'])}</td></tr>"
    )
    attr_rows = "".join(_attr_row_html(a) for a in pair["attributes"])
    return (
        f"<div class='pair {side_cls}'>"
        f"<div class='pair-label'>{esc(label)}</div>"
        "<table class='attr-table'><thead><tr>"
        "<th>attribute</th><th>gold (raw)</th><th>pred (raw)</th>"
        "<th>pred validity</th><th>pred canonicalized</th><th>match</th>"
        "</tr></thead><tbody>"
        f"{phrase_row}"
        f"{attr_rows}"
        "</tbody></table></div>"
    )


def _attr_row_html(attr: dict[str, Any]) -> str:
    return (
        f"<tr><td class='attr'>{esc(attr['key'])}</td>"
        f"<td>{_fmt(attr['gold'])}</td>"
        f"<td class='raw'>{_fmt(attr['pred'])}</td>"
        f"<td class='valid {_valid_cls(attr['validity'])}'>{_valid_label(attr['validity'])}</td>"
        f"<td class='canon'>{esc(attr['canonical']) if attr['canonical'] else '—'}</td>"
        f"<td class='match {_match_cls(attr['match'])}'>{_match_sym(attr['match'])}</td></tr>"
    )


def _valid_cls(validity: str) -> str:
    return {"ok": "ok", "absent": "absent", "illegal_value": "bad",
            "illegal_attr": "bad", "noise": "noise"}[validity]


def _valid_label(validity: str) -> str:
    return {"ok": "ok", "absent": "—", "illegal_value": "OUT OF VOCAB",
            "illegal_attr": "ILLEGAL ATTR", "noise": "noise attr"}[validity]


def _match_sym(match: str) -> str:
    return {"ok": "✓", "bad": "✗", "absent": "—"}[match]


def _match_cls(match: str) -> str:
    return {"ok": "m-ok", "bad": "m-bad", "absent": "m-absent"}[match]


# ---------------------------------------------------------------------------
# Render: Layer B (scoring components) for one letter.
# ---------------------------------------------------------------------------
def _components_html(components: list[dict[str, Any]]) -> str:
    intro = (
        "<p class='layer-note'><b>Layer B — scoring components.</b> "
        "Each of the 11 FrequencyStateScores projects every mention through a different rule "
        "into a hashable key; letters are scored by multiset (order-independent) match. "
        "For each component the table shows each mention's attribute inputs → count-based state → "
        "the component's projected state → final key, with TP / FP / FN status for THIS letter.</p>"
    )
    return intro + "".join(_component_block_html(c) for c in components)


def _component_block_html(comp: dict[str, Any]) -> str:
    has_error = comp["has_error"]
    verdict = (
        f"<span class='verdict-ok'>clean (tp={comp['tp']})</span>"
        if not has_error
        else f"<span class='verdict-err'>tp={comp['tp']} · fp={comp['fp']} · fn={comp['fn']}</span>"
    )
    body_rows = "".join(_mention_row_html(r) for r in comp["rows"])
    if not body_rows:
        body_rows = "<tr><td colspan='8' class='empty'>no SeizureFrequency mentions</td></tr>"
    err_cls = "comp-error" if has_error else ""
    return (
        f"<div class='comp-block {err_cls}'>"
        f"<div class='comp-head'>"
        f"<span class='comp-name'>{esc(comp['name'])}</span> {verdict}"
        f"<span class='comp-info'>{esc(comp['info'])}</span>"
        f"</div>"
        "<table class='comp-table'><thead><tr>"
        "<th>side</th><th>phrase</th><th>counts (NS/L/U)</th><th>FrequencyChange</th>"
        "<th>count→state</th><th>projected state</th><th>final key</th><th>this letter</th>"
        "</tr></thead><tbody>"
        f"{body_rows}"
        "</tbody></table></div>"
    )


def _mention_row_html(row: dict[str, Any]) -> str:
    side = row["side"]
    if row["status"] == "skip":
        return (
            f"<tr class='{side} skip'>"
            f"<td class='side'>{side}</td>"
            f"<td class='phrase'>{esc(row['phrase'])}</td>"
            f"<td>{esc(row['counts'])}</td>"
            f"<td>{_fmt(row['frequency_change'])}</td>"
            f"<td>{_fmt(row['count_state'])}</td>"
            f"<td class='proj muted'>— filtered —</td>"
            f"<td class='keycol muted'>(no key)</td>"
            f"<td class='st-skip'>—</td>"
            f"</tr>"
        )
    status_cls = {"tp": "st-tp", "fp": "st-fp", "fn": "st-fn"}[row["status"]]
    status_label = {"tp": "TP", "fp": "FP", "fn": "FN"}[row["status"]]
    return (
        f"<tr class='{side}'>"
        f"<td class='side'>{side}</td>"
        f"<td class='phrase'>{esc(row['phrase'])}</td>"
        f"<td>{esc(row['counts'])}</td>"
        f"<td>{_fmt(row['frequency_change'])}</td>"
        f"<td>{_fmt(row['count_state'])}</td>"
        f"<td class='proj'>{esc(row['projected_state'])}</td>"
        f"<td class='keycol'><code>{esc(row['key'])}</code></td>"
        f"<td class='{status_cls}'>{status_label}</td>"
        f"</tr>"
    )


# ---------------------------------------------------------------------------
# Render: dictionary-lens / override provenance for one letter.
# ---------------------------------------------------------------------------
def _lineage_html(lineage: dict[str, Any]) -> str:
    spans = lineage["candidate_spans"]
    spans_html = (
        "<ul class='spans'>"
        + "".join(
            f"<li><code>{esc(c.get('text_hint', ''))}</code> "
            f"<span class='muted'>[{esc(c.get('candidate_type', ''))} · "
            f"{esc(c.get('source', ''))}]</span> "
            f"<span class='ev'>{esc(c.get('evidence', ''))}</span></li>"
            for c in spans[:8]
        )
        + ("</ul>" if spans else "<p class='empty'>no candidate_spans recorded</p>")
    )

    override = lineage.get("override")
    override_note = ""
    if override and override.get("applied"):
        items = "".join(
            f"<li><code>{esc(it.get('applies_to', ''))}</code>: "
            f"<b>{esc(it.get('prior_frequency_change') or '(none)')}</b> → "
            f"<b>{esc(it.get('assembled_magnitude', ''))}</b> "
            f"<span class='muted'>(selector {esc(it.get('selection_mode', ''))}, "
            f"candidate {esc(it.get('selected_candidate_id', ''))})</span></li>"
            for it in override.get("items", [])
        )
        override_note = (
            "<div class='override'>"
            "<b>LLM magnitude-complement override applied</b> "
            "(deterministic rules had no magnitude regex match here; "
            "gpt-4.1-mini selected the FrequencyChange label):"
            f"<ul>{items}</ul></div>"
        )
    elif override and not override.get("applied"):
        override_note = (
            "<div class='override muted'>FrequencyChange differs from baseline v08 "
            f"(baseline {override.get('baseline')} vs complement {override.get('complement')}).</div>"
        )

    note = (
        "<p class='layer-note'><b>Prediction lineage.</b> SeizureFrequency is rules-owned in "
        "this pipeline: the deterministic SeizureFrequencyDictionaryLens mapped candidate spans "
        "(phrase→CUI, count/range extraction, seizure-free/active-rate state inference) into the "
        "scored <code>predicted_mentions</code>. SF <code>draft_mentions</code> are empty in this "
        "lineage, so no raw-LLM-draft stage is shown. Where the magnitude complement fired, the "
        "LLM overwrote <code>FrequencyChange</code> on this letter's SF mentions — shown below.</p>"
    )
    return (
        f"<details class='lineage'><summary>Prediction lineage "
        f"({len(spans)} candidate span(s){', override applied' if override_note else ''})</summary>"
        f"{note}{override_note}"
        "<div class='subhead'>Candidate spans (decision_lane=active_rate)</div>"
        f"{spans_html}</details>"
    )


# ---------------------------------------------------------------------------
# Render: one letter section.
# ---------------------------------------------------------------------------
def _letter_html(letter: dict[str, Any]) -> str:
    lid = letter["letter_id"]
    if not letter["has_activity"]:
        return (
            f"<section class='letter empty-letter' id='{esc(lid)}'>"
            f"<details><summary class='let-head'>"
            f"<span class='lid'>{esc(lid)}</span> "
            f"<span class='muted'>no SeizureFrequency activity (gold or prediction)</span>"
            f"</summary></details></section>"
        )

    err_count = letter["total_errors"]
    d = letter["direction_errors"]
    m = letter["magnitude_errors"]
    open_attr = " open" if err_count else ""
    badge = (
        f"<span class='badge'>dir fp={d['fp']}/fn={d['fn']}</span>"
        f"<span class='badge'>mag fp={m['fp']}/fn={m['fn']}</span>"
        f"<span class='badge-total'>{err_count} FP/FN across components</span>"
    )
    header = (
        f"<summary class='let-head'>"
        f"<span class='lid'>{esc(lid)}</span> "
        f"<span class='counts'>gold SF={letter['gold_count']} · pred SF={letter['pred_count']}</span> "
        f"{badge}"
        f"</summary>"
    )
    lineage = _lineage_html(letter["lineage"])
    layer_a = f"<div class='layer'><h3>Layer A · Schema attributes</h3>{_attr_table_html(letter['layer_a']['pairs'])}</div>"
    layer_b = f"<div class='layer'><h3>Layer B · Scoring components</h3>{_components_html(letter['layer_b']['components'])}</div>"

    return (
        f"<section class='letter' id='{esc(lid)}'>"
        f"<details{open_attr}>{header}"
        f"{lineage}{layer_a}{layer_b}"
        f"</details></section>"
    )


# ---------------------------------------------------------------------------
# Render: nav.
# ---------------------------------------------------------------------------
def _nav_html(letters: list[dict[str, Any]]) -> str:
    items = []
    for letter in letters:
        lid = letter["letter_id"]
        err = letter["total_errors"]
        empty = not letter["has_activity"]
        cls = "nav-item" + (" nav-err" if err else " nav-empty" if empty else "")
        if err:
            badge = f"<span class='nav-badge'>{err}</span>"
        elif empty:
            badge = "<span class='nav-badge nav-no'>no SF</span>"
        else:
            badge = "<span class='nav-badge nav-clean'>clean</span>"
        items.append(f"<a class='{cls}' href='#{esc(lid)}'><span class='nav-lid'>{esc(lid)}</span>{badge}</a>")
    return "\n".join(items)


# ---------------------------------------------------------------------------
# Main.
# ---------------------------------------------------------------------------
def main() -> None:
    # The builder runs the faithfulness gate (re-scores dev140 with the real
    # score_frequency_state and raises on drift). No gate logic lives here.
    payload = build_sf_inspection_payload()
    print(
        "[sf-inspection] faithfulness gate passed "
        f"({payload['scorecard']['state_profile']['f1']:.4f} / "
        f"{payload['scorecard']['state_profile_directional']['f1']:.4f} / "
        f"{payload['scorecard']['state_profile_magnitude']['f1']:.4f})."
    )

    scorecard = _scorecard_html(payload["scorecard"])
    nav = _nav_html(payload["letters"])
    letters = "\n".join(_letter_html(l) for l in payload["letters"])

    html_doc = _html_shell(
        scorecard=scorecard,
        nav=nav,
        letters=letters,
        n_letters=payload["n_letters"],
        n_with_errors=payload["n_with_errors"],
    )
    OUTPUT_HTML.write_text(html_doc, encoding="utf-8")
    print(f"[sf-inspection] wrote {OUTPUT_HTML.relative_to(ROOT)}")
    print(
        f"[sf-inspection] {payload['n_letters']} letters, "
        f"{payload['n_with_errors']} with >=1 component error."
    )


def _html_shell(*, scorecard: str, nav: str, letters: str, n_letters: int, n_with_errors: int) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>EXECT-V2 SeizureFrequency inspection — gold vs prediction (dev140)</title>
<style>
:root {{
  --bg:#f7f7f5; --ink:#1a1a1a; --muted:#6b6b6b; --line:#d9d9d4;
  --gold:#2f5d8a; --pred:#8a5d2f;
  --tp:#1b7a3d; --fp:#b3261e; --fn:#b3261e; --bad:#b3261e; --ok:#1b7a3d;
  --soft:#eef2f6; --soft2:#f3eee6;
}}
* {{ box-sizing:border-box; }}
body {{ font-family: ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; background:var(--bg); color:var(--ink); margin:0; font-size:13px; line-height:1.45; }}
h1,h2,h3 {{ font-family: ui-sans-serif,system-ui,Segoe UI,Roboto,sans-serif; }}
header.report {{ position:sticky; top:0; z-index:20; background:#fff; border-bottom:1px solid var(--line); padding:14px 18px; }}
header.report h1 {{ margin:0 0 4px; font-size:17px; }}
header.report .meta {{ color:var(--muted); font-size:12px; }}
.scorecard {{ margin:10px 0; overflow-x:auto; }}
.scorecard table {{ border-collapse:collapse; font-size:12px; background:#fff; }}
.scorecard th,.scorecard td {{ border:1px solid var(--line); padding:3px 8px; text-align:right; }}
.scorecard th {{ background:var(--soft); font-weight:600; }}
.scorecard td.comp,.scorecard th:first-child {{ text-align:left; }}
.scorecard tr:nth-child(odd) td {{ background:#fafafa; }}
.legend {{ display:flex; flex-wrap:wrap; gap:10px 18px; margin:8px 0 2px; font-size:12px; color:var(--muted); }}
.legend span b {{ color:var(--ink); }}
.controls {{ margin:6px 0; }}
.controls button {{ font:inherit; padding:4px 10px; margin-right:6px; cursor:pointer; border:1px solid var(--line); background:#fff; border-radius:3px; }}
.controls button:hover {{ background:var(--soft); }}
nav.letters {{ display:flex; flex-wrap:wrap; gap:4px; padding:8px 18px 14px; border-bottom:1px solid var(--line); background:#fff; position:sticky; top:auto; }}
.nav-item {{ display:inline-flex; align-items:center; gap:4px; text-decoration:none; color:var(--ink); border:1px solid var(--line); padding:2px 6px; border-radius:3px; background:#fff; }}
.nav-item:hover {{ background:var(--soft); }}
.nav-item.nav-err {{ border-color:#e3bfbf; background:#fbeeee; }}
.nav-item.nav-empty {{ opacity:.55; }}
.nav-lid {{ font-weight:600; }}
.nav-badge {{ font-size:10px; color:var(--fp); font-weight:700; }}
.nav-badge.nav-no,.nav-badge.nav-clean {{ color:var(--muted); font-weight:600; }}
main {{ padding:12px 18px 60px; }}
section.letter {{ background:#fff; border:1px solid var(--line); border-radius:4px; margin-bottom:8px; }}
section.letter details > summary {{ list-style:none; cursor:pointer; padding:8px 12px; }}
section.letter details > summary::-webkit-details-marker {{ display:none; }}
.let-head {{ display:flex; flex-wrap:wrap; align-items:center; gap:10px; }}
.lid {{ font-weight:700; font-size:14px; }}
.counts {{ color:var(--muted); font-size:12px; }}
.badge,.badge-total {{ font-size:11px; padding:1px 6px; border-radius:3px; background:#fbeeee; color:var(--fp); }}
.badge-total {{ background:#fdeede; color:#8a5d2f; }}
.empty-letter details > summary {{ color:var(--muted); }}
.layer {{ padding:4px 12px 10px; border-top:1px dashed var(--line); }}
.layer h3 {{ font-size:13px; margin:8px 0 4px; }}
.layer-note {{ color:var(--muted); font-size:12px; margin:6px 0 8px; max-width:1100px; }}
details.lineage {{ margin:8px 0; background:var(--soft); border:1px solid var(--line); border-radius:3px; padding:6px 10px; }}
details.lineage summary {{ cursor:pointer; font-weight:600; font-size:12px; }}
.subhead {{ font-size:11px; color:var(--muted); margin:8px 0 2px; text-transform:uppercase; letter-spacing:.04em; }}
ul.spans {{ margin:4px 0; padding-left:16px; }}
ul.spans li {{ margin:2px 0; }}
.ev {{ color:var(--muted); }}
.muted {{ color:var(--muted); }}
.override {{ background:#fff7e6; border:1px solid #e9d8a6; border-radius:3px; padding:6px 10px; margin:6px 0; font-size:12px; }}
.override ul {{ margin:4px 0; padding-left:16px; }}
.pair {{ border:1px solid var(--line); border-radius:3px; margin:8px 0; padding:6px 8px; }}
.pair.pair {{ border-left:3px solid var(--gold); }}
.pair.fn {{ border-left:3px solid var(--fn); background:#fdf3f3; }}
.pair.fp {{ border-left:3px solid var(--fp); background:#fdf3f3; }}
.pair-label {{ font-size:11px; font-weight:700; color:#8a5d2f; margin-bottom:4px; text-transform:uppercase; letter-spacing:.03em; }}
.pair.fn .pair-label {{ color:var(--fn); }}
.attr-table,.comp-table {{ border-collapse:collapse; width:100%; font-size:12px; }}
.attr-table th,.attr-table td,.comp-table th,.comp-table td {{ border:1px solid var(--line); padding:3px 6px; text-align:left; vertical-align:top; }}
.attr-table th,.comp-table th {{ background:var(--soft); font-weight:600; font-size:11px; }}
.attr-table .attr {{ font-weight:600; white-space:nowrap; }}
.attr-table .raw,.attr-table .canon {{ font-family:inherit; }}
.attr-table td.valid.bad {{ color:var(--bad); font-weight:700; }}
.attr-table td.valid.ok {{ color:var(--ok); }}
.attr-table td.valid.absent,.attr-table td.valid.noise {{ color:var(--muted); }}
.attr-table td.match.m-ok {{ color:var(--ok); font-weight:700; }}
.attr-table td.match.m-bad {{ color:var(--bad); font-weight:700; }}
.attr-table td.match.m-absent {{ color:var(--muted); }}
tr.phrase-row {{ background:var(--soft2); }}
.comp-block {{ margin:8px 0; border:1px solid var(--line); border-radius:3px; padding:6px 8px; }}
.comp-block.comp-error {{ border-color:#e3bfbf; background:#fffaf9; }}
.comp-head {{ font-size:12px; margin-bottom:4px; display:flex; flex-wrap:wrap; align-items:center; gap:8px; }}
.comp-name {{ font-weight:700; }}
.comp-info {{ color:var(--muted); font-size:11px; flex-basis:100%; }}
.verdict-ok {{ color:var(--ok); font-weight:600; }}
.verdict-err {{ color:var(--fp); font-weight:700; }}
.comp-table td.side {{ font-weight:600; width:42px; }}
.comp-table tr.gold td.side {{ color:var(--gold); }}
.comp-table tr.pred td.side {{ color:var(--pred); }}
.comp-table td.keycol {{ word-break:break-word; }}
.comp-table td.keycol code {{ font-size:11px; }}
.comp-table td.proj {{ font-weight:600; }}
.comp-table td.st-tp {{ color:var(--tp); font-weight:700; }}
.comp-table td.st-fp,.comp-table td.st-fn {{ color:var(--fp); font-weight:700; }}
.comp-table td.st-skip {{ color:var(--muted); }}
.comp-table tr.skip td {{ opacity:.5; }}
td.empty {{ color:var(--muted); text-align:center; padding:8px; }}
p.empty {{ color:var(--muted); padding:6px 0; }}
</style>
</head>
<body>
<header class="report">
  <h1>EXECT-V2 · SeizureFrequency · gold vs. prediction inspection (dev140)</h1>
  <div class="meta">
    Predictions: <code>exectv2_sf_magnitude_complement_dev140_20260708.jsonl</code> ·
    model gpt-4.1-mini (magnitude complement) · gold: <code>load_letters_for_split('dev')</code> ·
    {n_letters} letters · {n_with_errors} with ≥1 component error ·
    generated {DATESTR}.<br>
    Faithfulness gate: aggregate F1 reproduced within 1e-4 of the scorer (0.9338 / 0.8602 / 0.9244).
  </div>
  <div class="scorecard">
    <table>
      <thead><tr><th>component</th><th>F1</th><th>Precision</th><th>Recall</th><th>TP</th><th>FP</th><th>FN</th></tr></thead>
      <tbody>
      {scorecard}
      </tbody>
    </table>
  </div>
  <div class="legend">
    <span><b>Layer A</b> per schema attribute: raw → validity → canonicalized vs gold</span>
    <span><b>Layer B</b> per scoring component: attributes → count-state → projected state → key</span>
    <span><b style="color:var(--gold)">gold</b> / <b style="color:var(--pred)">pred</b></span>
    <span><b style="color:var(--tp)">TP</b> match · <b style="color:var(--fp)">FP</b> pred-only · <b style="color:var(--fn)">FN</b> gold-only · <b style="color:var(--bad)">OUT OF VOCAB</b></span>
  </div>
  <div class="controls">
    <button onclick="toggleAll(true)">Expand all</button>
    <button onclick="toggleAll(false)">Collapse all</button>
    <button id="errOnly" onclick="toggleErrorsOnly()">Errors only</button>
    <button onclick="jumpToFirstError()">First error</button>
  </div>
</header>
<nav class="letters">
{nav}
</nav>
<main>
{letters}
</main>
<script>
function toggleAll(open) {{
  document.querySelectorAll('section.letter details').forEach(d => d.open = open);
}}
function toggleErrorsOnly() {{
  const btn = document.getElementById('errOnly');
  const only = btn.dataset.on !== '1';
  btn.dataset.on = only ? '1' : '0';
  btn.textContent = only ? 'Show all' : 'Errors only';
  document.querySelectorAll('section.letter').forEach(s => {{
    const isErr = s.classList.contains('empty-letter') ? false : !!s.querySelector('.comp-error');
    const isEmpty = s.classList.contains('empty-letter');
    s.style.display = (only && (isErr)) || (only && !isEmpty && false) || !only ? '' : (only ? 'none' : '');
    if (only && isErr) {{ const d = s.querySelector('details'); if (d) d.open = true; }}
  }});
}}
function jumpToFirstError() {{
  const el = document.querySelector('.comp-error');
  if (el) {{ el.scrollIntoView({{behavior:'smooth',block:'start'}}); }}
}}
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
