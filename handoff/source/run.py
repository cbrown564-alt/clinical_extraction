"""Load optional local settings and run the clinical extraction CLI."""

from __future__ import annotations

import os
from pathlib import Path

# The selected internal prompt builders import DSPy/LiteLLM, but this handoff
# uses its own direct OpenAI-compatible client and must not fetch cost metadata.
os.environ.setdefault("LITELLM_LOCAL_MODEL_COST_MAP", "true")


def _load_dotenv() -> None:
    path = Path(__file__).resolve().with_name(".env")
    if not path.is_file():
        return
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not key.strip():
            raise SystemExit(f".env line {number}: expected KEY=value")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


_load_dotenv()

from clinical_extraction_local.cli import main  # noqa: E402

raise SystemExit(main())
