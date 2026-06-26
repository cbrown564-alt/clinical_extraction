"""Prompt introspection helpers for Observatory routes."""

from __future__ import annotations

import importlib
import inspect
import json
from collections.abc import Iterable, Mapping
from typing import Any

from pydantic import BaseModel


def jsonable_mapping_sequence(items: Iterable[Any]) -> list[dict[str, Any]]:
    payload = []
    for item in items:
        if isinstance(item, Mapping):
            payload.append({str(key): value for key, value in item.items()})
    return payload


def prompt_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    taxonomy = getattr(module, "PROMPT_POLICY_TAXONOMY", [])
    return {
        "module": module_name,
        "prompt_version": prompt_version,
        "policy_taxonomy": jsonable_mapping_sequence(taxonomy),
        "policy_ids": [
            str(policy["policy_id"])
            for policy in taxonomy
            if isinstance(policy, Mapping) and "policy_id" in policy
        ],
    }


def prompt_template_payload(module_name: str) -> dict[str, Any]:
    module = importlib.import_module(module_name)
    prompt_version = getattr(module, "PROMPT_VERSION", module_name.rsplit(".", maxsplit=1)[-1])
    taxonomy = getattr(module, "PROMPT_POLICY_TAXONOMY", [])

    system_hint: str | None = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and hasattr(attr, "__mro__"):
            if any(hasattr(base, "fields") for base in attr.__mro__ if base is not object):
                doc = inspect.getdoc(attr)
                if doc and len(doc) > 20:
                    system_hint = doc
                    break

    user_hint: str | None = None
    build_fn = getattr(module, "build_prompt_input", None)
    if build_fn is not None:
        user_hint = inspect.getdoc(build_fn)

    output_schema_hint: str | None = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, BaseModel) and "Record" in attr_name:
            doc = inspect.getdoc(attr)
            if doc and len(doc) > 10:
                output_schema_hint = doc
                break

    build_sig: str | None = None
    if build_fn is not None:
        try:
            build_sig = str(inspect.signature(build_fn))
        except Exception:
            build_sig = None

    return {
        "module": module_name,
        "prompt_version": prompt_version,
        "system_hint": system_hint,
        "user_hint": user_hint,
        "output_schema_hint": output_schema_hint,
        "build_prompt_signature": build_sig,
        "policy_taxonomy": jsonable_mapping_sequence(taxonomy),
    }
