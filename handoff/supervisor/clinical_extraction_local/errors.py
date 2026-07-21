"""Stable, privacy-safe errors returned by the handoff."""

from __future__ import annotations


class HandoffError(Exception):
    code = "handoff_error"
    safe_summary = "The extraction could not be completed."


class ConfigurationError(HandoffError):
    code = "configuration_error"
    safe_summary = "Endpoint configuration is missing or conflicting."


class InputValidationError(HandoffError):
    code = "input_validation_error"
    safe_summary = "The input file does not match the required JSONL format."


class EndpointError(HandoffError):
    code = "endpoint_error"
    safe_summary = "The configured endpoint did not complete the request."


class SchemaValidationError(HandoffError):
    code = "schema_validation_failure"
    safe_summary = "The model response did not satisfy the workflow schema."


class ResumeMismatchError(HandoffError):
    code = "resume_mismatch"
    safe_summary = "The partial run does not match the current input or settings."


def safe_error(error: Exception) -> dict[str, str]:
    if isinstance(error, HandoffError):
        return {"code": error.code, "summary": error.safe_summary}
    return {
        "code": "unexpected_error",
        "summary": "The workflow failed. Use a private trace for local diagnosis.",
    }

