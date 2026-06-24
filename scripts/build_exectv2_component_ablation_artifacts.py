"""Build committed ExECTv2 component-ablation replay artifacts."""

from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    component_ablation_replay,
)


def main() -> None:
    paths = component_ablation_replay.write_component_ablation_artifacts(
        component_ablation_replay.DEFAULT_REPLAY_SPECS,
    )
    print(f"Wrote {paths['json']}")
    print(f"Wrote {paths['jsonl']}")
    print(f"Wrote {paths['markdown']}")
    print(f"Wrote configs under {paths['configs']}")


if __name__ == "__main__":
    main()
