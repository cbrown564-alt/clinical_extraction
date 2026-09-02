"""Turn flat ``python run.py --flags`` argv into the operational CLI."""

from __future__ import annotations

from collections.abc import Sequence

_COMMANDS = frozenset({"gan", "exect", "probe"})


def gan_script_argv(argv: Sequence[str]) -> list[str]:
    args = list(argv)
    if args and args[0] in _COMMANDS:
        return args
    if "--probe" in args:
        return ["probe", *[item for item in args if item != "--probe"]]
    return ["gan", *args]
