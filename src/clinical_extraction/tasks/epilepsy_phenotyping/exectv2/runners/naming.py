"""Active ExECT method names and immutable legacy aliases."""

from typing import Literal

ActiveMethodName = Literal["rules", "llm", "llm_with_rules"]

RULES_METHOD_ALIASES: tuple[str, ...] = ("rules", "rules_only", "exectv2_rules_only")
LLM_METHOD_ALIASES: tuple[str, ...] = ("llm", "llm_only", "exectv2_llm_only")
LLM_WITH_RULES_METHOD_ALIASES: tuple[str, ...] = (
    "llm_with_rules",
    "exectv2_llm_with_rules",
)
UNOWNED_RULES_ALIASES = frozenset(("deterministic_all9", "exectv2_deterministic_all9"))

_ALIASES: dict[str, ActiveMethodName] = {
    alias: "rules" for alias in RULES_METHOD_ALIASES
}
_ALIASES.update(
    {
    **{alias: "llm" for alias in LLM_METHOD_ALIASES},
    **{alias: "llm_with_rules" for alias in LLM_WITH_RULES_METHOD_ALIASES},
    }
)

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
