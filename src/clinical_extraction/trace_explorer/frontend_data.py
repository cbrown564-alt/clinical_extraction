"""Allowlisted data source for the restored Next.js research frontend."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

_NAMED_RESOURCES: dict[str, str] = {
    "registry": "registry.json",
    "pipeline_families": "pipeline-families.json",
    "rules": "rules.json",
    "prompts": "prompts.json",
    "exectv2_runs": "exectv2/runs.json",
    "exectv2_component_ablation": "exectv2/component-ablation.json",
    "exectv2_component_transitions": "exectv2/component-transitions.json",
    "exectv2_reliability_scorecard": "exectv2/reliability-scorecard.json",
    "exectv2_sf_inspection": "exectv2/sf-inspection.json",
    "gan2026_component_ablation": "gan2026/component-ablation.json",
    "gan2026_component_transitions": "gan2026/component-transitions.json",
    "gan2026_reliability_scorecard": "gan2026/reliability-scorecard.json",
    "gold_audit_gan_rows": "gold-audit/rows.json",
    "gold_audit_gan_decisions": "gold-audit/decisions.json",
    "gold_audit_exect_rows": "gold-audit/exectv2-rows.json",
    "gold_audit_exect_decisions": "gold-audit/exectv2-decisions.json",
    "qualified_review_packets": "qualified-review/packets.json",
    "qualified_review_decisions": "qualified-review/decisions.json",
    "gold_noise_ledgers": "gold-noise/ledgers.json",
    "gold_noise_gan_audit": "gold-noise/gan-audit.json",
    "gold_noise_issues": "gold-noise/issues.json",
    "gold_noise_hypotheses": "gold-noise/hypotheses.json",
    "gold_noise_row": "gold-noise/row.json",
}


class FrontendDataStore:
    """Read only the explicit JSON resources used by the established frontend."""

    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        if not self.root.is_dir():
            raise ValueError("frontend data root is unavailable")
        self._exectv2_payload = self._object(self.root / _NAMED_RESOURCES["exectv2_runs"])
        self._artifacts = {
            path.stem: path
            for path in (self.root / "artifacts").glob("*.json")
            if path.is_file()
        }
        self._permitted_exect_letter_ids = self._load_permitted_exect_letter_ids()
        validation_dir = self.root / "records" / "validation"
        self._validation_records = {
            int(path.stem): path
            for path in validation_dir.glob("*.json")
            if path.is_file() and path.stem.isdigit()
        }

    def named(self, resource: str) -> dict[str, Any]:
        if resource == "exectv2_runs":
            return copy.deepcopy(self._exectv2_payload)
        relative_path = _NAMED_RESOURCES.get(resource)
        if relative_path is None:
            raise KeyError(resource)
        value = self._read(self.root / relative_path)
        if not isinstance(value, dict):
            raise ValueError("frontend resource must contain a JSON object")
        return value

    def records(self, split: str) -> dict[str, Any] | None:
        if split != "validation":
            return None
        return self._object(self.root / "records" / "validation.json")

    def record(self, split: str, source_row_index: int) -> dict[str, Any] | None:
        if split != "validation":
            return None
        path = self._validation_records.get(source_row_index)
        return self._object(path) if path is not None else None

    def artifact(self, run_id: str, *, limit: int | None = None) -> dict[str, Any] | None:
        path = self._artifacts.get(run_id)
        if path is None:
            return None
        payload = self._object(path)
        content = payload.get("content")
        if limit is not None and isinstance(content, list):
            payload["content"] = content[:limit]
        return payload

    def exectv2_catalog(self) -> dict[str, Any]:
        """Return architecture summaries without eagerly sending row-level data."""

        payload = self._exectv2_payload
        runs = payload.get("runs")
        if not isinstance(runs, list):
            raise ValueError("ExECTv2 runs resource must contain a list")
        return {
            "generated_on": payload.get("generated_on"),
            "source_index": payload.get("source_index"),
            "runs": [
                {**run, "letters": []}
                for run in runs
                if isinstance(run, dict)
            ],
        }

    def exectv2_run(self, run_id: str) -> dict[str, Any] | None:
        """Return one selected architecture plus the shared dev140 letters."""

        payload = self._exectv2_payload
        runs = payload.get("runs")
        shared_letters = payload.get("shared_letters")
        if not isinstance(runs, list) or not isinstance(shared_letters, list):
            raise ValueError("ExECTv2 runs resource is malformed")
        for run in runs:
            if isinstance(run, dict) and run.get("run_id") == run_id:
                return {
                    "generated_on": payload.get("generated_on"),
                    "source_index": payload.get("source_index"),
                    "shared_letters": shared_letters,
                    "run": run,
                }
        return None

    def prompt_template(self, module_name: str) -> dict[str, Any] | None:
        prompts = self.named("prompts").get("prompts")
        if not isinstance(prompts, list):
            return None
        for prompt in prompts:
            if isinstance(prompt, dict) and prompt.get("module") == module_name:
                return copy.deepcopy(prompt)
        return None

    def qualified_review_packets(self) -> dict[str, Any]:
        payload = self.named("qualified_review_packets")
        packets = payload.get("packets")
        if not isinstance(packets, list):
            raise ValueError("qualified review packets must contain a list")
        permitted = [
            packet
            for packet in packets
            if isinstance(packet, dict)
            and str(packet.get("letter_id")) in self._permitted_exect_letter_ids
        ]
        payload["packets"] = permitted
        payload["total"] = len(permitted)
        payload["decided"] = sum(bool(packet.get("has_decision")) for packet in permitted)
        return payload

    def qualified_review_decisions(self) -> dict[str, Any]:
        payload = self.named("qualified_review_decisions")
        permitted_ids = self.qualified_review_ids()
        decisions = payload.get("decisions")
        if isinstance(decisions, list):
            payload["decisions"] = [
                decision
                for decision in decisions
                if isinstance(decision, dict)
                and str(decision.get("attribute_review_id")) in permitted_ids
            ]
        return payload

    def qualified_review_ids(self) -> set[str]:
        return {
            str(packet["attribute_review_id"])
            for packet in self.qualified_review_packets()["packets"]
        }

    def gold_audit_rows(self, dataset: str) -> dict[str, Any]:
        resource = "gold_audit_exect_rows" if dataset == "exectv2" else "gold_audit_gan_rows"
        payload = self.named(resource)
        rows = payload.get("rows")
        if dataset == "exectv2" and isinstance(rows, list):
            rows = [
                row
                for row in rows
                if isinstance(row, dict)
                and str(row.get("letter_id")) in self._permitted_exect_letter_ids
            ]
            payload["rows"] = rows
            payload["total"] = len(rows)
            payload["decided"] = sum(bool(row.get("has_decision")) for row in rows)
        return payload

    def gold_audit_decisions(self, dataset: str) -> dict[str, Any]:
        resource = (
            "gold_audit_exect_decisions" if dataset == "exectv2" else "gold_audit_gan_decisions"
        )
        payload = self.named(resource)
        permitted_ids = self.gold_audit_ids(dataset)
        decisions = payload.get("decisions")
        if isinstance(decisions, list):
            payload["decisions"] = [
                decision
                for decision in decisions
                if isinstance(decision, dict)
                and str(decision.get("audit_id") or decision.get("source_row_index"))
                in permitted_ids
            ]
        return payload

    def gold_audit_ids(self, dataset: str) -> set[str]:
        rows = self.gold_audit_rows(dataset).get("rows")
        if not isinstance(rows, list):
            return set()
        return {
            str(row.get("audit_id") or row.get("source_row_index"))
            for row in rows
            if isinstance(row, dict)
        }

    def _object(self, path: Path) -> dict[str, Any]:
        value = self._read(path)
        if not isinstance(value, dict):
            raise ValueError("frontend resource must contain a JSON object")
        return value

    def _read(self, path: Path) -> Any:
        resolved = path.resolve()
        if not resolved.is_relative_to(self.root) or not resolved.is_file():
            raise ValueError("frontend resource is outside the approved data root")
        return json.loads(resolved.read_text(encoding="utf-8"))

    def _load_permitted_exect_letter_ids(self) -> frozenset[str]:
        letter_ids: set[str] = set()
        for run_id, path in self._artifacts.items():
            if not run_id.startswith("exectv2_"):
                continue
            content = self._object(path).get("content")
            if not isinstance(content, list):
                continue
            for item in content:
                if (
                    isinstance(item, dict)
                    and item.get("split") == "dev"
                    and item.get("stage") == "dev140"
                    and item.get("letter_id")
                ):
                    letter_ids.add(str(item["letter_id"]))
        if not letter_ids:
            raise ValueError("no permitted ExECT dev140 letters were found")
        return frozenset(letter_ids)
