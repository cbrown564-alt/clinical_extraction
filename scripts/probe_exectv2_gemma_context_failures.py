"""Rerun the two residual Gemma dev140 failures with detailed runtime telemetry."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

import dspy
import psutil

from clinical_extraction.core.local_structured_output import assess_structured_output
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines import (
    key_entities_structured as structured,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

ROW_IDS = ("EA0132", "EA0135")


def _get_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=5) as response:  # noqa: S310
        return json.load(response)


def _gpu_sample() -> dict[str, Any]:
    command = [
        "nvidia-smi",
        "--query-gpu=memory.used,utilization.gpu",
        "--format=csv,noheader,nounits",
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)  # noqa: S603
    memory_mib, utilization_pct = result.stdout.strip().split(", ")
    return {"vram_used_mib": int(memory_mib), "gpu_utilization_pct": int(utilization_pct)}


def _monitor(stop: threading.Event, samples: list[dict[str, Any]]) -> None:
    process = psutil.Process()
    while not stop.is_set():
        sample: dict[str, Any] = {
            "elapsed_seconds": time.monotonic(),
            "process_working_set_bytes": process.memory_info().rss,
            "system_available_bytes": psutil.virtual_memory().available,
        }
        try:
            sample.update(_gpu_sample())
            sample["ollama_ps"] = _get_json("http://localhost:11434/api/ps")
        except Exception as exc:  # telemetry must not abort the model call
            sample["telemetry_error"] = f"{type(exc).__name__}: {exc}"
        samples.append(sample)
        stop.wait(1)


def _history_summary(lm: dspy.LM) -> dict[str, Any]:
    history = list(getattr(lm, "history", ()))
    entries = []
    for item in history:
        response = item.get("response")
        entries.append(
            {
                "usage": item.get("usage") or getattr(response, "usage", None),
                "response_model": getattr(response, "model", None),
                "response_created": getattr(response, "created", None),
                "response_dump": response.model_dump(mode="json")
                if hasattr(response, "model_dump")
                else None,
            }
        )
    return {"entry_count": len(entries), "entries": entries}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--num-ctx", type=int, default=65536)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    os.environ["CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"] = str(args.num_ctx)

    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    results = []
    for row_id in ROW_IDS:
        lm = build_dspy_lm(
            "ollama_chat/gemma4:26b",
            temperature=0,
            max_tokens=args.max_tokens,
            cache=False,
            num_retries=0,
            timeout=1800,
        )
        dspy.configure(lm=lm)
        prompt_input = structured.build_prompt_input(letters[row_id], prompt_profile="full")
        samples: list[dict[str, Any]] = []
        stop = threading.Event()
        thread = threading.Thread(target=_monitor, args=(stop, samples), daemon=True)
        started = time.monotonic()
        thread.start()
        raw_output = ""
        call_error = None
        try:
            prediction = structured.DspyKeyEntitiesStructuredExtractor()(
                prompt_input_json=prompt_input
            )
            raw_output = str(prediction.extraction_json)
        except Exception as exc:
            call_error = f"{type(exc).__name__}: {exc}"
        finally:
            stop.set()
            thread.join(timeout=5)
        record, errors = (
            structured.parse_structured_events_json(raw_output)
            if raw_output
            else (None, ["not_run"])
        )
        assessment = assess_structured_output(raw_output, errors, call_error=call_error)
        normalized_samples = []
        for sample in samples:
            normalized_samples.append(
                {**sample, "elapsed_seconds": sample["elapsed_seconds"] - started}
            )
        results.append(
            {
                "letter_id": row_id,
                "num_ctx": args.num_ctx,
                "max_tokens": args.max_tokens,
                "prompt_input_chars": len(prompt_input),
                "raw_output_chars": len(raw_output),
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": errors,
                "failure_codes": list(assessment.failure_codes),
                "parsed_event_count": len(record.clinical_events) if record else 0,
                "wall_seconds": time.monotonic() - started,
                "lm_history": _history_summary(lm),
                "telemetry_samples": normalized_samples,
            }
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({"rows": results}, indent=2, default=str), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
