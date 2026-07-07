"""Focused tests for the deterministic retrieval-highlight span helpers.

These two side-effect-free helpers carry the whole item-3 design: an offset bug
in either would silently mis-highlight (Arm B) or drop context (Arm C) and the
run would still produce numbers. They are pure functions over `note_text`, so we
test them with tiny hand-built fixtures per the TDD skill. The dspy signature and
apply-then-rescore plumbing are integration-shaped and mirror item 2 verbatim, so
they are not unit-tested here (matching item 2's convention).
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

# The driver is a standalone script under scripts/, not an installed package, so
# load it by path (mirroring how other scripts have been tested in this repo).
_SCRIPT = (
    Path(__file__).resolve().parents[1] / "scripts" / "run_exectv2_sf_retrieval_highlight_probe.py"
)
_spec = importlib.util.spec_from_file_location("run_exectv2_sf_retrieval_highlight_probe", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

select_highlight_spans = _mod.select_highlight_spans
render_highlighted_text = _mod.render_highlighted_text
render_highlight_only = _mod.render_highlight_only
HighlightSpan = _mod.HighlightSpan


# --------------------------------------------------------------------------------------
# select_highlight_spans
# --------------------------------------------------------------------------------------
class TestSelectHighlightSpans:
    def test_change_cue_produces_offset_span_with_evidence(self) -> None:
        text = "The seizure frequency has decreased since starting medication."
        spans = select_highlight_spans(text)
        # The change.decreased rule should fire on "seizure frequency has decreased".
        dec = [s for s in spans if s["rule_id"] == "change.decreased"]
        assert dec, "expected change.decreased to fire"
        start, end = dec[0]["start"], dec[0]["end"]
        # The span must be valid char offsets into the text.
        assert 0 <= start < end <= len(text)
        # And the evidence must equal the substring at those offsets.
        assert text[start:end] == dec[0]["evidence"]
        # And the evidence must contain the direction cue.
        assert "decreased" in dec[0]["evidence"].lower()

    def test_temporal_cue_produces_offset_span(self) -> None:
        # A temporal "last seizure was <date>" anchor should fire.
        text = "She had no seizures since her last clinic in 2020, now 3 per month."
        spans = select_highlight_spans(text)
        temporal = [s for s in spans if s["rule_id"].startswith("temporal.")]
        assert temporal, "expected at least one temporal rule to fire"
        for s in temporal:
            assert text[s["start"] : s["end"]] == s["evidence"]

    def test_no_cue_returns_empty(self) -> None:
        text = "The patient is well. Blood pressure normal. No medication changes."
        spans = select_highlight_spans(text)
        assert spans == []

    def test_overlapping_spans_are_deduped_earliest_start_wins(self) -> None:
        # If two rules match overlapping regions, only the earliest-starting one
        # survives (deterministic). We assert the invariant: no two kept spans
        # overlap, regardless of input.
        text = (
            "Her seizure frequency has decreased since last clinic, "
            "now infrequent seizures, previously frequent."
        )
        spans = select_highlight_spans(text)
        for i in range(1, len(spans)):
            assert spans[i]["start"] >= spans[i - 1]["end"], (
                f"overlapping spans kept: {spans[i - 1]} and {spans[i]}"
            )

    def test_spans_are_sorted_by_start(self) -> None:
        text = "Seizure frequency has decreased. She had last seizure in 2019. Now seizure free."
        spans = select_highlight_spans(text)
        starts = [s["start"] for s in spans]
        assert starts == sorted(starts)

    def test_spans_are_json_serializable_dicts(self) -> None:
        import json

        text = "Seizure frequency has decreased since last clinic."
        spans = select_highlight_spans(text)
        assert spans  # sanity
        # HighlightSpan is a dict subclass; it must round-trip through json.
        for s in spans:
            round_tripped = json.loads(json.dumps(s))
            assert set(round_tripped) == {"start", "end", "evidence", "rule_id"}


# --------------------------------------------------------------------------------------
# render_highlighted_text
# --------------------------------------------------------------------------------------
class TestRenderHighlightedText:
    def test_single_span_wrapped_in_markers(self) -> None:
        text = "The seizure frequency has decreased today."
        # "seizure frequency has decreased" lives in the text; use a real span.
        spans = select_highlight_spans(text)
        dec = [s for s in spans if s["rule_id"] == "change.decreased"]
        assert dec, "precondition: change.decreased fired"
        rendered = render_highlighted_text(text, [dec[0]])
        assert "[[HL]]" in rendered and "[[/HL]]" in rendered
        # The wrapped substring must be the original evidence.
        assert f"[[HL]]{dec[0]['evidence']}[[/HL]]" in rendered

    def test_no_spans_returns_text_unchanged(self) -> None:
        text = "Nothing to highlight here."
        assert render_highlighted_text(text, []) == text

    def test_multiple_spans_each_wrapped_and_offsets_preserved(self) -> None:
        text = "Seizure frequency has decreased. In the last year she had increased episodes."
        spans = select_highlight_spans(text)
        # Keep at most two change-rule spans for a deterministic multi-span case.
        change_spans = [s for s in spans if s["rule_id"].startswith("change.")]
        if len(change_spans) < 2:
            # Fall back to any two spans if change rules didn't both fire.
            change_spans = spans[:2]
        assert len(change_spans) >= 2, "test needs >=2 spans"
        rendered = render_highlighted_text(text, change_spans)
        # Each evidence must appear exactly once wrapped.
        for s in change_spans:
            assert rendered.count(f"[[HL]]{s['evidence']}[[/HL]]") == 1
        # Strip markers and the result must equal the original text.
        stripped = rendered.replace("[[HL]]", "").replace("[[/HL]]", "")
        assert stripped == text

    def test_marker_insertion_is_right_to_left_safe(self) -> None:
        # Construct two synthetic spans that would corrupt each other if inserted
        # left-to-right (the second span's offsets would shift after the first
        # marker insertion). Right-to-left insertion keeps both valid.
        text = "AAAAABBBBB"
        spans = [
            HighlightSpan(start=0, end=5, evidence="AAAAA", rule_id="synthetic.first"),
            HighlightSpan(start=5, end=10, evidence="BBBBB", rule_id="synthetic.second"),
        ]
        rendered = render_highlighted_text(text, spans)
        assert rendered == "[[HL]]AAAAA[[/HL]][[HL]]BBBBB[[/HL]]"


# --------------------------------------------------------------------------------------
# render_highlight_only (Arm C)
# --------------------------------------------------------------------------------------
class TestRenderHighlightOnly:
    def test_concatenates_evidence_texts(self) -> None:
        spans = [
            HighlightSpan(start=0, end=3, evidence="foo", rule_id="r1"),
            HighlightSpan(start=5, end=8, evidence="bar", rule_id="r2"),
        ]
        assert render_highlight_only(spans) == "foo\nbar"

    def test_empty_spans_returns_explicit_note(self) -> None:
        # Arm C must not feed the LLM a literal empty string.
        out = render_highlight_only([])
        assert out and "(no direction or temporal cues" in out
