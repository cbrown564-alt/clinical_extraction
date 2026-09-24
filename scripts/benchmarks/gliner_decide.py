"""Exploratory GLiNER2.5-Decide runs of the adapted minimal/expanded seizure-frequency task.

    .venv/bin/python -m scripts.benchmarks.gliner_decide check
    .venv/bin/python -m scripts.benchmarks.gliner_decide infer --condition minimal --context full
    .venv/bin/python -m scripts.benchmarks.gliner_decide score --run zs_minimal_full
    .venv/bin/python -m scripts.benchmarks.gliner_decide build-data
    .venv/bin/python -m scripts.benchmarks.gliner_decide train --target minimal --train train300

Local model only; no provider calls. Run one model job at a time; setup and
memory limits: docs/runbooks/gliner_local_gpu.md. Only the Gan train300 and dev750 splits are
readable here: the test split is refused. This is not a locked study condition; see
docs/research/gan2026/gliner_decide_exploration.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import time
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_DATA_PATH,
    DEFAULT_SPLIT_MANIFEST_PATH,
    GanFrequencyRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.gliner import (
    normalize,
    project,
    schema,
    training,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.one_call import analysis, findings_score

MODEL = "fastino/GLiNER2.5-Decide"
ROOT = Path("runs/seizure_frequency/gliner")
RESULTS = Path("results/letter-benchmarks/gan/gliner")
REFERENCE = Path("runs/seizure_frequency/reference/dev750.jsonl")
DEEPSEEK = Path("runs/seizure_frequency/one_call/dev750/per_letter.json")
SPLITS = {"train300": "train", "dev750": "validation"}
CHUNK_SIZE = 384
CHUNK_OVERLAP = 64
LONG_WORDS = 384


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def read_lines(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def records(split: str) -> list[GanFrequencyRecord]:
    if split not in SPLITS:
        raise ValueError("Only train300 and dev750 are readable by this runner")
    return sorted(load_records_for_split(SPLITS[split]), key=lambda r: r.source_row_index)


def gold(record: GanFrequencyRecord) -> dict[str, str]:
    value = record.gold_monthly_frequency
    return {"purist": str(map_purist(value)), "pragmatic": str(map_pragmatic(value))}


def device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    return "mps" if torch.backends.mps.is_available() else "cpu"


def load_model(checkpoint: str, adapter: str | None) -> Any:
    from gliner2 import AutoExtractor

    model = AutoExtractor.from_pretrained(checkpoint)
    if adapter:
        model.load_adapter(adapter)
    return model.to(device()).eval()


def package_versions() -> dict[str, str]:
    from importlib.metadata import version

    return {name: version(name) for name in ("gliner2", "torch", "transformers", "huggingface-hub")}


def identity(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "dataset": "Gan 2026 synthetic",
        "split": args.split,
        "row_policy": "all split rows including row_ok=False",
        "dataset_sha256": digest(DEFAULT_DATA_PATH.read_bytes()),
        "manifest_sha256": digest(DEFAULT_SPLIT_MANIFEST_PATH.read_bytes()),
        "condition": args.condition,
        "context": args.context,
        "chunking": (
            {"chunk_words": CHUNK_SIZE, "overlap_words": CHUNK_OVERLAP}
            if args.context == "chunked"
            else None
        ),
        "model": args.checkpoint,
        "adapter": args.adapter,
        "schema_sha256": schema.schema_sha256(args.condition),
        "schema": schema.schema_dict(args.condition),
        "threshold": args.threshold,
        "structure_mode": args.structure_mode,
        "projection": project.PROJECTION,
        "normalizer": normalize.NORMALIZER,
        "packages": package_versions(),
        "device": device(),
        "platform": platform.platform(),
        "replay": "raw GLiNER output saved; projection and scoring are offline",
        "repair_policy": "none; format-only span normalisation, guide defaults counted",
    }


def infer(args: argparse.Namespace) -> None:
    import torch

    run = args.run or f"zs_{args.condition}_{args.context}"
    out = ROOT / run
    out.mkdir(parents=True, exist_ok=True)
    ident = identity(args)
    existing = out / "identity.json"
    if existing.exists():
        saved = json.loads(existing.read_text())
        keep = (
            "schema_sha256",
            "model",
            "adapter",
            "context",
            "split",
            "threshold",
            "structure_mode",
            "device",
        )
        if any(saved[k] != ident[k] for k in keep):
            raise SystemExit(f"{run} exists with a different identity")
    else:
        write_json(existing, ident)
    done = {row["source_row_index"] for row in read_lines(out / "raw.jsonl")}
    selected = [r for r in records(args.split) if r.source_row_index not in done]
    if args.limit:
        selected = selected[: args.limit]
    model = load_model(args.checkpoint, args.adapter)
    compiled = schema.build(model, args.condition, args.structure_mode)
    print(f"{run}: {len(selected)} letters on {device()}", flush=True)
    with (out / "raw.jsonl").open("a") as stream, torch.inference_mode():
        for n, record in enumerate(selected, 1):
            start = time.perf_counter()
            kwargs = {
                "threshold": args.threshold,
                "include_confidence": True,
                "include_spans": True,
            }
            if args.context == "chunked":
                raw = model.extract_long(
                    record.note_text,
                    compiled,
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP,
                    **kwargs,
                )
            else:
                raw = model.extract(record.note_text, compiled, **kwargs)
            row = {
                "source_row_index": record.source_row_index,
                "latency_seconds": round(time.perf_counter() - start, 4),
                "raw": raw,
            }
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
            stream.flush()
            if n % 50 == 0:
                print(f"  {n}/{len(selected)}", flush=True)


def _deepseek() -> dict[str, dict[int, bool]]:
    """Saved DeepSeek one-call Purist correctness per letter, for descriptive pairing."""
    if not DEEPSEEK.exists():
        return {}
    from clinical_extraction.tasks.seizure_frequency.gan2026.one_call.parse import (
        native_categories,
    )

    output: dict[str, dict[int, bool]] = {}
    for row in json.loads(DEEPSEEK.read_text())["per_letter"]:
        correct = False
        if row["failure"] is None and row["label"]:
            try:
                correct = native_categories(row["label"])["purist"] == row["gold"]["purist"]
            except ValueError:
                correct = False
        output.setdefault(row["condition"], {})[row["source_row_index"]] = correct
    return output


def score(args: argparse.Namespace) -> None:
    run_dir = ROOT / args.run
    ident = json.loads((run_dir / "identity.json").read_text())
    raws = {row["source_row_index"]: row for row in read_lines(run_dir / "raw.jsonl")}
    letters = records(ident["split"])
    missing = [r.source_row_index for r in letters if r.source_row_index not in raws]
    if missing and not args.partial:
        raise SystemExit(f"{len(missing)} letters have no saved output; use --partial")
    letters = [r for r in letters if r.source_row_index in raws]
    reference = (
        {row["source_row_index"]: row["findings"] for row in read_lines(REFERENCE)}
        if ident["split"] == "dev750"
        else {}
    )
    per_letter: list[dict[str, Any]] = []
    finding_letters: list[dict[str, Any]] = []
    tallies: Counter[str] = Counter()
    for record in letters:
        raw = raws[record.source_row_index]["raw"]
        answer = project.answer(raw, record.note_text)
        expected = gold(record)
        row: dict[str, Any] = {
            "source_row_index": record.source_row_index,
            "gold": expected,
            "answer": answer,
            "long": len(record.note_text.split()) > LONG_WORDS,
            "latency_seconds": raws[record.source_row_index]["latency_seconds"],
        }
        for method in analysis.METHODS:
            predicted = (answer["categories"] or {}).get(method)
            row[f"{method}_category_correct"] = predicted == expected[method]
            row[f"{method}_correct"] = row[f"{method}_category_correct"] and not answer["failure"]
        if ident["condition"] == "expanded":
            projected, tally = project.findings(raw, record.note_text)
            tallies.update(tally)
            row["findings"] = projected
            row["claim_indices"] = project.claim_indices(
                answer["evidence_span"], projected, record.note_text
            )
            if record.source_row_index in reference:
                finding_letters.append(
                    {
                        "source_row_index": record.source_row_index,
                        "note": record.note_text,
                        "reference": reference[record.source_row_index],
                        "predicted": projected,
                    }
                )
        per_letter.append(row)

    def view(rows: list[dict[str, Any]]) -> dict[str, Any]:
        return (
            {
                f"{method}_{kind}": analysis.agreement([r[f"{method}_{kind}"] for r in rows])
                for method in analysis.METHODS
                for kind in ("correct", "category_correct")
            }
            if rows
            else {}
        )

    summary: dict[str, Any] = {
        "run": args.run,
        "identity": {k: v for k, v in ident.items() if k != "schema"},
        "letters": len(per_letter),
        "all": view(per_letter),
        "short_letters": view([r for r in per_letter if not r["long"]]),
        "long_letters": view([r for r in per_letter if r["long"]]),
        "failures": dict(
            Counter(r["answer"]["failure"] for r in per_letter if r["answer"]["failure"])
        ),
        "evidence_exact_rate": sum(r["answer"]["evidence_exact"] for r in per_letter)
        / len(per_letter),
        "evidence_hits_gan_reference": _reference_hits(per_letter, letters),
        "predicted_purist": dict(
            Counter((r["answer"]["categories"] or {}).get("purist") for r in per_letter)
        ),
        "gold_purist": dict(Counter(r["gold"]["purist"] for r in per_letter)),
        "majority_baseline_purist": max(Counter(r["gold"]["purist"] for r in per_letter).values())
        / len(per_letter),
        "median_latency_seconds": sorted(r["latency_seconds"] for r in per_letter)[
            len(per_letter) // 2
        ],
    }
    deepseek = _deepseek()
    if not missing and ident["split"] == "dev750":
        for condition, correct in deepseek.items():
            summary[f"paired_vs_deepseek_{condition}"] = analysis.paired(
                [r["purist_correct"] for r in per_letter],
                [correct[r["source_row_index"]] for r in per_letter],
            )
    if args.pair:
        other = {
            r["source_row_index"]: r["purist_correct"]
            for r in json.loads((ROOT / args.pair / "per_letter.json").read_text())
        }
        summary[f"paired_vs_{args.pair}"] = analysis.paired(
            [r["purist_correct"] for r in per_letter],
            [other[r["source_row_index"]] for r in per_letter],
        )
    if ident["condition"] == "expanded":
        summary["projection_tally"] = dict(tallies)
        if finding_letters:
            summary["findings"], _ = findings_score.score(finding_letters)
    write_json(run_dir / "per_letter.json", per_letter)
    write_json(RESULTS / ident["split"] / args.run / "score.json", summary)
    brief = {k: summary["all"][k]["correct"] for k in ("purist_correct", "purist_category_correct")}
    print(json.dumps({"run": args.run, "letters": len(per_letter), **brief}))
    if "findings" in summary:
        f = summary["findings"]
        print(json.dumps({k: f[k] for k in ("precision", "recall_core", "recall_all")}))


def _reference_hits(
    rows: list[dict[str, Any]], letters: list[GanFrequencyRecord]
) -> dict[str, Any]:
    """How often the evidence span overlaps a Gan reference quotation found in the note."""
    by_id = {r.source_row_index: r for r in letters}
    eligible = hits = 0
    for row in rows:
        record = by_id[row["source_row_index"]]
        quotes = training.reference_quotes(record)
        if not quotes:
            continue
        eligible += 1
        span = row["answer"]["evidence_span"]
        if span and any(
            start < span[1] and span[0] < end for start, end in training.quote_spans(record, quotes)
        ):
            hits += 1
    return {"eligible": eligible, "hits": hits, "rate": hits / eligible if eligible else None}


def build_data(args: argparse.Namespace) -> None:
    out = ROOT / "training_data"
    reference = {row["source_row_index"]: row["findings"] for row in read_lines(REFERENCE)}
    report: dict[str, Any] = {"schema_sha256": schema.schema_sha256("expanded")}
    for split in ("train300", "dev750"):
        for target in schema.CONDITIONS:
            if target == "expanded" and split != "dev750":
                continue
            rows, stats = training.examples(
                records(split), target, reference if target == "expanded" else None
            )
            path = out / f"{split}.{target}.jsonl"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
            report[f"{split}.{target}"] = {
                "rows": len(rows),
                **stats,
                "sha256": digest(path.read_bytes()),
            }
    folds = training.folds(records("dev750"), k=5, seed=training.FOLD_SEED)
    write_json(out / "dev750_folds.json", folds)
    report["dev750_folds"] = {
        "k": 5,
        "seed": training.FOLD_SEED,
        "sizes": [len(f) for f in folds["folds"]],
    }
    write_json(out / "report.json", report)
    print(json.dumps(report, indent=2))


def train(args: argparse.Namespace) -> None:
    out = ROOT / "checkpoints" / args.name
    config = training.config(
        output_dir=str(out),
        name=args.name,
        device=device(),
        use_lora=args.lora,
        epochs=args.epochs,
        max_len=args.max_len,
        seed=args.seed,
        max_steps=args.max_steps,
    )
    data = ROOT / "training_data"
    train_rows = read_lines(data / f"{args.train}.{args.target}.jsonl")
    eval_rows: list[dict[str, Any]] = []
    if args.fold is not None:
        folds = json.loads((data / "dev750_folds.json").read_text())["folds"]
        held = set(folds[args.fold])
        dev_rows = read_lines(data / f"dev750.{args.target}.jsonl")
        eval_rows = [r for r in dev_rows if r["source_row_index"] in held]
        train_rows = train_rows + [r for r in dev_rows if r["source_row_index"] not in held]
    random.Random(args.seed).shuffle(train_rows)
    if args.limit:
        train_rows, eval_rows = train_rows[: args.limit], eval_rows[: args.limit]
    write_json(
        out / "training_identity.json",
        {
            "base_model": MODEL,
            "target": args.target,
            "train": args.train,
            "fold": args.fold,
            "train_rows": len(train_rows),
            "eval_rows": len(eval_rows),
            "train_source_row_indices": sorted(r["source_row_index"] for r in train_rows),
            "schema_sha256": schema.schema_sha256(args.target),
            "config": config.__dict__,
            "packages": package_versions(),
            "device": device(),
        },
    )
    training.run(MODEL, config, train_rows, eval_rows)


def check(args: argparse.Namespace) -> None:
    """Environment check: device, precision, memory, and a one-letter timing."""
    import torch

    report: dict[str, Any] = {"packages": package_versions(), "device": device()}
    if report["device"] == "cuda":
        free, total = torch.cuda.mem_get_info()
        report["cuda"] = {
            "name": torch.cuda.get_device_name(0),
            "bf16": torch.cuda.is_bf16_supported(),
            "free_gb": round(free / 2**30, 2),
            "total_gb": round(total / 2**30, 2),
        }
    record = records("dev750")[0]
    model = load_model(MODEL, None)
    compiled = schema.build(model, "expanded")
    with torch.inference_mode():
        model.extract(record.note_text, compiled)
        start = time.perf_counter()
        model.extract(record.note_text, compiled, include_confidence=True, include_spans=True)
        report["expanded_one_letter_seconds"] = round(time.perf_counter() - start, 3)
    if report["device"] == "cuda":
        report["cuda"]["peak_allocated_gb"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
    print(json.dumps(report, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check")
    p.set_defaults(func=check)
    p = sub.add_parser("infer")
    p.add_argument("--condition", choices=schema.CONDITIONS, required=True)
    p.add_argument("--context", choices=("full", "chunked"), default="full")
    p.add_argument("--split", choices=tuple(SPLITS), default="dev750")
    p.add_argument("--checkpoint", default=MODEL)
    p.add_argument("--adapter")
    p.add_argument("--threshold", type=float, default=0.5)
    p.add_argument("--structure-mode", choices=("natural",))
    p.add_argument("--run")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=infer)
    p = sub.add_parser("score")
    p.add_argument("--run", required=True)
    p.add_argument("--pair", help="Another run over the same letters for a paired contrast")
    p.add_argument("--partial", action="store_true")
    p.set_defaults(func=score)
    p = sub.add_parser("build-data")
    p.set_defaults(func=build_data)
    p = sub.add_parser("train")
    p.add_argument("--target", choices=schema.CONDITIONS, required=True)
    p.add_argument("--train", choices=tuple(SPLITS), default="train300")
    p.add_argument("--fold", type=int, help="Hold out this dev750 fold; train on the rest")
    p.add_argument("--name", required=True)
    p.add_argument("--lora", action="store_true")
    p.add_argument("--epochs", type=int, default=10)
    p.add_argument("--max-len", type=int)
    p.add_argument("--seed", type=int, default=20260925)
    p.add_argument("--max-steps", type=int, default=-1, help="Smoke tests only")
    p.add_argument("--limit", type=int, help="Smoke tests only: first N shuffled rows")
    p.set_defaults(func=train)
    args = parser.parse_args()
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    # Apple Silicon shares system memory; fail with an error instead of exhausting it.
    os.environ.setdefault("PYTORCH_MPS_HIGH_WATERMARK_RATIO", "0.5")
    args.func(args)


if __name__ == "__main__":
    main()
