#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if [ ! -x "$ROOT/.venv/bin/python" ]; then
  python3.11 -m venv "$ROOT/.venv"
fi
"$ROOT/.venv/bin/python" -m pip install --requirement "$ROOT/requirements.lock"
printf '%s\n' "Setup complete. Copy .env.example to .env, edit it, then run:"
printf '%s\n' "./.venv/bin/python run.py check"

