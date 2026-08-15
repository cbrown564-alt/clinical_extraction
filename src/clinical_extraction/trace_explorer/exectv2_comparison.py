"""Project retained ExECTv2 dev140 evidence into the frontend run contract.

The explorer compares the six models under the fixed decision-0041 one-call
architecture.  Each retained run contributes two views: the raw structured model
output and the final output after bounded deterministic assembly.  The no-call
deterministic all-9 pipeline is the common rules-only comparator.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration import (
    rules,
    structured_one_call,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
    RULES_METHOD_ALIASES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    clinical_headline_unit_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    aggregate_scores,
    clinical_headline_scores,
)

FAMILIES: tuple[str, ...] = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)


@dataclass(frozen=True)
class RetainedModelRun:
    slug: str
    label: str
    model: str
    package_date: str = "20260715"

    @property
    def summary_name(self) -> str:
        return (
            f"exectv2_six_model_single_call_{self.slug}_dev140_{self.package_date}.json"
        )

    @property
    def rows_name(self) -> str:
        return (
            f"exectv2_six_model_single_call_{self.slug}_dev140_{self.package_date}.jsonl"
        )

    @property
    def display_date(self) -> str:
        return f"{self.package_date[:4]}-{self.package_date[4:6]}-{self.package_date[6:]}"


RETAINED_MODEL_RUNS: tuple[RetainedModelRun, ...] = (
    RetainedModelRun("gpt56luna", "GPT-5.6 Luna", "openai/gpt-5.6-luna"),
    RetainedModelRun(
        "gemini37flash",
        "Gemini 3.7 Flash",
        "gemini/gemini-3.7-flash",
        package_date="20260813",
    ),
    RetainedModelRun("gpt56sol", "GPT-5.6 Sol", "openai/gpt-5.6-sol"),
    RetainedModelRun(
        "deepseek_v4_flash",
        "DeepSeek V4 Flash",
        "deepseek/deepseek-v4-flash",
    ),
    RetainedModelRun("qwen36_35b", "Qwen 3.6:35B", "ollama_chat/qwen3.6:35b"),
    RetainedModelRun("gemma4_26b", "Gemma 4 26B", "ollama_chat/gemma4:26b"),
)

MODEL_CLAIM_BOUNDARY = (
    "Retained dev140-only comparison under the fixed decision-0041 one-call, "
    "model-led architecture; not a locked-test, full-corpus, or benchmark claim."
)
DETERMINISTIC_CLAIM_BOUNDARY = (
    "Dev140-only no-call deterministic all-9 baseline, projected to the four "
    "clinical-recovery families; not a locked-test, full-corpus, or benchmark claim."
)


def build_exectv2_comparison(repo_root: Path) -> dict[str, Any]:
    """Build the 13-condition explorer payload from permitted retained evidence."""

    root = repo_root.resolve()
    experiments = root / "experiments"
    data_root = root / "data" / "ExECTv2 (2025)"
    gold_letters = load_letters_for_split(
        "dev",
        manifest_path=data_root / "splits" / "exectv2_split_v2.json",
        json_dir=data_root / "Json",
        text_dir=data_root / "Gold1-200_corrected_spelling",
    )
    if len(gold_letters) != 140:
        raise ValueError(f"expected the governed dev140 split, found {len(gold_letters)} rows")
    gold_by_id = {letter.letter_id: letter for letter in gold_letters}

    final_runs: list[dict[str, Any]] = []
    raw_runs: list[dict[str, Any]] = []
    for retained in RETAINED_MODEL_RUNS:
        summary_path = experiments / retained.summary_name
        rows_path = experiments / retained.rows_name
        summary = _read_object(summary_path)
        rows = _read_jsonl(rows_path)
        _validate_retained_run(retained, summary, rows, gold_by_id)
        final_runs.append(
            _model_run(
                retained=retained,
                summary=summary,
                rows=rows,
                gold_by_id=gold_by_id,
                active_method_lane="llm_with_rules",
                source_key="predicted_mentions",
                score_key="headline_target",
                summary_path=summary_path.relative_to(root),
                rows_path=rows_path.relative_to(root),
            )
        )
        raw_runs.append(
            _model_run(
                retained=retained,
                summary=summary,
                rows=rows,
                gold_by_id=gold_by_id,
                active_method_lane="llm",
                source_key="raw_lane_mentions",
                score_key="raw_lane_score",
                summary_path=summary_path.relative_to(root),
                rows_path=rows_path.relative_to(root),
            )
        )

    deterministic = _deterministic_run(root, gold_letters)
    runs = [*final_runs, *raw_runs, deterministic]
    return {
        "generated_on": "2026-07-18",
        "source_index": (
            "docs/experiments/exectv2/reliability/"
            "exectv2_six_model_comparison_protocol_2026-07-15.md"
        ),
        **_compact_letters(runs),
    }


def write_exectv2_comparison(repo_root: Path, output: Path) -> Path:
    """Materialize the compact frontend projection without changing source evidence."""

    payload = build_exectv2_comparison(repo_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    return output


def _model_run(
    *,
    retained: RetainedModelRun,
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, ExectLetter],
    active_method_lane: Literal["llm_with_rules", "llm"],
    source_key: str,
    score_key: str,
    summary_path: Path,
    rows_path: Path,
) -> dict[str, Any]:
    is_final = active_method_lane == "llm_with_rules"
    surface = _mapping(_mapping(summary["score_ladder"])[score_key])
    lane_diagnostics = _mapping(summary["lane_diagnostics"])
    if is_final:
        # Re-run HEAD deterministic assembly on raw outputs for current stack repairs.
        structured_by_id = _structured_rows_by_id(rows_path)
        letters = []
        for row in rows:
            gold = gold_by_id[str(row["letter_id"])]
            structured = structured_by_id.get(str(row["letter_id"]), {})
            raw_out = row.get("raw_output") or structured.get("raw_output")
            if raw_out:
                producer = structured_one_call.produce_structured_letter(
                    gold,
                    model=retained.model,
                    mode="prompt-only",
                    raw_output=raw_out,
                    split="dev140",
                )
                result = structured_one_call.run_llm_with_rules_letter(gold, producer)
                predicted_mentions_payload = _list_of_mappings(
                    result.row.get("predicted_mentions")
                )
                if not predicted_mentions_payload:
                    predicted_mentions_payload = [
                        m.model_dump(mode="json") for m in result.prediction.mentions
                    ]
            else:
                predicted_mentions_payload = _list_of_mappings(row.get(source_key))
            letters.append(
                _frontend_letter(
                    gold=gold,
                    predicted=predicted_mentions_payload,
                    source_model=retained.model,
                )
            )
    else:
        letters = [
            _frontend_letter(
                gold=gold_by_id[str(row["letter_id"])],
                predicted=_list_of_mappings(row.get(source_key)),
                source_model=retained.model,
            )
            for row in rows
        ]
    mode_label = "LLM + rules" if is_final else "LLM only"
    run_id = (
        f"exectv2_winning_mode_{retained.slug}_"
        f"{'llm_plus_rules' if is_final else 'llm_only'}_dev140"
    )
    payload = {
        "run_id": run_id,
        "task": "exectv2",
        "label": f"{retained.label} · {mode_label}",
        "model": retained.model,
        "kind": active_method_lane,
        "architecture_family": "decision_0041_model_led_single_call",
        # The saved frontend run id and source artifact remain immutable.  Only
        # the active outward method identity changes for the raw lane.
    "pipeline_family": "exectv2_model_led_key_family_event_ledger",
        "split": "dev140",
        "row_count": 140,
        "date": retained.display_date,
        "decision": "control" if is_final else "diagnostic",
        "promotion_decision": "winning-mode comparison" if is_final else "raw comparator",
        "claim_boundary": MODEL_CLAIM_BOUNDARY,
        "scorer_view": score_key,
        "artifact_paths": [summary_path.as_posix(), rows_path.as_posix()],
        "source_paths": [rows_path.as_posix()],
        "metrics": _frontend_metrics(surface),
        "operational": _model_operational(
            lane_diagnostics,
            letters,
            final=is_final,
        ),
        "letters": letters,
    }
    if not is_final:
        payload.pop("active_method", None)
        payload["pipeline_family"] = "llm"
        payload["source_pipeline_family"] = "exectv2_model_led_key_family_event_ledger"
        if retained.slug == "gpt56sol":
            payload["active_method"] = "llm"
            payload["method_id"] = "llm"
    elif retained.slug == "gpt56sol":
        payload["active_method"] = "llm_with_rules"
        payload["method_id"] = "llm_with_rules"
    return payload


def _deterministic_run(root: Path, gold_letters: Sequence[ExectLetter]) -> dict[str, Any]:
    predictions = [rules.run_letter(letter).prediction for letter in gold_letters]
    pred_letters = [
        to_exect_letter(prediction, note_text=gold.note_text)
        for prediction, gold in zip(predictions, gold_letters, strict=True)
    ]
    family_scores = clinical_headline_scores(list(gold_letters), pred_letters)
    surface = {
        "overall": aggregate_scores(family_scores.values()),
        "by_indicator": family_scores,
    }
    letters = [
        _frontend_letter(
            gold=gold,
            predicted=_prediction_mappings(prediction),
            source_model="",
        )
        for gold, prediction in zip(gold_letters, predictions, strict=True)
    ]
    by_family = {
        family: _operational_for_mentions(
            mention
            for letter in letters
            for mention in letter["predicted_mentions"]
            if mention["entity"] == family
        )
        for family in FAMILIES
    }
    exact_count = sum(int(item["exact_evidence_mentions"]) for item in by_family.values())
    scored_count = sum(int(item["scored_mentions"]) for item in by_family.values())
    summary_path = Path("experiments/exectv2_deterministic_all9_dev_20260714.json")
    if not (root / summary_path).is_file():
        raise FileNotFoundError(root / summary_path)
    return {
        # `rules` is the active outward identity.  Keep the historical saved
        # artifact/run name explicit because replay manifests depend on it.
        "run_id": "rules",
        "saved_run_id": "exectv2_deterministic_all9_dev140",
        "retained_evidence_id": "exectv2_deterministic_all9_dev_20260714",
        "legacy_run_ids": [
            *RULES_METHOD_ALIASES[1:],
            "exectv2_deterministic_all9_dev140",
            "exectv2_deterministic_all9_dev_20260714",
        ],
        "task": "exectv2",
        "label": "Deterministic all-9 · rules only",
        "model": "(model-independent)",
        "kind": "rules",
        "architecture_family": "rules",
        "pipeline_family": "rules",
        "split": "dev140",
        "row_count": 140,
        "date": "2026-07-14",
        "decision": "diagnostic",
        "promotion_decision": "rules-only comparator",
        "claim_boundary": DETERMINISTIC_CLAIM_BOUNDARY,
        "scorer_view": "clinical_headline",
        "artifact_paths": [summary_path.as_posix()],
        "source_paths": [
            "src/clinical_extraction/tasks/epilepsy_phenotyping/exectv2/"
            "deterministic/all_entities/orchestrator.py"
        ],
        "metrics": _frontend_metrics(surface),
        "operational": {
            "call_failures": 0,
            "parse_schema_failures": 0,
            "evidence_invalid_dropped": 0,
            "exact_evidence_rate": round(exact_count / scored_count, 4)
            if scored_count
            else 1.0,
            "by_family": by_family,
        },
        "letters": letters,
    }


def _compact_letters(runs: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Store shared source/gold data once and keep only predictions per run."""

    if not runs:
        return {"shared_letters": [], "runs": []}
    first_letters = _list_of_mappings(runs[0].get("letters"))
    shared_letters = [
        {
            "letter_id": letter["letter_id"],
            "split": letter["split"],
            "stage": letter["stage"],
            "letter_text": letter["letter_text"],
            "gold_mentions": letter["gold_mentions"],
            "gold_family_counts": _mapping(letter["family_counts"])["gold"],
            "evidence_spans": [
                span
                for span in letter["evidence_spans"]
                if isinstance(span, Mapping) and span.get("kind") == "gold"
            ],
        }
        for letter in first_letters
    ]
    compact_runs = []
    for run in runs:
        compact = {key: value for key, value in run.items() if key != "letters"}
        compact["letters"] = [
            {
                "letter_id": letter["letter_id"],
                "split": letter["split"],
                "stage": letter["stage"],
                "predicted_mentions": letter["predicted_mentions"],
                "predicted_family_counts": _mapping(letter["family_counts"])[
                    "predicted"
                ],
                "evidence_spans": [
                    span
                    for span in letter["evidence_spans"]
                    if isinstance(span, Mapping) and span.get("kind") == "llm"
                ],
            }
            for letter in _list_of_mappings(run.get("letters"))
        ]
        compact_runs.append(compact)
    return {"shared_letters": shared_letters, "runs": compact_runs}


def _structured_rows_by_id(rows_path: Path) -> dict[str, Mapping[str, Any]]:
    """Load the sibling structured jsonl used for no-call HEAD reassembly."""

    path = Path(rows_path)
    structured_name = path.name.replace(".jsonl", "_structured.jsonl")
    candidates = [path.with_name(structured_name)]
    if not path.is_absolute():
        candidates.append(Path.cwd() / path.with_name(structured_name))
    for candidate in candidates:
        if candidate.is_file():
            return {str(row["letter_id"]): row for row in _read_jsonl(candidate)}
    return {}


def _project_predicted_cuis(
    predicted: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Attach known CUI/CUIPhrase values that assembly residuals may omit."""

    letter = PredictedLetter(
        letter_id="frontend",
        mentions=tuple(
            PredictedMention(
                entity=str(item.get("entity") or ""),
                text=str(item.get("text") or ""),
                attributes=_string_mapping(item.get("attributes")),
                evidence=str(item.get("evidence") or item.get("text") or ""),
                component_owner=str(item.get("component_owner") or ""),
            )
            for item in predicted
        ),
    )
    projected = {id(before): after for before, after in zip(
        letter.mentions, project_cuis(letter).mentions, strict=True
    )}
    out: list[dict[str, Any]] = []
    for item, mention in zip(predicted, letter.mentions, strict=True):
        payload = dict(item)
        payload["attributes"] = dict(projected[id(mention)].attributes)
        out.append(payload)
    return out


def _frontend_letter(
    *,
    gold: ExectLetter,
    predicted: Sequence[Mapping[str, Any]],
    source_model: str,
) -> dict[str, Any]:
    gold_payloads = [_annotation_mapping(annotation) for annotation in gold.annotations]
    gold_payloads = [item for item in gold_payloads if item["entity"] in FAMILIES]
    predicted_payloads = _project_predicted_cuis(
        [item for item in predicted if str(item.get("entity")) in FAMILIES]
    )
    gold_mentions = [
        _frontend_mention(
            item,
            letter_id=gold.letter_id,
            index=index,
            source="gold",
            source_model="",
        )
        for index, item in enumerate(gold_payloads)
    ]
    predicted_mentions = [
        _frontend_mention(
            item,
            letter_id=gold.letter_id,
            index=index,
            source="predicted",
            source_model=source_model,
        )
        for index, item in enumerate(predicted_payloads)
    ]
    return {
        "letter_id": gold.letter_id,
        "split": "dev",
        "stage": "dev140",
        "letter_text": gold.note_text,
        "gold_mentions": gold_mentions,
        "predicted_mentions": predicted_mentions,
        "family_counts": {
            "gold": _headline_counts(gold_payloads, gold.note_text),
            "predicted": _headline_counts(predicted_payloads, gold.note_text),
        },
        "evidence_spans": _evidence_spans(
            note_text=gold.note_text,
            gold=gold_payloads,
            predicted=predicted_payloads,
        ),
    }


# Assembly always appends a wrap-up event even when the mention is unchanged.
# Those events, plus the producer emission, are the hybrid baseline and are
# not useful on the review card.
_BASELINE_PROVENANCE_ACTIONS = frozenset(
    {
        "emitted_raw_candidate",
        "emitted_scored_candidate",
        "selected_saved_artifact_mentions",
        "applied_standard_dictionary_prescription_repair",
        "applied_standard_dictionary_diagnosis_repair",
    }
)


def last_diverging_provenance_event(
    mention: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    """Return the last provenance event that changed this mention, else None."""

    events = mention.get("provenance")
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        return None
    for event in reversed(events):
        if not isinstance(event, Mapping):
            continue
        action = str(event.get("action") or "").strip()
        if action and action not in _BASELINE_PROVENANCE_ACTIONS:
            return event
    return None


def last_diverging_provenance_action(mention: Mapping[str, Any]) -> str:
    """Return the last rule action that changed this mention, else empty.

    Gold mentions and unchanged model findings stay blank. The wrap-up lens
    events fire on every finding, so they are treated as baseline.
    """

    event = last_diverging_provenance_event(mention)
    if event is None:
        return ""
    return str(event.get("action") or "").strip()


def last_rule_label(mention: Mapping[str, Any]) -> str:
    """Plain sentence for the last diverging rule, with before/after when known."""

    event = last_diverging_provenance_event(mention)
    if event is None:
        return ""
    action = str(event.get("action") or "").strip()
    detail = event.get("detail")
    detail_map = detail if isinstance(detail, Mapping) else {}
    if action == "normalized_prescription_from_dictionary":
        changes = _format_attribute_changes(detail_map)
        if changes:
            return f"Dictionary {changes}"
        return "Dictionary normalized this regimen"
    if action == "split_prescription_regimen_from_dictionary":
        source = str(detail_map.get("source_text") or "").strip()
        target = str(detail_map.get("target_text") or "").strip()
        after = detail_map.get("after_attributes")
        after_map = after if isinstance(after, Mapping) else {}
        dose = f"{after_map.get('DrugDose', '')}{after_map.get('DoseUnit', '')}".strip()
        piece = target or dose
        if source and piece:
            return f"Dictionary split “{source}” into this dose ({piece})"
        if piece:
            return f"Dictionary split the regimen into this dose ({piece})"
        return "Dictionary split this regimen"
    if action == "rewrote_diagnosis_convention_from_dictionary":
        source = str(detail_map.get("source_text") or "").strip()
        target = str(detail_map.get("target_text") or "").strip()
        if source and target:
            return f"Dictionary rewrote “{source}” to “{target}”"
        return "Dictionary rewrote the diagnosis wording"
    if action == "added_diagnosis_residual_from_dictionary":
        target = str(detail_map.get("target_text") or "").strip()
        if target:
            return f"Dictionary added “{target}” from the letter"
        return "Dictionary added this diagnosis"
    if action == "added_sf_residual_convention_from_dictionary":
        target = str(detail_map.get("target_text") or "").strip()
        if target:
            return f"Dictionary added “{target}” from the letter"
        return "Dictionary added this seizure-frequency fact"
    return action.replace("_", " ")


def _format_attribute_changes(detail: Mapping[str, Any]) -> str:
    raw = detail.get("attribute_changes")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return ""
    parts: list[str] = []
    for item in raw:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("attribute") or "").strip()
        before = str(item.get("before") or "").strip()
        after = str(item.get("after") or "").strip()
        if not name or not after:
            continue
        if before:
            parts.append(f"set {name} from {before} to {after}")
        else:
            parts.append(f"set {name} to {after}")
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + f", and {parts[-1]}"


def _frontend_mention(
    mention: Mapping[str, Any],
    *,
    letter_id: str,
    index: int,
    source: Literal["gold", "predicted"],
    source_model: str,
) -> dict[str, Any]:
    attributes = _string_mapping(mention.get("attributes"))
    finding_id = str(mention.get("finding_id") or "")
    evidence = str(
        mention.get("evidence")
        or mention.get("raw_text")
        or mention.get("text")
        or ""
    )
    return {
        "id": finding_id or f"{letter_id}:{source}:{index}",
        "source": source,
        "entity": str(mention.get("entity") or ""),
        "text": str(mention.get("text") or ""),
        "evidence": evidence,
        "evidence_valid": bool(mention.get("evidence_valid", True)),
        "component_owner": str(mention.get("component_owner") or ""),
        "source_lane": str(mention.get("source_lane") or ""),
        "source_model": str(mention.get("source_model") or source_model),
        "confidence": str(mention.get("confidence") or ""),
        "assertion": str(mention.get("assertion") or ""),
        "attributes": attributes,
        "status": source,
        "headline_status": "",
        "last_rule_action": last_diverging_provenance_action(mention),
        "last_rule_label": last_rule_label(mention),
    }


def _headline_counts(
    mentions: Sequence[Mapping[str, Any]], note_text: str
) -> dict[str, int]:
    annotations = [_annotation_from_mapping(item) for item in mentions]
    return {
        family: len(
            clinical_headline_unit_keys(
                family,
                [annotation for annotation in annotations if annotation.entity == family],
                note_text,
            )
        )
        for family in FAMILIES
    }


def _evidence_spans(
    *,
    note_text: str,
    gold: Sequence[Mapping[str, Any]],
    predicted: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    seen: set[tuple[int, int, str, str]] = set()
    for kind, mentions in (("llm", predicted), ("gold", gold)):
        for mention in mentions:
            located = _locate_evidence(note_text, mention)
            if located is None:
                continue
            start, end, evidence = located
            entity = str(mention.get("entity") or "")
            key = (start, end, entity, kind)
            if key in seen:
                continue
            seen.add(key)
            spans.append(
                {
                    "start": start,
                    "end": end,
                    "text": evidence,
                    "entity": entity,
                    "kind": kind,
                    "label": f"{'predicted' if kind == 'llm' else 'gold'} {entity}",
                }
            )
    return spans


def _locate_evidence(
    note_text: str, mention: Mapping[str, Any]
) -> tuple[int, int, str] | None:
    span = mention.get("evidence_span")
    if isinstance(span, Mapping):
        start = span.get("start_char")
        end = span.get("end_char")
        if isinstance(start, int) and isinstance(end, int) and note_text[start:end]:
            return start, end, note_text[start:end]

    candidates = [
        str(mention.get("evidence") or ""),
        str(mention.get("raw_text") or ""),
        str(mention.get("text") or ""),
    ]
    candidates.extend(candidate.replace("-", " ") for candidate in tuple(candidates))
    lowered = note_text.casefold()
    for candidate in candidates:
        clean = candidate.strip()
        if not clean:
            continue
        start = lowered.find(clean.casefold())
        if start >= 0:
            end = start + len(clean)
            return start, end, note_text[start:end]
    return None


def _frontend_metrics(surface: Mapping[str, Any]) -> dict[str, Any]:
    overall = _mapping(surface["overall"])
    by_indicator = _mapping(surface["by_indicator"])
    return {
        "overall_f1": _rounded(overall.get("f1")),
        "precision": _rounded(overall.get("precision")),
        "recall": _rounded(overall.get("recall")),
        "families": {
            family: _family_metrics(_mapping(by_indicator[family])) for family in FAMILIES
        },
    }


def _family_metrics(score: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "f1": _rounded(score.get("f1")),
        "precision": _rounded(score.get("precision")),
        "recall": _rounded(score.get("recall")),
        "tp": _optional_int(score.get("tp")),
        "fp": _optional_int(score.get("fp")),
        "fn": _optional_int(score.get("fn")),
    }


def _model_operational(
    lane_diagnostics: Mapping[str, Any],
    letters: Sequence[Mapping[str, Any]],
    *,
    final: bool,
) -> dict[str, Any]:
    by_family: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        retained = dict(_mapping(lane_diagnostics[family]))
        if not final:
            mentions = (
                mention
                for letter in letters
                for mention in letter["predicted_mentions"]
                if mention["entity"] == family
            )
            computed = _operational_for_mentions(mentions)
            retained.update(
                {
                    "raw_mentions": computed["raw_mentions"],
                    "scored_mentions": computed["scored_mentions"],
                    "exact_evidence_mentions": computed["exact_evidence_mentions"],
                    "exact_evidence_rate": computed["exact_evidence_rate"],
                }
            )
        by_family[family] = retained
    total_exact = sum(int(item.get("exact_evidence_mentions", 0)) for item in by_family.values())
    total_scored = sum(int(item.get("scored_mentions", 0)) for item in by_family.values())
    return {
        "call_failures": max(int(item.get("call_failures", 0)) for item in by_family.values()),
        "parse_schema_failures": max(
            int(item.get("parse_schema_failures", 0)) for item in by_family.values()
        ),
        "evidence_invalid_dropped": sum(
            int(item.get("evidence_invalid_dropped", 0)) for item in by_family.values()
        ),
        "exact_evidence_rate": round(total_exact / total_scored, 4)
        if total_scored
        else 1.0,
        "by_family": by_family,
    }


def _operational_for_mentions(mentions: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    items = list(mentions)
    exact = sum(bool(item.get("evidence_valid")) for item in items)
    return {
        "call_failures": 0,
        "parse_schema_failures": 0,
        "evidence_invalid_dropped": 0,
        "raw_mentions": len(items),
        "scored_mentions": len(items),
        "exact_evidence_mentions": exact,
        "exact_evidence_rate": round(exact / len(items), 4) if items else 1.0,
    }


def _prediction_mappings(prediction: PredictedLetter) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    for index, mention in enumerate(prediction.mentions):
        payload = mention.model_dump(mode="json")
        payload.update(
            {
                "finding_id": f"{prediction.letter_id}:deterministic:{index}",
                "source_lane": "deterministic_all9",
                "source_model": "",
                "evidence_valid": True,
            }
        )
        result.append(payload)
    return result


def _annotation_mapping(annotation: ExectAnnotation) -> dict[str, Any]:
    return {
        "entity": annotation.entity,
        "text": annotation.text,
        "raw_text": annotation.raw_text or annotation.text,
        "attributes": dict(annotation.attributes),
        "start_index": annotation.start_index,
        "end_index": annotation.end_index,
        "evidence_valid": True,
    }


def _annotation_from_mapping(mention: Mapping[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(mention.get("entity") or ""),
        text=str(mention.get("text") or ""),
        attributes=_string_mapping(mention.get("attributes")),
    )


def _validate_retained_run(
    retained: RetainedModelRun,
    summary: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    gold_by_id: Mapping[str, ExectLetter],
) -> None:
    model_swap = _mapping(summary.get("model_swap"))
    if model_swap.get("model") != retained.model:
        raise ValueError(f"retained model mismatch for {retained.slug}")
    if summary.get("split") != "dev140" or int(summary.get("row_count", 0)) != 140:
        raise ValueError(f"retained run {retained.slug} is not the governed dev140 run")
    ids = [str(row.get("letter_id")) for row in rows]
    if len(ids) != 140 or Counter(ids) != Counter(gold_by_id.keys()):
        raise ValueError(f"retained rows for {retained.slug} do not match dev140")


def _read_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"expected object at {path}:{line_number}")
            rows.append(value)
    return rows


def _mapping(value: object) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise TypeError("expected mapping")
    return value


def _list_of_mappings(value: object) -> list[Mapping[str, Any]]:
    if not isinstance(value, list) or not all(isinstance(item, Mapping) for item in value):
        raise TypeError("expected list of mappings")
    return value


def _string_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): str(item) for key, item in value.items() if item is not None}


def _rounded(value: object) -> float | None:
    if value is None:
        return None
    if not isinstance(value, (str, int, float)):
        raise TypeError("expected numeric value")
    return round(float(value), 4)


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if not isinstance(value, (str, int, float)):
        raise TypeError("expected integer value")
    return int(value)
