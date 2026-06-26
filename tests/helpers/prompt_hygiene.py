"""Shared prompt-hygiene constants and leak-check helpers for LLM-facing strings."""

from __future__ import annotations

FORBIDDEN_PHRASES = (
    "Decision 000",
    "decision 000",
    "deterministic code",
    "downstream deterministic",
    "architecture gate",
    "deterministic candidates",
    "gold labels",
    "gold_label",
    "parser-ready",
    "scorer-facing",
    "scoring-facing",
    "benchmark",
    "synthetic",
    "prompt_policy_taxonomy",
    " -> ",
)


def find_leaked_phrases(text: str) -> list[str]:
    """Return forbidden internal phrases present in *text*."""
    return [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]


def collect_signature_text(sig_class) -> str:
    """Collect the docstring and all field desc strings from a DSPy Signature."""
    parts = [sig_class.__doc__ or ""]
    for field_name in sig_class.model_fields:
        field = sig_class.model_fields[field_name]
        extra = field.json_schema_extra or {}
        parts.append(extra.get("desc", ""))
    return " ".join(parts)
