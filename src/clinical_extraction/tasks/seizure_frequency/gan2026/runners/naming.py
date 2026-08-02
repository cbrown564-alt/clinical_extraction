"""Active Gan method names and immutable historical aliases."""

from typing import Literal

ActivePipelineName = Literal["rules", "llm", "llm_with_rules"]

_ALIASES = {
    "rules": "rules",
    "rules_only": "rules",
    "deterministic_canonical_pipeline": "rules",
    "llm": "llm",
    "llm_only": "llm",
    "llm_only_canonical_pipeline": "llm",
    "llm_with_rules": "llm_with_rules",
    "hybrid_structured_events": "llm_with_rules",
}


def active_pipeline_name(value: str) -> ActivePipelineName:
    """Map an active name or documented legacy alias to its active name."""

    try:
        return _ALIASES[value]  # type: ignore[return-value]
    except KeyError as exc:
        raise ValueError(f"Unsupported Gan rules pipeline name: {value}") from exc
