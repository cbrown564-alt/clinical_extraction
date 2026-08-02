"""Active ExECT method names and immutable legacy aliases."""

from typing import Literal

ActiveMethodName = Literal["rules", "llm", "llm_with_rules"]

_ALIASES: dict[str, ActiveMethodName] = {
    "rules": "rules",
    "rules_only": "rules",
    "exectv2_rules_only": "rules",
    "deterministic_all9": "rules",
    "exectv2_deterministic_all9": "rules",
    "llm": "llm",
    "llm_only": "llm",
    "exectv2_llm_only": "llm",
    "llm_with_rules": "llm_with_rules",
    "exectv2_llm_with_rules": "llm_with_rules",
}

_RETAINED_METHOD_IDS = {
    "rules": "exectv2_rules_only",
    "llm": "exectv2_llm_only",
    "llm_with_rules": "exectv2_llm_with_rules",
}


def active_method_name(value: str) -> ActiveMethodName:
    """Resolve an active ExECT name or an explicit legacy alias."""

    try:
        return _ALIASES[value]
    except KeyError as exc:
        raise ValueError(f"Unsupported ExECT method name: {value}") from exc


def retained_method_id(value: str) -> str:
    """Return the retained manifest identity for an active method."""

    return _RETAINED_METHOD_IDS[active_method_name(value)]
