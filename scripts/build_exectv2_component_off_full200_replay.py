"""Build the frozen ExECTv2 full-200 component-off aggregate replay."""

from __future__ import annotations

import subprocess
from datetime import date

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    component_ablation_replay,
)


def main() -> None:
    paths = component_ablation_replay.write_full200_component_off_readout_artifacts(
        generated_on=date.today().isoformat(),
        code_hash=_git_output("rev-parse", "--short", "HEAD"),
        worktree_state=_worktree_state(),
    )
    print(f"Wrote {paths['component_off_json']}")
    print(f"Wrote {paths['component_off_jsonl']}")
    print(f"Wrote {paths['component_off_markdown']}")


def _git_output(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _worktree_state() -> str:
    status = _git_output("status", "--short")
    return "clean" if not status else "dirty: " + status.replace("\n", "; ")


if __name__ == "__main__":
    main()
