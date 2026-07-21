"""OpenAI-compatible endpoint adapter with no content logging or cache."""

from __future__ import annotations

from typing import Any

from .config import EndpointConfig
from .errors import EndpointError
from .models import GenerationSettings, ModelResponse


class VLLMClient:
    def __init__(self, config: EndpointConfig) -> None:
        from openai import OpenAI

        self.config = config
        self._client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.settings.timeout_seconds,
            max_retries=config.settings.retry_count,
        )

    @classmethod
    def from_env(cls) -> VLLMClient:
        return cls(EndpointConfig.from_env())

    def complete_json(
        self,
        *,
        messages: list[dict[str, str]],
        schema: dict[str, object],
        settings: GenerationSettings,
    ) -> ModelResponse:
        modes = ("json_schema", "json_object")
        last_error: Exception | None = None
        for attempt, mode in enumerate(modes, 1):
            response_format: dict[str, Any]
            if mode == "json_schema":
                response_format = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "clinical_extraction",
                        "strict": True,
                        "schema": schema,
                    },
                }
            else:
                response_format = {"type": "json_object"}
            request: dict[str, Any] = {
                "model": self.config.model,
                "messages": messages,
                "temperature": settings.temperature,
                "max_tokens": settings.max_completion_tokens,
                "response_format": response_format,
                "extra_body": {
                    "chat_template_kwargs": {"enable_thinking": settings.thinking}
                },
            }
            if settings.seed is not None:
                request["seed"] = settings.seed
            if settings.reasoning_effort:
                request["reasoning_effort"] = settings.reasoning_effort
            try:
                response = self._client.chat.completions.create(**request)
            except Exception as exc:  # provider exceptions can contain request details
                last_error = exc
                if mode == "json_schema" and exc.__class__.__name__ == "BadRequestError":
                    continue
                raise EndpointError() from exc
            if not response.choices:
                raise EndpointError("the endpoint returned no choices")
            choice = response.choices[0]
            message = choice.message
            content = message.content or ""
            extras = getattr(message, "model_extra", None) or {}
            if not content.strip():
                raise EndpointError("the endpoint returned no final content")
            usage = getattr(response, "usage", None)
            usage_dict = {
                key: int(value)
                for key in ("prompt_tokens", "completion_tokens", "total_tokens")
                if (value := getattr(usage, key, None)) is not None
            }
            return ModelResponse(
                content=content,
                requested_model=self.config.model,
                response_model=getattr(response, "model", None),
                reasoning_content_present=bool(extras.get("reasoning_content")),
                finish_reason=getattr(choice, "finish_reason", None),
                structured_output_mode=mode,
                request_attempts=attempt,
                usage=usage_dict,
            )
        raise EndpointError() from last_error

