"""Allowlisted data source for the restored Next.js research frontend."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
    LLM_METHOD_ALIASES,
    LLM_WITH_RULES_METHOD_ALIASES,
    RULES_METHOD_ALIASES,
    UNOWNED_RULES_ALIASES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
)
from clinical_extraction.trace_explorer.gan2026_comparison import (
    GanValidationDiscovery,
    discover_gan2026_validation_runs,
)

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
        self._repo_root = self._resolve_repo_root(self.root)
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
        self._validation_dataset_records = {
            int(record.source_row_index): record
            for record in load_records_for_split("validation")
        }
        self._gan_fingerprint: tuple[tuple[str, int, int], ...] = ()
        self._gan_validation = self._discover_gan_validation()

    @staticmethod
    def _resolve_repo_root(frontend_data_root: Path) -> Path:
        """Locate the repository root above the frontend mock-data directory."""

        for candidate in (frontend_data_root, *frontend_data_root.parents):
            if (candidate / "pyproject.toml").is_file() and (candidate / "src").is_dir():
                return candidate
        raise ValueError("repository root is unavailable from frontend data root")

    def named(self, resource: str) -> dict[str, Any]:
        if resource in {"pipeline_families", "registry"}:
            self._refresh_gan_validation()
        if resource == "exectv2_runs":
            return copy.deepcopy(self._exectv2_payload)
        if resource == "pipeline_families" and self._gan_validation is not None:
            return copy.deepcopy(self._gan_validation.catalog)
        relative_path = _NAMED_RESOURCES.get(resource)
        if relative_path is None:
            raise KeyError(resource)
        value = self._read(self.root / relative_path)
        if not isinstance(value, dict):
            raise ValueError("frontend resource must contain a JSON object")
        if resource == "registry" and self._gan_validation is not None:
            runs = value.get("runs")
            if not isinstance(runs, list):
                raise ValueError("frontend registry must contain a run list")
            dynamic_ids = {
                str(item["run_id"]) for item in self._gan_validation.registry_entries
            }
            value["runs"] = [
                item
                for item in runs
                if isinstance(item, dict) and str(item.get("run_id")) not in dynamic_ids
            ] + [copy.deepcopy(item) for item in self._gan_validation.registry_entries]
        return value

    def records(self, split: str) -> dict[str, Any] | None:
        if split != "validation":
            return None
        return self._object(self.root / "records" / "validation.json")

    def record(self, split: str, source_row_index: int) -> dict[str, Any] | None:
        if split != "validation":
            return None
        path = self._validation_records.get(source_row_index)
        if path is not None:
            return self._object(path)
        record = self._validation_dataset_records.get(source_row_index)
        if record is None:
            return None
        return {
            "split": "validation",
            "source_row_index": record.source_row_index,
            "gold_label": record.gold_label,
            "gold_reference": record.gold_reference,
            "row_ok": record.row_ok,
            "note_text": record.note_text,
            "labels_match_all_categories": record.labels_match_all_categories,
            "quotes_ok_all_categories": record.quotes_ok_all_categories,
        }

    def artifact(self, run_id: str, *, limit: int | None = None) -> dict[str, Any] | None:
        self._refresh_gan_validation()
        if self._gan_validation is not None:
            replay_path = self._gan_validation.replay_artifacts.get(run_id)
            if replay_path is not None:
                return {
                    "run_id": run_id,
                    "artifact_path": replay_path.relative_to(self._repo_root).as_posix(),
                    "artifact_type": "jsonl",
                    "content": self._read_jsonl(replay_path, limit=limit),
                }
        path = self._artifacts.get(run_id)
        if path is None:
            return None
        payload = self._object(path)
        content = payload.get("content")
        if limit is not None and isinstance(content, list):
            payload["content"] = content[:limit]
        return payload

    def _discover_gan_validation(self) -> GanValidationDiscovery | None:
        repo_root = self._repo_root
        config_path = (
            repo_root / "configs" / "gan2026" / "six_model_validation_comparison_20260718.json"
        )
        if not config_path.is_file():
            return None
        expected_indices = {
            int(record.source_row_index) for record in load_records_for_split("validation")
        }
        discovery = discover_gan2026_validation_runs(
            config_path,
            expected_indices=expected_indices,
        )
        self._gan_fingerprint = self._gan_source_fingerprint(config_path)
        return discovery

    def _refresh_gan_validation(self) -> None:
        repo_root = self._repo_root
        config_path = (
            repo_root / "configs" / "gan2026" / "six_model_validation_comparison_20260718.json"
        )
        changed = (
            config_path.is_file()
            and self._gan_source_fingerprint(config_path) != self._gan_fingerprint
        )
        if changed:
            self._gan_validation = self._discover_gan_validation()

    @staticmethod
    def _gan_source_fingerprint(config_path: Path) -> tuple[tuple[str, int, int], ...]:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        repo_root = config_path.parent.parent.parent
        artifact_root = repo_root / str(config["artifact_root"])
        paths = [config_path, *artifact_root.glob("*/*/validation750.rows.jsonl")]
        return tuple(
            sorted(
                (str(path.resolve()), path.stat().st_size, path.stat().st_mtime_ns)
                for path in paths
                if path.is_file()
            )
        )

    @staticmethod
    def _read_jsonl(path: Path, *, limit: int | None) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"expected object at {path}:{line_number}")
                rows.append(value)
                if limit is not None and len(rows) >= limit:
                    break
        return rows

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
                {**self._canonical_exect_run(run), "letters": []}
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
        canonical_runs = [
            self._canonical_exect_run(run) for run in runs if isinstance(run, dict)
        ]
        matches = [run for run in canonical_runs if self._exect_run_matches(run, run_id)]
        if len(matches) == 1:
            return {
                "generated_on": payload.get("generated_on"),
                "source_index": payload.get("source_index"),
                "shared_letters": shared_letters,
                "run": matches[0],
            }
        return None

    @staticmethod
    def _canonical_exect_run(run: dict[str, Any]) -> dict[str, Any]:
        """Expose the active rules name while retaining saved-run lookup."""

        if run.get("run_id") not in {
            *RULES_METHOD_ALIASES,
            "exectv2_deterministic_all9_dev140",
        }:
            return run
        canonical = {**run, "run_id": "rules"}
        saved_run_id = str(
            canonical.setdefault("saved_run_id", "exectv2_deterministic_all9_dev140")
        )
        retained_evidence_id = str(
            canonical.setdefault(
                "retained_evidence_id", "exectv2_deterministic_all9_dev_20260714"
            )
        )
        prior_aliases = canonical.get("legacy_run_ids", [])
        approved_prior_aliases = [
            alias
            for alias in (prior_aliases if isinstance(prior_aliases, list) else [])
            if alias in {*RULES_METHOD_ALIASES[1:], saved_run_id, retained_evidence_id}
        ]
        aliases = [
            *approved_prior_aliases,
            *RULES_METHOD_ALIASES[1:],
            saved_run_id,
            retained_evidence_id,
        ]
        canonical["legacy_run_ids"] = list(dict.fromkeys(alias for alias in aliases if alias))
        canonical["architecture_family"] = "rules"
        canonical["pipeline_family"] = "rules"
        return canonical

    @staticmethod
    def _exect_run_matches(run: dict[str, Any], requested: str) -> bool:
        if requested in UNOWNED_RULES_ALIASES:
            return False
        active_aliases = {
            **{alias: "llm" for alias in LLM_METHOD_ALIASES},
            **{alias: "llm_with_rules" for alias in LLM_WITH_RULES_METHOD_ALIASES},
            **{alias: "rules" for alias in RULES_METHOD_ALIASES},
        }
        requested_active = active_aliases.get(requested)
        if requested_active is not None and requested_active in {
            run.get("active_method"),
            run.get("method_id"),
        }:
            return True
        aliases = {
            value
            for value in (
                run.get("run_id"),
                run.get("saved_run_id"),
                run.get("retained_evidence_id"),
                run.get("active_method"),
                run.get("method_id"),
            )
            if isinstance(value, str)
        }
        legacy_run_ids = run.get("legacy_run_ids", [])
        if isinstance(legacy_run_ids, list):
            aliases.update(item for item in legacy_run_ids if isinstance(item, str))
        return requested in aliases

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

    def semantic_support_review_packets(self) -> dict[str, Any]:
        """Return the frozen dev140 review sample with governed full-letter context."""

        repo_root = self._repo_root
        substrate_path = (
            repo_root
            / "experiments"
            / "exectv2_semantic_support_review_substrate_dev140_20260718.json"
        ).resolve()
        if not substrate_path.is_relative_to(repo_root) or not substrate_path.is_file():
            raise ValueError("semantic-support review substrate is unavailable")
        substrate = json.loads(substrate_path.read_text(encoding="utf-8"))
        if not isinstance(substrate, dict):
            raise ValueError("semantic-support review substrate must be an object")
        review_items = substrate.get("review_items")
        shared_letters = self._exectv2_payload.get("shared_letters")
        if not isinstance(review_items, list) or not isinstance(shared_letters, list):
            raise ValueError("semantic-support review source is malformed")

        letter_text_by_id = {
            str(letter["letter_id"]): str(letter["letter_text"])
            for letter in shared_letters
            if isinstance(letter, dict)
            and str(letter.get("letter_id")) in self._permitted_exect_letter_ids
            and isinstance(letter.get("letter_text"), str)
        }
        packets: list[dict[str, Any]] = []
        review_fields = {
            "semantic_support",
            "evidence_decisive",
            "current_fact_warranted",
            "unsupported_inference",
            "reviewer_id",
            "reviewed_at",
            "review_notes",
        }
        for review_item in review_items:
            if not isinstance(review_item, dict):
                continue
            letter_id = str(review_item.get("letter_id"))
            full_letter_text = letter_text_by_id.get(letter_id)
            if full_letter_text is None:
                continue
            packet = {
                key: copy.deepcopy(value)
                for key, value in review_item.items()
                if key not in review_fields
            }
            packet["full_letter_text"] = full_letter_text
            packet["queue_position"] = len(packets) + 1
            packets.append(packet)

        if len(packets) != 48:
            raise ValueError("semantic-support review queue must contain 48 dev140 items")
        return {
            "claim_boundary": substrate.get("claim_boundary"),
            "dataset": substrate.get("dataset"),
            "families": copy.deepcopy(substrate.get("families")),
            "models": copy.deepcopy(substrate.get("models")),
            "packets": packets,
        }

    def semantic_support_review_ids(self) -> set[str]:
        return {
            str(packet["review_item_id"])
            for packet in self.semantic_support_review_packets()["packets"]
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
