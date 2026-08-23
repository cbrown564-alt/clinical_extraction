"""Five-cell paper teaching runs. Replay saved development raws only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.architecture.fact_lineage import attach_run_gold, build_exect_facts
from clinical_extraction.architecture.stage_manifest import load_manifest
from clinical_extraction.architecture.teaching_case import (
    GanCaseSpec,
    MethodRun,
    TeachingCase,
    _exect_gold_label,
    _exect_llm_only_run,
    _exect_llm_pre_post_run,
    _exect_rules_only_run,
    _exect_scoring,
    _gan_llm_only_run,
    _gan_llm_with_rules_run,
    _gan_record,
    _gan_rules_only_run,
    _gan_scoring,
    _mention_summary,
)
from clinical_extraction.core.paths import discover_repo_root

ROOT = discover_repo_root(start=Path(__file__))

PAPER_GAN_IDS = (
    "gan_rules",
    "gan_llm_pre_post_label_forms",
    "gan_llm_extract_label_forms",
    "gan_llm_encode",
    "gan_llm_select_from_extract",
)
PAPER_EXECT_IDS = (
    "exect_rules",
    "exect_llm_pre_post",
    "exect_llm_only",
    "exect_llm_encode",
    "exect_llm_select",
)
PAPER_METHOD_IDS = PAPER_GAN_IDS + PAPER_EXECT_IDS

GAN_EXTRACT_RAW = (
    ROOT
    / "experiments/paper/gan_llm_extract_label_forms/grok46/dev750/rows.jsonl"
)
GAN_PRE_POST_RAW = (
    ROOT
    / "experiments/paper/gan_llm_pre_post_label_forms/gemini37flash/dev750/rows.jsonl"
)
GAN_SELECT_RAW = (
    ROOT
    / "experiments/paper/gan_llm_select_from_extract/gemini37flash"
    / "gan_llm_extract_label_forms/dev750/rows.jsonl"
)
EXECT_PRE_POST_RAW = (
    ROOT
    / "paper_experiments/exect/exect_llm_pre_post/gpt56luna/dev140/structured.jsonl"
)
EXECT_ONLY_RAW = (
    ROOT
    / "paper_experiments/exect/exect_llm_only/gpt56luna/dev140/structured.jsonl"
)
EXECT_ENCODE_RAW = (
    ROOT / "experiments/paper/exect_llm_encode/gemini37flash/dev140/rows.jsonl"
)
EXECT_SELECT_RAW = (
    ROOT / "experiments/paper/exect_llm_select/gemini37flash/dev140/rows.jsonl"
)

GAN_SOURCE_NOTES = {
    "gan_rules": "rules (no model raw)",
    "gan_llm_pre_post_label_forms": str(GAN_PRE_POST_RAW.relative_to(ROOT)),
    "gan_llm_extract_label_forms": str(GAN_EXTRACT_RAW.relative_to(ROOT)),
    "gan_llm_encode": str(GAN_EXTRACT_RAW.relative_to(ROOT)),
    "gan_llm_select_from_extract": str(GAN_SELECT_RAW.relative_to(ROOT)),
}
EXECT_SOURCE_NOTES = {
    "exect_rules": "rules (no model raw)",
    "exect_llm_pre_post": str(EXECT_PRE_POST_RAW.relative_to(ROOT)),
    "exect_llm_only": str(EXECT_ONLY_RAW.relative_to(ROOT)),
    "exect_llm_encode": str(EXECT_ENCODE_RAW.relative_to(ROOT)),
    "exect_llm_select": str(EXECT_SELECT_RAW.relative_to(ROOT)),
}

FRONTEND_METHOD_REMAP = {
    "gan2026_rules_only": "gan_rules",
    "gan2026_llm_only": "gan_llm_only",
    "gan2026_llm_with_rules": "gan_llm_with_rules",
    "exectv2_rules_only": "exect_rules",
    "exectv2_llm_only": "exect_llm_only",
    "exectv2_llm_pre_post": "exect_llm_pre_post",
}

MANIFEST_CLONE_FROM = {
    "gan_rules": "gan2026_rules_only",
    "gan_llm_pre_post_label_forms": "gan2026_llm_with_rules",
    "gan_llm_extract_label_forms": "gan2026_llm_with_rules",
    "gan_llm_encode": "gan2026_llm_with_rules",
    "gan_llm_select_from_extract": "gan2026_llm_with_rules",
    "exect_rules": "exectv2_rules_only",
    "exect_llm_pre_post": "exectv2_llm_pre_post",
    "exect_llm_only": "exectv2_llm_only",
    "exect_llm_encode": "exectv2_llm_only",
    "exect_llm_select": "exectv2_llm_only",
}


def _ownership(
    run: MethodRun,
    *,
    extract: str,
    encode: str,
    select: str,
    extract_in: Any,
    extract_out: Any,
    encode_in: Any,
    encode_out: Any,
    select_in: Any,
    select_out: Any,
    extract_note: str,
    encode_note: str,
    select_note: str,
) -> None:
    prefix = run.method_id
    existing = list(run.observations)
    run.observations.clear()
    run.record(
        f"{prefix}.extract",
        input_value=extract_in,
        output_value=extract_out,
        changed=True,
        note=extract_note,
        owner="model" if extract in {"LLM", "both"} else "deterministic",
        stage_name="Extract",
        effect_class="clinical_meaning",
    )
    run.record(
        f"{prefix}.encode",
        input_value=encode_in,
        output_value=encode_out,
        changed=True,
        note=encode_note,
        owner="model" if encode == "LLM" else "deterministic",
        stage_name="Encode",
        effect_class="representation",
    )
    run.record(
        f"{prefix}.select",
        input_value=select_in,
        output_value=select_out,
        changed=True,
        note=select_note,
        owner="model" if select == "LLM" else "deterministic",
        stage_name="Select",
        effect_class="clinical_meaning",
    )
    run.observations.extend(existing)


def gan_paper_runs(spec: GanCaseSpec) -> list[MethodRun]:
    extract_raw = spec.extract_label_forms_raw
    pre_post_raw = spec.pre_post_label_forms_raw
    select_raw = spec.select_from_extract_raw

    rules = _gan_rules_only_run(spec)
    rules.method_id = "gan_rules"
    _collapse_gan_rules(rules)

    pre_post = _gan_llm_with_rules_run(
        spec,
        repair_mode="llm_select",
        method_id="gan_llm_pre_post_label_forms",
        raw_output=pre_post_raw,
    )
    _collapse_gan_hybrid(
        pre_post,
        spec,
        extract="both",
        encode="rules",
        select="rules",
        extract_note=(
            "Cell 2: Gemini 3.7 Flash extract on the label-forms pre-post "
            "request; rules own encode and select."
        ),
        encode_note="Codebook encode is deterministic after the joint extract.",
        select_note="Select families are deterministic.",
    )

    extract = _gan_llm_with_rules_run(
        spec,
        repair_mode="llm_select_after_codebook",
        method_id="gan_llm_extract_label_forms",
        raw_output=extract_raw,
    )
    _collapse_gan_hybrid(
        extract,
        spec,
        extract="LLM",
        encode="rules",
        select="rules",
        extract_note="Cell 3 headline: Gemini 3.7 Flash codebook extract.",
        encode_note="Deterministic codebook encode after the extract.",
        select_note="Deterministic select families.",
    )

    encode = _gan_llm_with_rules_run(
        spec,
        repair_mode="llm_select_only",
        method_id="gan_llm_encode",
        raw_output=extract_raw,
    )
    _collapse_gan_hybrid(
        encode,
        spec,
        extract="LLM",
        encode="LLM",
        select="rules",
        extract_note="Cell 4 uses the same codebook extract; the extract already wrote the form.",
        encode_note="LLM encode: the extract raw already carries codebook form.",
        select_note="Select families only; no encode rewrite.",
    )

    select = _gan_select_from_extract_run(spec, extract_raw, select_raw)
    extras = [_gan_llm_only_run(spec), _gan_llm_with_rules_run(spec)]
    return [rules, pre_post, extract, encode, select, *extras]


def _collapse_gan_rules(run: MethodRun) -> None:
    by_id = {obs.stage_id: obs for obs in run.observations}
    extract = by_id["gan.rules.extract"]
    encode = by_id["gan.rules.normalize"]
    select = by_id["gan.rules.select_and_render"]
    score = by_id["gan.rules.score"]
    _ownership(
        run,
        extract="rules",
        encode="rules",
        select="rules",
        extract_in=extract.input_value,
        extract_out=extract.output_value,
        encode_in=encode.input_value,
        encode_out=encode.output_value,
        select_in=select.input_value,
        select_out=select.output_value,
        extract_note="Cell 1: rules extract.",
        encode_note="Rules normalize / encode the candidates.",
        select_note="Rules select and render.",
    )
    run.record(
        "gan_rules.score",
        input_value=score.input_value,
        output_value=score.output_value,
        changed=True,
        note=score.note,
        owner="scorer",
        stage_name="Score",
        effect_class="benchmark_projection",
    )


def _collapse_gan_hybrid(
    run: MethodRun,
    spec: GanCaseSpec,
    *,
    extract: str,
    encode: str,
    select: str,
    extract_note: str,
    encode_note: str,
    select_note: str,
) -> None:
    by_id = {obs.stage_id: obs for obs in run.observations}
    model = by_id.get("gan.llm_with_rules.model_call")
    normalize = by_id.get("gan.llm_with_rules.normalize_events")
    resolve = by_id.get("gan.llm_with_rules.resolve_label")
    score = next(obs for obs in run.observations if obs.stage_id.endswith(".score"))
    _ownership(
        run,
        extract=extract,
        encode=encode,
        select=select,
        extract_in=spec.note_text,
        extract_out=model.output_value if model else "(none)",
        encode_in=normalize.input_value if normalize else "(none)",
        encode_out=normalize.output_value if normalize else "(none)",
        select_in=resolve.input_value if resolve else "(none)",
        select_out=resolve.output_value if resolve else run.final_answer,
        extract_note=extract_note,
        encode_note=encode_note,
        select_note=select_note,
    )
    run.record(
        f"{run.method_id}.score",
        input_value=score.input_value,
        output_value=score.output_value,
        changed=True,
        note=score.note,
        owner="scorer",
        stage_name="Score",
        effect_class="benchmark_projection",
    )


def _gan_select_from_extract_run(
    spec: GanCaseSpec, extract_raw: str, select_raw: str
) -> MethodRun:
    from clinical_extraction.paper.gan_later_stage import score_later_stage_row

    manifest = load_manifest("gan2026_llm_with_rules")
    run = MethodRun(method_id="gan_llm_select_from_extract", manifest=manifest)
    record = _gan_record(spec)
    row = score_later_stage_row(
        "gan_llm_select_from_extract",
        record,
        select_raw,
        extract_row={"raw_output": extract_raw},
        encode_row=None,
        split="dev750",
        machine="validation",
    )
    structured = row.get("structured_record") or {}
    selection = structured.get("selection") or {}
    events = structured.get("events") or []
    final_label = selection.get("final_label")
    _ownership(
        run,
        extract="LLM",
        encode="LLM",
        select="LLM",
        extract_in=spec.note_text,
        extract_out=[event.get("event_id") for event in events],
        encode_in=row.get("encoded_events") or [],
        encode_out=[
            f"{item.get('event_id')}: {item.get('label')}"
            for item in (row.get("encoded_events") or [])
        ],
        select_in=select_raw,
        select_out=f"selected {selection.get('selected_event_ids')} -> {final_label}",
        extract_note="Cell 5 extract is the codebook extract ledger.",
        encode_note="Encode is the extract form; no separate encode call.",
        select_note="Gemini later-stage select on the extract ledger.",
    )
    _gan_scoring(run, "gan_llm_select_from_extract.score", final_label, gold_label=spec.gold)
    attach_run_gold(run, spec.gold, spec.gold_note)
    return run


def exect_paper_runs(
    letter: Any,
    *,
    pre_post_raw: str,
    only_raw: str,
    encode_row: dict[str, Any],
    select_row: dict[str, Any],
) -> list[MethodRun]:
    rules = _exect_rules_only_run(letter)
    rules.method_id = "exect_rules"
    _collapse_exect_rules(rules, letter)

    pre_post = _exect_llm_pre_post_run(letter, pre_post_raw)
    pre_post.method_id = "exect_llm_pre_post"
    _collapse_exect_existing(
        pre_post,
        letter,
        extract="both",
        encode="rules",
        select="rules",
        extract_note="Cell 2: Gemini 3.7 Flash pre-post extract; rules encode and select.",
        encode_note="Family transforms / encode are deterministic.",
        select_note="Lenses and store keep rule select.",
    )

    only = _exect_llm_only_run(letter, only_raw)
    only.method_id = "exect_llm_only"
    _collapse_exect_existing(
        only,
        letter,
        extract="LLM",
        encode="rules",
        select="rules",
        extract_note="Cell 3: Gemini 3.7 Flash extract (exect_llm_only raw).",
        encode_note="Rule encode after flatten.",
        select_note="Rule select after flatten.",
    )

    encode = _exect_later_encode_run(letter, only_raw, encode_row)
    select = _exect_later_select_run(letter, only_raw, encode_row, select_row)
    return [rules, pre_post, only, encode, select]


def _collapse_exect_rules(run: MethodRun, letter: Any) -> None:
    extract = next(
        (obs for obs in run.observations if "extract" in obs.stage_id),
        run.observations[0],
    )
    score = next(obs for obs in run.observations if obs.stage_id.endswith(".score"))
    _ownership(
        run,
        extract="rules",
        encode="rules",
        select="rules",
        extract_in=letter.note_text,
        extract_out=extract.output_value,
        encode_in=extract.output_value,
        encode_out=extract.output_value,
        select_in=extract.output_value,
        select_out=run.final_answer,
        extract_note="Cell 1: nine-entity rule extractors.",
        encode_note="Rules encode the extracted mentions.",
        select_note="Rules keep the extracted set.",
    )
    run.record(
        "exect_rules.score",
        input_value=score.input_value,
        output_value=score.output_value,
        changed=True,
        note=score.note,
        owner="scorer",
        stage_name="Score",
        effect_class="benchmark_projection",
    )


def _collapse_exect_existing(
    run: MethodRun,
    letter: Any,
    *,
    extract: str,
    encode: str,
    select: str,
    extract_note: str,
    encode_note: str,
    select_note: str,
) -> None:
    model = next((obs for obs in run.observations if "model_call" in obs.stage_id), None)
    score = next(obs for obs in run.observations if obs.stage_id.endswith(".score"))
    _ownership(
        run,
        extract=extract,
        encode=encode,
        select=select,
        extract_in=letter.note_text,
        extract_out=model.output_value if model else run.final_answer,
        encode_in=model.output_value if model else "(none)",
        encode_out=run.final_answer,
        select_in=run.final_answer,
        select_out=run.final_answer,
        extract_note=extract_note,
        encode_note=encode_note,
        select_note=select_note,
    )
    run.record(
        f"{run.method_id}.score",
        input_value=score.input_value,
        output_value=score.output_value,
        changed=True,
        note=score.note,
        owner="scorer",
        stage_name="Score",
        effect_class="benchmark_projection",
    )


def _exect_later_encode_run(letter: Any, extract_raw: str, encode_row: dict[str, Any]) -> MethodRun:
    from clinical_extraction.paper.exect_later_stage import (
        flatten_extract_mentions,
        join_encode_mentions,
        parse_encode_mentions,
    )
    from clinical_extraction.paper.exect_rule_select_after_encode import (
        apply_rule_select_after_llm_encode,
    )
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
        extract_json_object,
    )

    manifest = load_manifest("exectv2_llm_only")
    run = MethodRun(method_id="exect_llm_encode", manifest=manifest)
    extract_mentions = list(encode_row.get("extract_mentions") or [])
    if not extract_mentions:
        extract_mentions = flatten_extract_mentions(
            letter, extract_raw, model="gemini/gemini-3.7-flash", split="dev140"
        )
    encoded = list(encode_row.get("encoded_mentions") or [])
    if not encoded:
        blob = extract_json_object(str(encode_row.get("raw_output") or "")) or encode_row.get(
            "raw_output"
        )
        encoded = join_encode_mentions(extract_mentions, parse_encode_mentions(str(blob)))
    selected, _actions = apply_rule_select_after_llm_encode(
        encoded, extract_mentions, letter.note_text
    )
    _ownership(
        run,
        extract="LLM",
        encode="LLM",
        select="rules",
        extract_in=letter.note_text,
        extract_out=[_mention_summary(item) for item in extract_mentions],
        encode_in=[_mention_summary(item) for item in extract_mentions],
        encode_out=[_mention_summary(item) for item in encoded],
        select_in=[_mention_summary(item) for item in encoded],
        select_out=[_mention_summary(item) for item in selected],
        extract_note="Same Gemini exect_llm_only extract raw as cell 3.",
        encode_note="Gemini later-stage encode writes the form.",
        select_note="Accepted select rules after encode.",
    )
    _exect_scoring(
        run,
        "exect_llm_encode.score",
        selected,
        nine_entity=False,
        letter=letter,
    )
    run.facts = build_exect_facts(
        letter,
        selected,
        [],
        run,
        gold_label=_exect_gold_label(letter),
    )
    attach_run_gold(run, _exect_gold_label(letter))
    return run


def _exect_later_select_run(
    letter: Any, extract_raw: str, encode_row: dict[str, Any], select_row: dict[str, Any]
) -> MethodRun:
    from clinical_extraction.paper.exect_later_stage import (
        flatten_extract_mentions,
        join_select_mentions,
        parse_select_mentions,
    )

    manifest = load_manifest("exectv2_llm_only")
    run = MethodRun(method_id="exect_llm_select", manifest=manifest)
    extract_mentions = list(
        select_row.get("extract_mentions") or encode_row.get("extract_mentions") or []
    )
    if not extract_mentions:
        extract_mentions = flatten_extract_mentions(
            letter, extract_raw, model="gemini/gemini-3.7-flash", split="dev140"
        )
    encoded = list(select_row.get("encoded_mentions") or encode_row.get("encoded_mentions") or [])
    selected = list(select_row.get("selected_mentions") or [])
    if not selected:
        selected = join_select_mentions(
            encoded, parse_select_mentions(str(select_row.get("raw_output") or ""))
        )
    _ownership(
        run,
        extract="LLM",
        encode="LLM",
        select="LLM",
        extract_in=letter.note_text,
        extract_out=[_mention_summary(item) for item in extract_mentions],
        encode_in=[_mention_summary(item) for item in extract_mentions],
        encode_out=[_mention_summary(item) for item in encoded],
        select_in=[_mention_summary(item) for item in encoded],
        select_out=[_mention_summary(item) for item in selected],
        extract_note="Same Gemini exect_llm_only extract raw as cells 3-4.",
        encode_note="Same later-stage encode ledger as cell 4.",
        select_note="Gemini later-stage select writes keep/drop/merge.",
    )
    _exect_scoring(
        run,
        "exect_llm_select.score",
        selected,
        nine_entity=False,
        letter=letter,
    )
    run.facts = build_exect_facts(
        letter,
        selected,
        [],
        run,
        gold_label=_exect_gold_label(letter),
    )
    attach_run_gold(run, _exect_gold_label(letter))
    return run


def _remap_payload(payload: dict[str, Any]) -> dict[str, Any]:
    method_id = str(payload.get("method_id") or "")
    payload["method_id"] = FRONTEND_METHOD_REMAP.get(method_id, method_id)
    return payload


def teaching_cases_payload(cases: tuple[TeachingCase, ...]) -> dict[str, Any]:
    manifests = []
    for method_id, source_id in MANIFEST_CLONE_FROM.items():
        data = load_manifest(source_id).to_dict()
        data["method_id"] = method_id
        manifests.append(data)
    return {
        "cases": [_remap_payload(case.to_dict()) for case in cases],
        "manifests": manifests,
    }


def write_teaching_cases_json(path: Path | None = None) -> Path:
    from clinical_extraction.architecture.paper_teaching_cases import (
        build_paper_teaching_letters,
    )

    dest = path or (ROOT / "frontend/public/mock-data/teaching-cases.json")
    payload = teaching_cases_payload(build_paper_teaching_letters())
    dest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return dest
