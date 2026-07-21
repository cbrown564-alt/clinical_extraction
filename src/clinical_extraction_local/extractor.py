"""Documented Python API for the two separate workflows."""

from __future__ import annotations

from typing import Any

from .clinical_findings import ClinicalFindingsPipeline
from .errors import safe_error
from .models import GenerationSettings, ModelClient, WorkflowOutput
from .seizure_frequency import SeizureFrequencyPipeline


class ClinicalExtractor:
    def __init__(
        self, model: ModelClient, settings: GenerationSettings | None = None
    ) -> None:
        self.model = model
        self.settings = settings or GenerationSettings()
        self._frequency = SeizureFrequencyPipeline(model, self.settings)
        self._findings = ClinicalFindingsPipeline(model, self.settings)

    def seizure_frequency(self, *, note_id: str, text: str) -> dict[str, Any]:
        return self._frequency.run(note_id=note_id, text=text).result

    def clinical_findings(self, *, note_id: str, text: str) -> dict[str, Any]:
        return self._findings.run(note_id=note_id, text=text).result

    def run_workflow(self, workflow: str, *, note_id: str, text: str) -> WorkflowOutput:
        if workflow == "seizure_frequency":
            return self._frequency.run(note_id=note_id, text=text)
        if workflow == "clinical_findings":
            return self._findings.run(note_id=note_id, text=text)
        raise ValueError(f"unknown workflow: {workflow}")

    def all(self, *, note_id: str, text: str) -> dict[str, Any]:
        workflows: dict[str, Any] = {}
        traces: dict[str, Any] = {}
        for workflow in ("seizure_frequency", "clinical_findings"):
            try:
                output = self.run_workflow(workflow, note_id=note_id, text=text)
            except Exception as exc:
                workflows[workflow] = {"status": "error", "error": safe_error(exc)}
            else:
                workflows[workflow] = {"status": "ok", "result": output.result}
                traces[workflow] = output.trace
        statuses = [value["status"] for value in workflows.values()]
        if statuses == ["ok", "ok"]:
            status = "ok"
        elif statuses == ["error", "error"]:
            status = "error"
        else:
            status = "partial"
        return {"status": status, "workflows": workflows, "traces": traces}
