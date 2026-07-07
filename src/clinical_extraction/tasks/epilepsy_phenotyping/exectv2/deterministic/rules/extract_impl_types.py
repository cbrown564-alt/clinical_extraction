"""Shared types for Stack A extract rule implementations."""

from __future__ import annotations

from dataclasses import dataclass
from re import Pattern

from ..rule_metadata import ExclusionPredicate, RuleBuilder


@dataclass(frozen=True)
class ExtractRuleImpl:
    pattern: Pattern[str]
    build: RuleBuilder
    exclude: tuple[ExclusionPredicate, ...] = ()
