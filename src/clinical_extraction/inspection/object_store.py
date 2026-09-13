from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


class ObjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, value: Any) -> str:
        payload = canonical_json_bytes(value)
        digest = hashlib.sha256(payload).hexdigest()
        target = self.root / f"{digest}.json"
        if not target.exists():
            temporary = self.root / f".{digest}.{os.getpid()}.tmp"
            temporary.write_bytes(payload)
            os.replace(temporary, target)
        return digest

    def get(self, digest: str) -> dict[str, Any]:
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("invalid object digest")
        return json.loads((self.root / f"{digest}.json").read_text(encoding="utf-8"))
