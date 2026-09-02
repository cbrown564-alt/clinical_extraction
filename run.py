"""Run Gan extraction without installing the package (HPC / pip-only deps).

Usage:

    python run.py --input notes.jsonl --output predictions.jsonl \\
        --base-url http://127.0.0.1:8000/v1 --model vllm/deepseek-v4-flash

    python run.py --probe --base-url http://127.0.0.1:8000/v1 \\
        --model vllm/deepseek-v4-flash

    python run.py --method llm_select --input notes.jsonl --output out.jsonl \\
        --base-url http://127.0.0.1:8000/v1 --model vllm/deepseek-v4-flash
"""

from __future__ import annotations

import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from clinical_extraction.operational.cli import main  # noqa: E402
from clinical_extraction.operational.script_argv import gan_script_argv  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main(gan_script_argv(sys.argv[1:])))
