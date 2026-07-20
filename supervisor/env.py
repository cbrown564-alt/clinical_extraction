from __future__ import annotations

import os
import re
from pathlib import Path


_ENV_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def load_dotenv(path: str | Path | None = None, *, override: bool = False) -> None:
    """Load simple KEY=value pairs from a .env file into os.environ."""
    env_path = Path(path) if path is not None else Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].lstrip()

        key, separator, value = line.partition("=")
        key = key.strip()
        if not separator or not _ENV_NAME.fullmatch(key):
            continue
        if not override and key in os.environ:
            continue

        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"\"", "'"}:
            value = value[1:-1]
        os.environ[key] = value
