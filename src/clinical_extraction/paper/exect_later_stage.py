"""Gemini later-stage ExECT encode on a saved flatten ledger."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import dspy
from dotenv import load_dotenv
from dspy.adapters.chat_adapter import ChatAdapter

from clinical_extraction.core.paths import discover_repo_root
from clinical_extraction.paper.batch import BatchChatItem, complete_chat_batch
from clinical_extraction.paper.exect import (
    MODELS,
    _prepare_live_runtime,
    apply_reasoning_effort,
    letters_for_split,
)
from clinical_extraction.paper.exect_rung_replay import (
    exect_llm_only_rows_path,
    schema_mention_rows,
)
from clinical_extraction.paper.lm import resolve_paper_api_base
from clinical_extraction.paper.methods import (
    exect_machine_split,
    exect_row_count,
    holdout_is_aggregate_only,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.lexicon import (
    attach_cui,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm import (
    llm_only_key_entities_structured as structured,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_llm_encode import (
    EXECT_LLM_ENCODE,
    LLM_ENCODE_AUTHORED_KEYS,
    build_llm_encode_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_llm_select import (
    EXECT_LLM_SELECT,
    LLM_SELECT_AUTHORED_KEYS,
    build_llm_select_prompt_input,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompt_mention_view import (
    gold_key_for_detail,
    mention_family,
    mention_id,
    mention_sentence,
    mention_standard_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.contracts import (
    StructuredMethodConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    annotation_from_mapping,
    exact_clinical_headline_scores,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.parse_diagnostics import (
    extract_json_object,
)

LaterStageMethod = Literal["exect_llm_encode", "exect_llm_select"]
LATER_STAGE_SCORER = "clinical_headline_unit_keys"
_CROSS_FAMILIES = frozenset({"Diagnosis", "SeizureFrequency"})
CITED_SLUG = "gemini37flash"
EXTRACT_SLUG = "gemini37flash"
MAX_TOKENS = 8000
ROOT = discover_repo_root(start=Path(__file__))
WORK_ROOT = ROOT / "experiments/paper"
HOLDOUT_SCRATCH = ROOT / "scratch/holdout/paper"


class ExectLaterStageSignature(dspy.Signature):
    """Return one JSON object with a mentions list."""

    prompt_input_json: str = dspy.InputField(
        desc="JSON with the task, instructions, and mention rows."
    )
    structured_json: str = dspy.OutputField(
        desc="One JSON object with a mentions list."
    )


class ExectLaterStageProgram(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExectLaterStageSignature)

    def render_messages(self, *, prompt_input_json: str) -> list[dict[str, object]]:
        return ChatAdapter().format(
            ExectLaterStageSignature,
            demos=[],
            inputs={"prompt_input_json": prompt_input_json},
        )


def prompt_version(method: LaterStageMethod) -> str:
    if method == "exect_llm_encode":
        return EXECT_LLM_ENCODE
    return EXECT_LLM_SELECT


def later_stage_work_root(
    method: LaterStageMethod,
    slug: str = CITED_SLUG,
    split: str = "dev140",
) -> Path:
    root = HOLDOUT_SCRATCH if holdout_is_aggregate_only(split) else WORK_ROOT
    return root / method / slug / split


def encode_work_rows_path(split: str, slug: str = CITED_SLUG) -> Path:
    return later_stage_work_root("exect_llm_encode", slug, split) / "rows.jsonl"


def later_stage_pred_key(method: LaterStageMethod) -> str:
    return "selected_mentions" if method == "exect_llm_select" else "encoded_mentions"


def comparison_from_later_stage_rows(
    method: LaterStageMethod,
    letters: Sequence[ExectLetter],
    rows: Sequence[Mapping[str, Any]],
    *,
    existing: Mapping[str, Any] | None,
    slug: str,
    model: str,
    split: str,
    prompt: str,
) -> dict[str, Any]:
    """Score joined later-stage mentions with the exact clinical-fact scorer."""

    pred_key = later_stage_pred_key(method)
    pred_letters = [
        ExectLetter(
            letter_id=letter.letter_id,
            note_text=letter.note_text,
            annotations=tuple(
                annotation_from_mapping(mention)
                for mention in row[pred_key]
            ),
        )
        for letter, row in zip(letters, rows, strict=True)
    ]
    family_scores = exact_clinical_headline_scores(letters, pred_letters)
    overall = aggregate_scores(family_scores.values())
    holdout = holdout_is_aggregate_only(split)
    prior = None if existing is None else existing.get("four_family_headline_f1")
    artifact: dict[str, Any] = {
        "schema_version": f"paper.{method}.v1",
        "generated_on": datetime.now(UTC).date().isoformat(),
        "method": method,
        "model_slug": slug,
        "model": model,
        "split": split,
        "split_machine": exect_machine_split(split),
        "row_count": len(letters),
        "row_policy": (
            "aggregate_only" if holdout else "development_review_permitted"
        ),
        "prompt_version": prompt,
        "started_utc": None if existing is None else existing.get("started_utc"),
        "finished_utc": None if existing is None else existing.get("finished_utc"),
        "live": False if existing is None else existing.get("live", False),
        "call_transport": (
            None if existing is None else existing.get("call_transport")
        ),
        "model_calls": 0 if existing is None else existing.get("model_calls", 0),
        "scorer": LATER_STAGE_SCORER,
        "clinical_headline": family_scores,
        "four_family_headline_f1": overall["f1"],
        "summary": overall,
        "claim_boundary": (
            "ExECT aggregate-only test60 later-stage cell. Do not inspect holdout rows."
            if holdout
            else (
                "ExECT development later-stage cell. Not holdout. "
                "Join only. CUI is decoration."
            )
        ),
    }
    if prior is not None and prior != overall["f1"]:
        artifact["prior_four_family_headline_f1"] = prior
        artifact["rescored_utc"] = datetime.now(UTC).isoformat()
    return artifact


def rescore_later_stage(
    method: LaterStageMethod,
    slug: str,
    split: str,
) -> dict[str, Any]:
    """Rewrite a finished later-stage comparison with the exact scorer."""

    if method not in {"exect_llm_encode", "exect_llm_select"}:
        raise RuntimeError(f"unsupported later-stage method {method}")
    if slug != CITED_SLUG:
        raise RuntimeError("later-stage ExECT encode and select run on Gemini only")
    work_root = later_stage_work_root(method, slug, split)
    rows_path = work_root / "rows.jsonl"
    comparison_path = work_root / "comparison.json"
    if not rows_path.is_file() or not comparison_path.is_file():
        raise RuntimeError(f"missing finished later-stage {method} {slug} {split} run")
    letters = letters_for_split(split)
    expected = exect_row_count(split)
    if len(letters) != expected:
        raise RuntimeError(f"expected {expected} {split} letters, found {len(letters)}")
    rows = load_jsonl_rows(rows_path)
    if len(rows) != expected:
        raise RuntimeError(f"{rows_path} has {len(rows)} rows, expected {expected}")
    by_id = {str(row["letter_id"]): row for row in rows}
    ordered = [by_id[letter.letter_id] for letter in letters]
    existing = json.loads(comparison_path.read_text(encoding="utf-8"))
    if existing.get("split") != split or existing.get("method") != method:
        raise RuntimeError(f"{comparison_path} is not this paper cell")
    artifact = comparison_from_later_stage_rows(
        method,
        letters,
        ordered,
        existing=existing,
        slug=slug,
        model=str(existing.get("model") or "gemini/gemini-3.7-flash"),
        split=split,
        prompt=prompt_version(method),
    )
    comparison_path.write_text(
        json.dumps(artifact, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "artifact": comparison_path.relative_to(ROOT).as_posix(),
        "method": method,
        "split": split,
        "model_slug": slug,
        "scorer": LATER_STAGE_SCORER,
        "summary": artifact["summary"],
        "four_family_headline_f1": artifact["four_family_headline_f1"],
    }


def verify_later_stage_prompt(method: LaterStageMethod) -> None:
    sample = [
        {
            "mention_id": "m1",
            "entity": "SeizureFrequency",
            "standard_name": "seizures",
            "text": "seizures",
            "evidence": "two seizures a week",
            "attributes": {"count": "2"},
        }
    ]
    if method == "exect_llm_encode":
        payload = json.loads(build_llm_encode_prompt_input(sample))
        if set(payload) != set(LLM_ENCODE_AUTHORED_KEYS):
            raise RuntimeError("exect_llm_encode prompt drifted from authored keys")
        return
    payload = json.loads(build_llm_select_prompt_input(sample))
    if set(payload) != set(LLM_SELECT_AUTHORED_KEYS):
        raise RuntimeError("exect_llm_select prompt drifted from authored keys")
    if "standard_names" in payload:
        raise RuntimeError("exect_llm_select must not include the encode name list")


def flatten_extract_mentions(
    letter: ExectLetter,
    raw_output: str,
    *,
    model: str,
    split: str = "dev140",
) -> list[dict[str, Any]]:
    """Replay saved extract raw to flatten rows with minted mention ids."""

    before = structured.PROMPT_VERSION
    try:
        structured.set_active_prompt_version(structured.EXECT_LLM_ONLY)
        producer = structured_one_call.produce_structured_letter(
            letter,
            model=model,
            mode="replay",
            raw_output=raw_output,
            split=exect_machine_split(split),
            config=StructuredMethodConfig.selected(),
        )
    finally:
        structured.set_active_prompt_version(before)
    return schema_mention_rows(producer)


def parse_encode_mentions(raw_output: str) -> list[dict[str, Any]]:
    blob = extract_json_object(raw_output) or raw_output
    payload = json.loads(blob)
    if not isinstance(payload, dict):
        raise ValueError("encode output is not a JSON object")
    rows = payload.get("mentions")
    if not isinstance(rows, list):
        raise ValueError("encode output has no mentions list")
    mentions: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("encode mention is not an object")
        mention_key = mention_id(row)
        if not mention_key:
            raise ValueError("encode mention is missing mention_id")
        mentions.append(dict(row))
    return mentions


def join_encode_mentions(
    extract_mentions: Sequence[Mapping[str, Any]],
    encoded_mentions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Join encode writes onto extract rows. Same fact set. CUI is decoration."""

    by_id = {mention_id(row): dict(row) for row in encoded_mentions}
    joined: list[dict[str, Any]] = []
    for extract in extract_mentions:
        row_id = mention_id(extract)
        encoded = by_id.get(row_id, {})
        standard_name = str(
            encoded.get("standard_name") or extract.get("text") or ""
        )
        details = encoded.get("details")
        if not isinstance(details, Mapping):
            details = {}
        attrs = dict(extract.get("attributes") or {})
        family = str(extract.get("entity") or "")
        for key, value in details.items():
            gold_key = gold_key_for_detail(family, standard_name, str(key))
            if gold_key and value not in (None, ""):
                attrs[gold_key] = str(value)
        attrs = attach_cui(standard_name, attrs)
        joined.append(
            {
                **dict(extract),
                "mention_id": row_id,
                "standard_name": standard_name,
                "text": standard_name,
                "attributes": attrs,
            }
        )
    return joined


def parse_select_mentions(raw_output: str) -> list[dict[str, Any]]:
    blob = extract_json_object(raw_output) or raw_output
    payload = json.loads(blob)
    if not isinstance(payload, dict):
        raise ValueError("select output is not a JSON object")
    rows = payload.get("mentions")
    if not isinstance(rows, list):
        raise ValueError("select output has no mentions list")
    mentions: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("select mention is not an object")
        mentions.append(dict(row))
    return mentions


def _apply_select_writes(
    base: Mapping[str, Any],
    writes: Mapping[str, Any],
) -> dict[str, Any]:
    standard_name = str(
        writes.get("standard_name") or mention_standard_name(base) or ""
    )
    details = writes.get("details")
    if not isinstance(details, Mapping):
        details = {}
    attrs = dict(base.get("attributes") or {})
    family = mention_family(base)
    for key, value in details.items():
        gold_key = gold_key_for_detail(family, standard_name, str(key))
        if gold_key and value not in (None, ""):
            attrs[gold_key] = str(value)
    attrs = attach_cui(standard_name, attrs)
    return {
        **dict(base),
        "standard_name": standard_name,
        "text": standard_name,
        "attributes": attrs,
    }


def join_select_mentions(
    encoded_mentions: Sequence[Mapping[str, Any]],
    select_mentions: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Join select writes onto encoded rows. Same quotes. No letter scan."""

    by_id = {mention_id(row): dict(row) for row in encoded_mentions if mention_id(row)}
    kept = {row_id: dict(row) for row_id, row in by_id.items()}
    extras: list[dict[str, Any]] = []
    for row in select_mentions:
        action = str(row.get("action") or "keep").strip().lower()
        if action == "also_list":
            source = by_id.get(str(row.get("from_mention_id") or ""))
            if source is None:
                continue
            source_family = mention_family(source)
            requested = str(row.get("clinical_family") or "")
            other = next(iter(_CROSS_FAMILIES - {source_family}), "")
            if source_family not in _CROSS_FAMILIES or requested != other:
                continue
            name = str(row.get("standard_name") or mention_standard_name(source) or "")
            extras.append(
                {
                    "mention_id": "",
                    "entity": requested,
                    "clinical_family": requested,
                    "standard_name": name,
                    "text": name,
                    "evidence": mention_sentence(source),
                    "attributes": attach_cui(name, {}),
                }
            )
            continue
        row_id = mention_id(row)
        if row_id not in by_id:
            continue
        if action == "drop":
            kept.pop(row_id, None)
            continue
        if action == "merge":
            kept.pop(row_id, None)
            target_id = str(row.get("merge_into") or "")
            if target_id in kept:
                kept[target_id] = _apply_select_writes(kept[target_id], row)
            continue
        kept[row_id] = _apply_select_writes(kept[row_id], row)
    submitted = [kept[mention_id(row)] for row in encoded_mentions if mention_id(row) in kept]
    submitted.extend(extras)
    return submitted


def run_later_stage(
    method: LaterStageMethod,
    slug: str,
    *,
    split: str,
    overwrite: bool = False,
    api_base: str | None = None,
    timeout: int | None = None,
    progress_every: int = 1,
    reasoning_effort: str | None = None,
) -> dict[str, Any]:
    if method not in {"exect_llm_encode", "exect_llm_select"}:
        raise RuntimeError(f"unsupported later-stage method {method}")
    if slug != CITED_SLUG:
        raise RuntimeError("later-stage ExECT encode and select run on Gemini only")
    verify_later_stage_prompt(method)
    holdout = holdout_is_aggregate_only(split)
    spec = apply_reasoning_effort(MODELS[slug], reasoning_effort)
    load_dotenv(ROOT / ".env", override=False)
    letters = letters_for_split(split)
    expected = exect_row_count(split)
    if len(letters) != expected:
        raise RuntimeError(f"expected {expected} {split} letters, found {len(letters)}")
    extract_rows = {
        str(row["letter_id"]): row
        for row in load_jsonl_rows(exect_llm_only_rows_path(EXTRACT_SLUG, split))
    }
    encode_rows: dict[str, dict[str, Any]] = {}
    if method == "exect_llm_select":
        encode_path = encode_work_rows_path(split, spec.slug)
        if not encode_path.exists():
            raise RuntimeError("exect_llm_select needs a finished exect_llm_encode work cell")
        encode_rows = {
            str(row["letter_id"]): row for row in load_jsonl_rows(encode_path)
        }
    work_root = later_stage_work_root(method, spec.slug, split)
    work_root.mkdir(parents=True, exist_ok=True)
    rows_path = work_root / "rows.jsonl"
    started = datetime.now(UTC).isoformat()
    prompt = prompt_version(method)
    existing = [] if overwrite else _existing_complete_rows(rows_path, prompt)
    done = {str(row["letter_id"]) for row in existing}
    todo = [letter for letter in letters if letter.letter_id not in done]
    resolved_base = resolve_paper_api_base(spec.slug, api_base)
    program = ExectLaterStageProgram()
    extract_mentions_by_id: dict[str, list[dict[str, Any]]] = {}
    for letter in letters:
        extract_row = extract_rows[letter.letter_id]
        extract_mentions_by_id[letter.letter_id] = flatten_extract_mentions(
            letter,
            str(extract_row["raw_output"]),
            model=spec.model,
            split=split,
        )
    if todo:
        _prepare_live_runtime(
            spec,
            api_base=resolved_base,
            timeout=timeout or spec.timeout,
        )
    batch_raws = (
        complete_chat_batch(
            spec,
            [
                BatchChatItem(
                    custom_id=letter.letter_id,
                    messages=program.render_messages(
                        prompt_input_json=_prompt_input(
                            method,
                            extract_mentions=extract_mentions_by_id[letter.letter_id],
                            encode_row=encode_rows.get(letter.letter_id),
                        )
                    ),
                )
                for letter in todo
            ],
            work_dir=work_root,
            max_tokens=MAX_TOKENS,
        )
        if todo
        else {}
    )
    by_id = {str(row["letter_id"]): row for row in existing}
    for index, letter in enumerate(todo, start=1):
        raw_output = batch_raws.get(letter.letter_id, "")
        row = score_later_stage_row(
            method,
            letter,
            raw_output,
            extract_mentions=extract_mentions_by_id[letter.letter_id],
            encode_row=encode_rows.get(letter.letter_id),
            split=split,
        )
        if row.get("call_error"):
            raise RuntimeError(
                "a test60 letter call failed"
                if holdout
                else f"{letter.letter_id} call failed: {row['call_error']}"
            )
        by_id[letter.letter_id] = row
        rows = [by_id[item.letter_id] for item in letters if item.letter_id in by_id]
        write_jsonl_rows(rows, rows_path)
        if progress_every and index % progress_every == 0:
            print(f"{spec.slug} {method} {split}: {len(rows)}/{len(letters)}", flush=True)
    if len(by_id) != len(letters):
        raise RuntimeError(f"{method} {split} has {len(by_id)} rows, expected {len(letters)}")
    rows = [by_id[letter.letter_id] for letter in letters]
    write_jsonl_rows(rows, rows_path)
    artifact = comparison_from_later_stage_rows(
        method,
        letters,
        rows,
        existing={
            "started_utc": started,
            "finished_utc": datetime.now(UTC).isoformat(),
            "live": True,
            "call_transport": "openrouter_batch",
            "model_calls": len(todo),
        },
        slug=spec.slug,
        model=spec.model,
        split=split,
        prompt=prompt,
    )
    out = work_root / "comparison.json"
    out.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "ok": True,
        "artifact": out.relative_to(ROOT).as_posix(),
        "live": True,
        "method": method,
        "split": split,
        "model": spec.model,
        "model_calls": artifact["model_calls"],
        "summary": artifact["summary"],
        "default_prompt_version": prompt,
    }


def _prompt_input(
    method: LaterStageMethod,
    *,
    extract_mentions: Sequence[Mapping[str, Any]],
    encode_row: Mapping[str, Any] | None,
) -> str:
    if method == "exect_llm_encode":
        return build_llm_encode_prompt_input(extract_mentions)
    if encode_row is None:
        raise RuntimeError("select row is missing its encode row")
    return build_llm_select_prompt_input(list(encode_row["encoded_mentions"]))


def score_later_stage_row(
    method: LaterStageMethod,
    letter: ExectLetter,
    raw_output: str,
    *,
    extract_mentions: Sequence[Mapping[str, Any]],
    encode_row: Mapping[str, Any] | None,
    split: str,
) -> dict[str, Any]:
    parse_errors: list[str] = []
    call_error = None if raw_output else "missing_raw_output"
    prompt_input = _prompt_input(
        method,
        extract_mentions=extract_mentions,
        encode_row=encode_row,
    )
    encoded = list(extract_mentions)
    selected = list(extract_mentions)
    try:
        if method == "exect_llm_encode":
            encoded = join_encode_mentions(
                extract_mentions, parse_encode_mentions(raw_output)
            )
            selected = encoded
        else:
            if encode_row is None:
                raise RuntimeError("select row is missing its encode row")
            encoded = list(encode_row["encoded_mentions"])
            selected = join_select_mentions(encoded, parse_select_mentions(raw_output))
    except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
        parse_errors.append(str(exc))
    return {
        "letter_id": letter.letter_id,
        "split": exect_machine_split(split),
        "paper_split": split,
        "prompt_version": prompt_version(method),
        "prompt_input_json": prompt_input,
        "raw_output": raw_output,
        "call_error": call_error,
        "parse_errors": parse_errors,
        "extract_mentions": list(extract_mentions),
        "encoded_mentions": encoded,
        "selected_mentions": selected,
    }


def _existing_complete_rows(path: Path, prompt_version_name: str) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in load_jsonl_rows(path):
        letter_id = str(row.get("letter_id") or "")
        if not letter_id or letter_id in seen:
            continue
        if row.get("prompt_version") != prompt_version_name:
            raise RuntimeError(f"{path} has {letter_id} with {row.get('prompt_version')}")
        if row.get("call_error") or not row.get("raw_output"):
            continue
        seen.add(letter_id)
        rows.append(row)
    return rows
