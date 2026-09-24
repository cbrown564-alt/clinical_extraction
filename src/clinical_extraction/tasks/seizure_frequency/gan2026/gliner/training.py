"""Training data and configuration for fine-tuning GLiNER2.5-Decide on the adapted task.

Targets mirror the two adapted conditions:

* ``minimal``: the native Purist band (from the Gan gold label) and, when Gan's
  reference quotations appear verbatim in the note, those quotations as the evidence
  entity. A row whose quotations are absent keeps its label but gets no evidence
  target, so it never teaches "no evidence"; a no-reference row teaches an empty span.
* ``expanded``: the ``minimal`` target plus one ``seizure_frequency_finding`` per
  dev750 reference finding. Only dev750 has reference findings, so the expanded
  target is trained by cross-validation over dev750 folds.

Numeric fields are aligned to note wording by searching the finding's own evidence for
the shortest phrase that the format normaliser reads as the reference value. That is
training-data construction only; unaligned fields are omitted and counted.

No test-split rows are read. torch and gliner2 are imported only by ``run``.
"""

from __future__ import annotations

import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Any

from clinical_extraction.core.evidence import clean_semantically_neutral_text_artifacts
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    SEIZURE_FREQUENCY_KEY,
    GanFrequencyRecord,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gliner import normalize, schema
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

FOLD_SEED = 20260925
MAX_PHRASE_WORDS = 6


def reference_quotes(record: GanFrequencyRecord) -> list[str]:
    """Gan reference quotations for the frequency label that occur verbatim in the note."""
    value = record.raw[SEIZURE_FREQUENCY_KEY].get("reference") or []
    quotes = value if isinstance(value, list) else [value]
    found = []
    for quote in quotes:
        if not isinstance(quote, str):
            continue
        for candidate in (quote.strip(), clean_semantically_neutral_text_artifacts(quote).strip()):
            if candidate and candidate in record.note_text and candidate not in found:
                found.append(candidate)
                break
    return found


def quote_spans(record: GanFrequencyRecord, quotes: list[str]) -> list[tuple[int, int]]:
    spans = []
    for quote in quotes:
        at = record.note_text.find(quote)
        while at >= 0:
            spans.append((at, at + len(quote)))
            at = record.note_text.find(quote, at + 1)
    return spans


def purist(record: GanFrequencyRecord) -> str:
    return str(map_purist(record.gold_monthly_frequency))


def _phrases(text: str) -> list[str]:
    words = list(re.finditer(r"\S+", text))
    phrases = []
    for size in range(1, MAX_PHRASE_WORDS + 1):
        for i in range(len(words) - size + 1):
            phrases.append(text[words[i].start() : words[i + size - 1].end()].strip(".,;:()"))
    return [p for p in phrases if p]


def _same(parsed: dict[str, Any] | None, target: dict[str, Any]) -> bool:
    if not parsed:
        return False
    keys = [k for k in target if k != "kind"]
    return parsed.get("kind") == target.get("kind") and all(
        parsed.get(k) == target[k] for k in keys
    )


def align(evidence: list[str], target: dict[str, Any] | None, reader: Any) -> str | None:
    """Shortest phrase in the evidence that ``reader`` maps to ``target``."""
    if not target or target.get("kind") == "verbatim":
        return target.get("text") if target and _in_any(target.get("text"), evidence) else None
    for quote in evidence:
        for phrase in _phrases(quote):
            if _same(reader(phrase), target):
                return phrase
    return None


def _in_any(text: str | None, evidence: list[str]) -> bool:
    return text is not None and bool(text) and any(text in quote for quote in evidence)


def _choice(value: str, choices: list[str]) -> dict[str, Any]:
    return {"value": value, "choices": choices}


def finding_structure(
    finding: dict[str, Any], note: str, tally: Counter[str]
) -> dict[str, Any] | None:
    evidence = [q for q in finding["evidence"] if q in note]
    if not evidence:
        tally["finding_dropped_no_verbatim_evidence"] += 1
        return None
    measurement = finding["measurement"]
    kind = measurement["kind"]
    fields: dict[str, Any] = {"evidence": evidence[0]}
    label = finding["event"]["label"]
    if label in note:
        fields["event"] = label
    else:
        tally["event_unaligned"] += 1
    quantity_target = measurement.get("quantity") or measurement.get("count")
    if quantity_target:
        phrase = align(evidence, quantity_target, normalize.quantity)
        tally["quantity_aligned" if phrase else "quantity_unaligned"] += 1
        if phrase:
            fields["quantity"] = phrase
    per_target = measurement.get("per") or measurement.get("duration")
    per_field = "window" if kind == "seizure_free" else "per"
    if per_target:
        phrase = align(evidence, per_target, normalize.duration)
        tally[f"{per_field}_aligned" if phrase else f"{per_field}_unaligned"] += 1
        if phrase:
            fields[per_field] = phrase
    source = (
        finding["time"].get("source") or measurement.get("since") or measurement.get("occurred_at")
    )
    if source and source in note and "window" not in fields:
        fields["window"] = source
    per_cluster = measurement.get("seizures_per_cluster")
    if per_cluster:
        phrase = align(evidence, per_cluster, normalize.quantity)
        if phrase:
            fields["seizures_per_cluster"] = phrase
    if finding.get("restriction") and finding["restriction"] in note:
        fields["restriction"] = finding["restriction"]
    fields["kind"] = _choice(kind, schema.KINDS)
    fields["phase"] = _choice(finding["time"]["phase"], schema.PHASES)
    fields["scope"] = _choice(finding["event"]["scope"], schema.SCOPES)
    fields["counted_unit"] = _choice(finding["counted_unit"], schema.COUNTED_UNITS)
    fields["status"] = _choice(finding["status"], schema.STATUSES)
    fields["level"] = _choice(measurement.get("level", "not_applicable"), schema.LEVELS)
    tally["finding_kept"] += 1
    return {schema.FINDING: fields}


def example(
    record: GanFrequencyRecord,
    target: schema.Condition,
    reference: list[dict[str, Any]] | None,
    tally: Counter[str],
) -> dict[str, Any]:
    gold = purist(record)
    output: dict[str, Any] = {
        "classifications": [
            {
                "task": schema.ANSWER_TASK,
                "labels": list(schema.PURIST_LABELS),
                "true_label": [schema.PURIST_TO_LABEL[gold]],
                "label_descriptions": schema.answer_labels(),
            }
        ]
    }
    quotes = reference_quotes(record)
    no_reference = record.gold_label.strip().lower() == "no seizure frequency reference"
    if quotes or no_reference:
        output["entities"] = {schema.EVIDENCE_ENTITY: quotes}
        output["entity_descriptions"] = {schema.EVIDENCE_ENTITY: schema.EVIDENCE_DESCRIPTION}
        tally["evidence_target"] += 1
    else:
        tally["evidence_omitted"] += 1
    if target == "expanded":
        structures = [
            s for f in reference or [] if (s := finding_structure(f, record.note_text, tally))
        ]
        output["json_structures"] = structures
        output["json_descriptions"] = {
            schema.FINDING: {name: desc for name, _, _, desc in schema.FINDING_FIELDS}
        }
    return {
        "source_row_index": record.source_row_index,
        "input": record.note_text,
        "output": output,
    }


def examples(
    records: list[GanFrequencyRecord],
    target: schema.Condition,
    reference: dict[int, list[dict[str, Any]]] | None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    tally: Counter[str] = Counter()
    if target == "expanded" and reference is None:
        raise ValueError("The expanded target needs reference findings")
    rows = [example(r, target, (reference or {}).get(r.source_row_index), tally) for r in records]
    return rows, dict(sorted(tally.items()))


def folds(records: list[GanFrequencyRecord], k: int, seed: int) -> dict[str, Any]:
    """Letter-level folds stratified by gold Purist band."""
    by_band: dict[str, list[int]] = defaultdict(list)
    for record in sorted(records, key=lambda r: r.source_row_index):
        by_band[purist(record)].append(record.source_row_index)
    rng = random.Random(seed)
    assigned: list[list[int]] = [[] for _ in range(k)]
    offset = 0
    for band in sorted(by_band):
        rows = by_band[band]
        rng.shuffle(rows)
        for i, row in enumerate(rows):
            assigned[(i + offset) % k].append(row)
        offset += len(rows)
    return {
        "seed": seed,
        "stratified_by": "gold Purist band",
        "folds": [sorted(f) for f in assigned],
    }


@dataclass(frozen=True)
class Settings:
    """Per-device training settings. The effective batch is 16 letters everywhere."""

    batch_size: int
    gradient_accumulation_steps: int
    bf16: bool
    gradient_checkpointing: bool
    encoder_lr: float = 1e-5
    task_lr: float = 5e-4
    lora_r: int = 16
    lora_alpha: float = 32.0


def settings_for(device: str) -> Settings:
    """CUDA (8 GB, e.g. RTX 3070 laptop): batch 1, bf16 when supported, checkpointing.

    DeBERTa-v3 overflows in fp16, so fp16 is never used; a pre-Ampere card trains in
    fp32. Apple Silicon shares system memory: smoke tests only, fp32, small batch.
    """
    if device == "cuda":
        import torch

        return Settings(
            batch_size=1,
            gradient_accumulation_steps=16,
            bf16=torch.cuda.is_bf16_supported(),
            gradient_checkpointing=True,
        )
    return Settings(
        batch_size=1, gradient_accumulation_steps=16, bf16=False, gradient_checkpointing=True
    )


def config(
    *,
    output_dir: str,
    name: str,
    device: str,
    use_lora: bool,
    epochs: int,
    max_len: int | None,
    seed: int,
    max_steps: int = -1,
    settings: Settings | None = None,
) -> Any:
    from gliner2.training.trainer import TrainingConfig

    settings = settings or settings_for(device)
    return TrainingConfig(
        output_dir=output_dir,
        experiment_name=name,
        num_epochs=epochs,
        max_steps=max_steps,
        batch_size=settings.batch_size,
        eval_batch_size=1,
        gradient_accumulation_steps=settings.gradient_accumulation_steps,
        encoder_lr=settings.encoder_lr,
        task_lr=settings.task_lr,
        fp16=False,
        bf16=settings.bf16,
        gradient_checkpointing=settings.gradient_checkpointing,
        eval_strategy="epoch",
        save_best=True,
        metric_for_best="eval_loss",
        # Windows DataLoader workers re-import the process; keep loading in-process.
        num_workers=0,
        pin_memory=device == "cuda",
        seed=seed,
        max_len=max_len,
        use_lora=use_lora,
        lora_r=settings.lora_r,
        lora_alpha=settings.lora_alpha,
        save_adapter_only=use_lora,
        fused_optimizer=device == "cuda",
        logging_steps=10,
    )


def run(
    base_model: str, cfg: Any, train_rows: list[dict[str, Any]], eval_rows: list[dict[str, Any]]
) -> Any:
    from gliner2 import AutoExtractor
    from gliner2.training.data import InputExample
    from gliner2.training.trainer import ExtractorTrainer

    def load(rows: list[dict[str, Any]]) -> list[Any]:
        return [InputExample.from_dict({"input": r["input"], "output": r["output"]}) for r in rows]

    if not eval_rows:
        cfg.eval_strategy = "no"
        cfg.save_best = False
    model = AutoExtractor.from_pretrained(base_model)
    trainer = ExtractorTrainer(model=model, config=cfg)
    evaluation = load(eval_rows)
    if evaluation:
        return trainer.train(train_data=load(train_rows), eval_data=evaluation)
    return trainer.train(train_data=load(train_rows))
