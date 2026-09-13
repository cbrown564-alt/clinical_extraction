"""Supported one-call task profiles using the shared persistent artifact lifecycle."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clinical_extraction.core.artifact_store import ArtifactStore
from clinical_extraction.core.artifacts import (
    ExtractionArtifact,
    PreparedExtractionRequest,
    SourceDocument,
)
from clinical_extraction.operational.io import InputNote
from clinical_extraction.operational.runtime import RuntimeConfig


@dataclass(frozen=True)
class ExtractionTask:
    name: str
    program_version: str
    prepare: Callable[[SourceDocument], PreparedExtractionRequest]
    execute: Callable[..., ExtractionArtifact[Any]]
    program_factory: Callable[[], Any]
    response_field: str


def task_profile(name: str) -> ExtractionTask:
    if name == 'gan':
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm.extraction import (
            execute_gan_request,
            prepare_gan_request,
        )
        from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
            DspyStructuredExtractor,
        )
        return ExtractionTask(name, 'gan-artifact-v1', prepare_gan_request,
                              execute_gan_request, DspyStructuredExtractor, 'structured_json')
    if name == 'exect':
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.extraction import (
            execute_exect_request,
            prepare_exect_request,
        )
        from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.signatures import (  # noqa: E501
            DspyKeyEntitiesStructuredExtractor,
        )
        return ExtractionTask(name, 'exect-artifact-v1', prepare_exect_request,
                              execute_exect_request, DspyKeyEntitiesStructuredExtractor,
                              'extraction_json')
    raise ValueError(f'unsupported extraction task: {name}')


def run_artifact_notes(
    notes: Sequence[InputNote], runtime: RuntimeConfig, *, task: str,
    completion: Callable[[PreparedExtractionRequest], str] | None = None,
    store_path: Path | None = None, replay_only: bool = False, retry_failed: bool = False,
) -> list[dict[str, Any]]:
    """Preserve input order/failures; exact saved requests never construct a provider."""
    profile = task_profile(task)
    execution = runtime.execution_configuration()
    program: Any = None

    def complete(request: PreparedExtractionRequest) -> str:
        nonlocal program
        if completion is not None:
            return completion(request)
        if program is None:
            import dspy

            from clinical_extraction.core.dspy_runtime import build_dspy_lm
            dspy.configure(lm=build_dspy_lm(
                runtime.model, temperature=runtime.temperature, max_tokens=runtime.max_tokens,
                cache=False, api_base=runtime.base_url, api_key=runtime.api_key,
                timeout=int(runtime.timeout_seconds),
            ))
            program = profile.program_factory()
        prediction = program(prompt_input_json=request.prompt_input_json)
        return str(getattr(prediction, profile.response_field))

    rows: list[dict[str, Any]] = []
    store = ArtifactStore(store_path) if store_path is not None else None
    try:
        for note in notes:
            source = SourceDocument.from_text(source_id=note.note_id, text=note.text)
            request = profile.prepare(source)

            def capture() -> ExtractionArtifact[Any]:
                return profile.execute(request, source=source, completion=complete,
                                       provider_metadata={'runtime': execution.to_dict()})

            try:
                if store is not None:
                    artifact = store.execute(request, execution,
                        program_version=profile.program_version, capture=capture,
                        replay_only=replay_only, retry_failed=retry_failed)
                elif replay_only:
                    raise ValueError('replay requires an artifact store')
                else:
                    artifact = capture()
            except ValueError as exc:
                rows.append({'id': note.note_id, 'task': task, 'status': 'error',
                             'error': str(exc), 'request_id': request.request_id})
                continue
            rows.append({'id': note.note_id, 'task': task,
                         'status': 'ok' if artifact.status == 'ready' else 'error',
                         'model': runtime.api_model, 'pipeline': f'{task}_llm_extract_artifact_v1',
                         'artifact': artifact.to_dict()})
    finally:
        if store is not None:
            store.connection.close()
    return rows
