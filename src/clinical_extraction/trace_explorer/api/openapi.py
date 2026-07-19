from __future__ import annotations

import json

from clinical_extraction.trace_explorer.api.app import create_app


def main() -> int:
    print(json.dumps(create_app().openapi(), ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
