"""Benchmark CUI-projection ablation diagnostic for ExECTv2 (satellite 09, Phase D).

The benchmark (with-CUI) match key includes ``CUI`` while the semantic key drops
it (``contract.evaluation``). So the gap between the semantic and benchmark
headlines is owned entirely by the deterministic CUI projection
(``benchmark_projection.project_cuis``) — never by LLM clinical reasoning. This
report makes that contribution auditable as a *separate post-step* with its own
numbers:

* **coverage** — fraction of predicted mentions the lexicon attaches a CUI to;
* **correctness** — on source-near overlapping (gold, predicted) pairs where both
  carry a CUI, the fraction whose projected CUI matches gold;
* **gold CUI density** — fraction of gold mentions that carry a CUI (the share of
  the benchmark key the projection must reproduce).

The honest reading the plan demands: a low benchmark-vs-semantic delta driven by
*coverage* means the lexicon under-covers (closing it is in-sample CUI lookup, a
documented projection artifact — never a clinical-reasoning gain); a low
*correctness* means the lexicon maps the concept to the wrong ontology code.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import normalize_phrase
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

_CUI = "CUI"
_CUI_PHRASE = "CUIPhrase"


@dataclass(frozen=True)
class CuiProjectionEntityDiagnostic:
    """CUI projection coverage + correctness for one entity."""

    entity: str
    predicted_mentions: int
    predicted_with_cui: int
    gold_mentions: int
    gold_with_cui: int
    overlap_pairs: int
    cui_both_present: int
    cui_agree: int
    cuiphrase_both_present: int
    cuiphrase_agree: int

    @property
    def coverage(self) -> float:
        return self.predicted_with_cui / self.predicted_mentions if self.predicted_mentions else 0.0

    @property
    def gold_cui_density(self) -> float:
        return self.gold_with_cui / self.gold_mentions if self.gold_mentions else 0.0

    @property
    def cui_agreement_rate(self) -> float:
        return self.cui_agree / self.cui_both_present if self.cui_both_present else 0.0

    @property
    def cuiphrase_agreement_rate(self) -> float:
        return (
            self.cuiphrase_agree / self.cuiphrase_both_present
            if self.cuiphrase_both_present
            else 0.0
        )


@dataclass(frozen=True)
class CuiProjectionDiagnostic:
    """Per-entity CUI projection diagnostic plus the micro-averaged overall."""

    per_entity: dict[str, CuiProjectionEntityDiagnostic]
    overall: CuiProjectionEntityDiagnostic


def _first_overlap(
    gold_phrase: str,
    predictions: Sequence[Mapping[str, str | None]],
    used: set[int],
) -> int | None:
    if not gold_phrase:
        return None
    for i, pred in enumerate(predictions):
        if i in used:
            continue
        pred_phrase = normalize_phrase(pred.get("text") or "")
        if pred_phrase and (gold_phrase in pred_phrase or pred_phrase in gold_phrase):
            return i
    return None


def _entity_diagnostic(
    entity: str,
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> CuiProjectionEntityDiagnostic:
    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())

    pred_n = pred_cui = gold_n = gold_cui = 0
    ov = cui_both = cui_agree = phrase_both = phrase_agree = 0
    for letter_id in all_ids:
        gold = list(gold_by_id[letter_id].entities(entity)) if letter_id in gold_by_id else []
        pred = [
            {
                "text": a.text,
                "CUI": a.attributes.get(_CUI),
                "CUIPhrase": a.attributes.get(_CUI_PHRASE),
            }
            for a in (pred_by_id[letter_id].entities(entity) if letter_id in pred_by_id else [])
        ]
        gold_n += len(gold)
        pred_n += len(pred)
        pred_cui += sum(1 for p in pred if p.get(_CUI))
        gold_cui += sum(1 for g in gold if g.attributes.get(_CUI))
        used: set[int] = set()
        for g in gold:
            idx = _first_overlap(normalize_phrase(g.text), pred, used)
            if idx is None:
                continue
            used.add(idx)
            ov += 1
            gc, pc = g.attributes.get(_CUI), pred[idx].get(_CUI)
            if gc and pc:
                cui_both += 1
                if gc == pc:
                    cui_agree += 1
            gcp, pcp = g.attributes.get(_CUI_PHRASE), pred[idx].get(_CUI_PHRASE)
            if gcp and pcp:
                phrase_both += 1
                if normalize_phrase(gcp) == normalize_phrase(pcp):
                    phrase_agree += 1
    return CuiProjectionEntityDiagnostic(
        entity=entity,
        predicted_mentions=pred_n,
        predicted_with_cui=pred_cui,
        gold_mentions=gold_n,
        gold_with_cui=gold_cui,
        overlap_pairs=ov,
        cui_both_present=cui_both,
        cui_agree=cui_agree,
        cuiphrase_both_present=phrase_both,
        cuiphrase_agree=phrase_agree,
    )


def cui_projection_diagnostic(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> CuiProjectionDiagnostic:
    """Compute the per-entity + overall CUI projection coverage/correctness."""
    per_entity = {
        entity: _entity_diagnostic(entity, gold_letters, pred_letters) for entity in entities
    }
    overall = CuiProjectionEntityDiagnostic(
        entity="__overall__",
        predicted_mentions=sum(d.predicted_mentions for d in per_entity.values()),
        predicted_with_cui=sum(d.predicted_with_cui for d in per_entity.values()),
        gold_mentions=sum(d.gold_mentions for d in per_entity.values()),
        gold_with_cui=sum(d.gold_with_cui for d in per_entity.values()),
        overlap_pairs=sum(d.overlap_pairs for d in per_entity.values()),
        cui_both_present=sum(d.cui_both_present for d in per_entity.values()),
        cui_agree=sum(d.cui_agree for d in per_entity.values()),
        cuiphrase_both_present=sum(d.cuiphrase_both_present for d in per_entity.values()),
        cuiphrase_agree=sum(d.cuiphrase_agree for d in per_entity.values()),
    )
    return CuiProjectionDiagnostic(per_entity=per_entity, overall=overall)


def render_markdown(
    diagnostic: CuiProjectionDiagnostic,
    *,
    entities: Sequence[str],
    title: str = "ExECTv2 Benchmark CUI-Projection Ablation",
    source: str = "",
) -> str:
    """Render the projection ablation as a Markdown table."""
    lines = [f"# {title}", ""]
    if source:
        lines.append(f"- Source: `{source}`")
    lines.extend(
        [
            "",
            "CUI projection is a deterministic post-step; the benchmark (with-CUI) "
            "headline minus the semantic (CUI-dropped) headline is its credit, never "
            "LLM clinical reasoning. Closing a coverage gap is in-sample CUI lookup, a "
            "documented projection artifact.",
            "",
            "| Entity | Pred | CUI coverage | Gold CUI density | Overlaps | "
            "CUI agreement | CUIPhrase agreement |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for entity in list(entities) + ["__overall__"]:
        d = diagnostic.overall if entity == "__overall__" else diagnostic.per_entity.get(entity)
        if d is None:
            continue
        label = "overall" if entity == "__overall__" else entity
        lines.append(
            f"| {label} | {d.predicted_mentions} "
            f"| {d.coverage:.2f} ({d.predicted_with_cui}/{d.predicted_mentions}) "
            f"| {d.gold_cui_density:.2f} ({d.gold_with_cui}/{d.gold_mentions}) "
            f"| {d.overlap_pairs} "
            f"| {d.cui_agreement_rate:.2f} ({d.cui_agree}/{d.cui_both_present}) "
            f"| {d.cuiphrase_agreement_rate:.2f} ({d.cuiphrase_agree}/{d.cuiphrase_both_present}) |"
        )
    lines.append("")
    return "\n".join(lines)
