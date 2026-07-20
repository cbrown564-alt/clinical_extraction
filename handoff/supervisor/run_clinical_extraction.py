"""Run the bundled clinical extraction source tree."""

from __future__ import annotations

import os
from pathlib import Path


def _load_local_env() -> None:
    path = Path(__file__).with_name(".env")
    if not path.is_file():
        return
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not key:
            raise SystemExit(f"{path}:{line_number}: expected KEY=value")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key, value)


if __name__ == "__main__":
    _load_local_env()
    from clinical_extraction.operational.cli import main

    raise SystemExit(main())
