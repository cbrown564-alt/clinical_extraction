"""On/off flags for the 2026-08-20 post-stack hop-audit repairs.

Defaults keep the new behaviors on so existing tests stay pinned. A
diagnostic no-call reparse can turn each flag off to measure isolated
dev750 impact against the pre-repair stack.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PostStackFixFlags:
    no_reference_daily: bool = True
    month_x_typical_preserve: bool = False
    diary_sum_all_months: bool = True
    vague_seizure_free_diary: bool = True
    date_list_span: bool = True


_FLAGS: ContextVar[PostStackFixFlags | None] = ContextVar(
    "gan2026_post_stack_fix_flags",
    default=None,
)


def post_stack_fix_flags() -> PostStackFixFlags:
    return _FLAGS.get() or PostStackFixFlags()


@contextmanager
def using_post_stack_fix_flags(**overrides: bool) -> Iterator[PostStackFixFlags]:
    flags = replace(post_stack_fix_flags(), **overrides)
    token = _FLAGS.set(flags)
    try:
        yield flags
    finally:
        _FLAGS.reset(token)
