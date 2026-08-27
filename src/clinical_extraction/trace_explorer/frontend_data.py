"""Allowlisted data source for the Next.js research frontend."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Literal

from clinical_extraction.paper.exect import hydrate_saved_exect_letter
from clinical_extraction.paper.exect_cell_replay import hydrate_exect_five_cell_letter
from clinical_extraction.paper.exect_panel import (
    paper_exect_catalog_runs,
    paper_exect_identity,
)
from clinical_extraction.paper.gan import hydrate_saved_raw_row
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    DEFAULT_SPLIT_MANIFEST as EXECT_SPLIT_MANIFEST,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.runners.naming import (
    LLM_METHOD_ALIASES,
    LLM_WITH_RULES_METHOD_ALIASES,
    RULES_METHOD_ALIASES,
    UNOWNED_RULES_ALIASES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_SPLIT_MANIFEST_PATH as GAN_SPLIT_MANIFEST,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records_for_split,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
)
from clinical_extraction.trace_explorer.gan2026_comparison import (
    GanValidationDiscovery,
    discover_gan2026_validation_runs,
    paper_identity_from_run_id,
)

DatasetId = Literal["gan2026", "exectv2"]

_FIVE_CELL_REPAIR = {
    "gan_llm_extract": "llm_select",
    "gan_llm_encode": "llm_encode",
    "gan_llm_select_from_extract": "llm_select",
}

_NAMED_RESOURCES: dict[str, str] = {
    "registry": "registry.json",
    "pipeline_families": "pipeline-families.json",
    "exectv2_runs": "exectv2/runs.json",
    "gold_audit_gan_decisions": "gold-audit/decisions.json",
    "gold_audit_exect_decisions": "gold-audit/exectv2-decisions.json",
}

_DATASET_SPLITS: dict[str, str] = {
    "gan2026": "dev750",
    "exectv2": "dev140",
}

_SPLIT_TO_DATASET: dict[str, DatasetId] = {
    "dev750": "gan2026",
    "validation": "gan2026",
    "validation750": "gan2026",
    "dev140": "exectv2",
    "dev": "exectv2",
}

# Official manifests own the browsable letter set. Payload split labels are not trusted.
_LOCKED_SPLIT_KEYS = frozenset(
    {
        "test",
        "test60",
        "test450",
        "holdout",
        "full",
        "full200",
        "lockedtest",
    }
)


class FrontendDataStore:
    """Read only the explicit resources used by the live frontend surfaces."""

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
        self._gan_dev_ids, self._gan_holdout_ids = _gan_split_ids(self._repo_root)
        self._exect_dev_ids, self._exect_holdout_ids = _exect_split_ids(self._repo_root)
        self._paper_exect_run_cache: dict[str, dict[str, Any]] = {}
        self._exect_gold_by_id: dict[str, Any] | None = None

    @staticmethod
    def _resolve_repo_root(frontend_data_root: Path) -> Path:
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

    def letters(self, dataset: str) -> dict[str, Any]:
        dataset_id = self._require_dataset(dataset)
        if dataset_id == "gan2026":
            letters = [self._gan_letter_summary(record) for record in self._gan_records()]
        else:
            letters = [
                self._exect_letter_summary(letter) for letter in self._exect_shared_letters()
            ]
        return {
            "dataset": dataset_id,
            "split": _DATASET_SPLITS[dataset_id],
            "count": len(letters),
            "letters": letters,
        }

    def is_locked_letter(self, dataset: str, letter_id: str) -> bool:
        dataset_id = self._require_dataset(dataset)
        if dataset_id == "exectv2":
            return str(letter_id) in self._exect_holdout_ids
        return str(letter_id) in self._gan_holdout_ids

    def is_locked_letter_id(self, letter_id: str) -> bool:
        return str(letter_id) in self._exect_holdout_ids or str(letter_id) in self._gan_holdout_ids

    def letter(self, dataset: str, letter_id: str) -> dict[str, Any] | None:
        dataset_id = self._require_dataset(dataset)
        if self.is_locked_letter(dataset_id, letter_id):
            return None
        if dataset_id == "gan2026":
            try:
                source_row_index = int(letter_id)
            except ValueError:
                return None
            return self.record("validation", source_row_index)
        for letter in self._exect_shared_letters():
            if str(letter.get("letter_id")) == letter_id:
                return copy.deepcopy(letter)
        return None

    def records(self, split: str) -> dict[str, Any] | None:
        dataset = _SPLIT_TO_DATASET.get(split)
        if dataset != "gan2026":
            return None
        payload = self.letters("gan2026")
        records = [
            {
                "source_row_index": int(letter["id"]),
                "gold_label": letter["label"],
                "gold_reference": letter.get("gold_reference") or "",
                "row_ok": bool(letter.get("row_ok", True)),
                "note_preview": letter["preview"],
            }
            for letter in payload["letters"]
        ]
        return {
            "split": "validation",
            "count": len(records),
            "records": records,
        }

    def record(self, split: str, source_row_index: int) -> dict[str, Any] | None:
        if _SPLIT_TO_DATASET.get(split) != "gan2026":
            return None
        if self.is_locked_letter("gan2026", str(source_row_index)):
            return None
        if str(source_row_index) not in self._gan_dev_ids:
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

    def runs(self, dataset: str) -> dict[str, Any]:
        dataset_id = self._require_dataset(dataset)
        if dataset_id == "exectv2":
            return self.exectv2_catalog()
        self._refresh_gan_validation()
        families = self.named("pipeline_families").get("families")
        if not isinstance(families, list):
            raise ValueError("Gan pipeline families must contain a list")
        return {
            "dataset": "gan2026",
            "split": "dev750",
            "runs": [copy.deepcopy(item) for item in families if isinstance(item, dict)],
        }

    def run(self, dataset: str, run_id: str) -> dict[str, Any] | None:
        dataset_id = self._require_dataset(dataset)
        if dataset_id == "exectv2":
            return self.exectv2_run(run_id)
        runs = self.runs("gan2026").get("runs")
        if not isinstance(runs, list):
            return None
        for item in runs:
            if isinstance(item, dict) and str(item.get("run_id")) == run_id:
                return {"dataset": "gan2026", "split": "dev750", "run": copy.deepcopy(item)}
        return None

    def artifact(
        self,
        run_id: str,
        *,
        limit: int | None = None,
        letter_id: str | None = None,
    ) -> dict[str, Any] | None:
        self._refresh_gan_validation()
        if letter_id is not None and self.is_locked_letter_id(letter_id):
            return None
        if self._gan_validation is not None:
            replay_path = self._gan_validation.replay_artifacts.get(run_id)
            if replay_path is not None:
                if letter_id is not None:
                    row = self._read_jsonl_matching(replay_path, letter_id)
                    content = [] if row is None else [self._hydrate_gan_replay_row(run_id, row)]
                else:
                    content = [
                        self._hydrate_gan_replay_row(run_id, row)
                        for row in self._read_jsonl(replay_path, limit=limit)
                    ]
                return {
                    "run_id": run_id,
                    "artifact_path": replay_path.relative_to(self._repo_root).as_posix(),
                    "artifact_type": "jsonl",
                    "content": content,
                }
        path = self._artifacts.get(run_id)
        if path is None:
            return None
        payload = self._object(path)
        rows = payload.get("content")
        if isinstance(rows, list) and letter_id is not None:
            payload["content"] = [
                item
                for item in rows
                if isinstance(item, dict) and self._row_matches_letter(item, letter_id)
            ]
        elif limit is not None and isinstance(rows, list):
            payload["content"] = rows[:limit]
        return payload

    def _discover_gan_validation(self) -> GanValidationDiscovery | None:
        config_path = self._repo_root.joinpath(
            "configs", "gan2026", "six_model_validation_comparison_20260718.json"
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
        config_path = self._repo_root.joinpath(
            "configs", "gan2026", "six_model_validation_comparison_20260718.json"
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
        hybrid_root = (
            repo_root / str(config["hybrid_artifact_root"])
            if config.get("hybrid_artifact_root")
            else None
        )
        paths = [
            config_path,
            *artifact_root.glob("*/*/validation750.rows.jsonl"),
            *artifact_root.glob("*--llm_only.jsonl"),
            *artifact_root.glob("*--llm_with_rules.jsonl"),
        ]
        if hybrid_root is not None:
            paths.extend(hybrid_root.glob("*/validation750.rows.jsonl"))
            paths.extend(hybrid_root.glob("*/*/validation750.rows.jsonl"))
            paths.extend(hybrid_root.glob("*--llm_with_rules.jsonl"))
        paper_gan = repo_root / "paper_experiments" / "gan"
        paths.append(paper_gan / "dev750_panel.json")
        paths.extend(paper_gan.glob("*/*/dev750/rows.jsonl"))
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

    def _paper_exect_run(self, run_id: str) -> dict[str, Any] | None:
        identity = paper_exect_identity(run_id)
        if identity is None:
            return None
        cached = self._paper_exect_run_cache.get(run_id)
        if cached is not None:
            return copy.deepcopy(cached)
        _slug, method = identity
        summary = next(
            (item for item in paper_exect_catalog_runs() if item["run_id"] == run_id),
            None,
        )
        if summary is None:
            return None
        paths = summary.get("artifact_paths") or []
        if not paths:
            return None
        rows_path = self._repo_root / str(paths[0])
        if not rows_path.is_file():
            return None
        gold_by_id = self._exect_gold_letters()
        letters = []
        for row in load_jsonl_rows(rows_path):
            letter_id = str(row.get("letter_id") or "")
            gold = gold_by_id.get(letter_id)
            if gold is None:
                continue
            raw_output = str(row.get("raw_output") or "")
            if method in {"llm_extract", "llm_encode", "llm_select"}:
                letters.append(
                    hydrate_exect_five_cell_letter(
                        gold,
                        raw_output,
                        model=str(summary["model"]),
                        cell=method,
                    )
                )
                continue
            lane: Literal["llm", "llm_with_rules"] = (
                "llm" if method == "exect_llm_only" else "llm_with_rules"
            )
            letters.append(
                hydrate_saved_exect_letter(
                    gold,
                    raw_output,
                    model=str(summary["model"]),
                    lane=lane,
                )
            )
        run = {**summary, "letters": letters}
        self._paper_exect_run_cache[run_id] = run
        return copy.deepcopy(run)

    def _exect_gold_letters(self) -> dict[str, Any]:
        if self._exect_gold_by_id is None:
            letters = load_letters_for_split("dev")
            self._exect_gold_by_id = {letter.letter_id: letter for letter in letters}
        return self._exect_gold_by_id

    def _hydrate_gan_replay_row(self, run_id: str, row: dict[str, Any]) -> dict[str, Any]:
        if row.get("structured_record") or row.get("decision_record") or row.get("row_trace"):
            return row
        identity = paper_identity_from_run_id(run_id)
        if identity is None:
            return row
        method, _slug = identity
        source = row.get("source_row_index")
        if source is None:
            return row
        record = self._validation_dataset_records.get(int(source))
        if record is None:
            return row
        hydrate_method = method
        repair_mode = _FIVE_CELL_REPAIR.get(method)
        if repair_mode is not None:
            hydrate_method = "gan_llm_extract_raw"
        if hydrate_method not in {"gan_llm_extract_raw", "gan_llm_only"}:
            return row
        return hydrate_saved_raw_row(
            hydrate_method,
            record,
            str(row.get("raw_output") or ""),
            repair_mode=repair_mode,
        )

    @classmethod
    def _read_jsonl_matching(cls, path: Path, letter_id: str) -> dict[str, Any] | None:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"expected object at {path}:{line_number}")
                if cls._row_matches_letter(value, letter_id):
                    return value
        return None

    @staticmethod
    def _row_matches_letter(row: dict[str, Any], letter_id: str) -> bool:
        identifiers = (
            row.get("source_row_index"),
            row.get("letter_id"),
            row.get("source_id"),
        )
        return any(value is not None and str(value) == letter_id for value in identifiers)

    def exectv2_catalog(self) -> dict[str, Any]:
        payload = self._exectv2_payload
        runs = payload.get("runs")
        if not isinstance(runs, list):
            raise ValueError("ExECTv2 runs resource must contain a list")
        paper_runs = paper_exect_catalog_runs()
        kept = [
            {**self._canonical_exect_run(run), "letters": []}
            for run in runs
            if isinstance(run, dict)
            and (
                not paper_runs
                or run.get("run_id") in {*RULES_METHOD_ALIASES, "exectv2_deterministic_all9_dev140"}
                or run.get("kind") == "rules"
                or run.get("pipeline_family") == "rules"
            )
        ]
        return {
            "generated_on": payload.get("generated_on"),
            "source_index": payload.get("source_index"),
            "dataset": "exectv2",
            "split": "dev140",
            "runs": [*paper_runs, *kept],
        }

    def exectv2_run(self, run_id: str) -> dict[str, Any] | None:
        payload = self._exectv2_payload
        runs = payload.get("runs")
        if not isinstance(runs, list) or not isinstance(payload.get("shared_letters"), list):
            raise ValueError("ExECTv2 runs resource is malformed")
        paper_run = self._paper_exect_run(run_id)
        if paper_run is not None:
            return {
                "generated_on": payload.get("generated_on"),
                "source_index": payload.get("source_index"),
                "dataset": "exectv2",
                "split": "dev140",
                "shared_letters": self._exect_shared_letters(),
                "run": paper_run,
            }
        catalog_runs = paper_exect_catalog_runs()
        canonical_runs = [
            self._canonical_exect_run(run)
            for run in runs
            if isinstance(run, dict)
            and (
                not catalog_runs
                or run.get("run_id") in {*RULES_METHOD_ALIASES, "exectv2_deterministic_all9_dev140"}
                or run.get("kind") == "rules"
                or run.get("pipeline_family") == "rules"
            )
        ]
        matches = [run for run in canonical_runs if self._exect_run_matches(run, run_id)]
        if len(matches) == 1:
            run = matches[0]
            run_letters = run.get("letters")
            if isinstance(run_letters, list):
                run = {**run, "letters": self._filter_exect_letters(run_letters)}
            return {
                "generated_on": payload.get("generated_on"),
                "source_index": payload.get("source_index"),
                "dataset": "exectv2",
                "split": "dev140",
                "shared_letters": self._exect_shared_letters(),
                "run": run,
            }
        return None

    @staticmethod
    def _canonical_exect_run(run: dict[str, Any]) -> dict[str, Any]:
        if run.get("run_id") not in {
            *RULES_METHOD_ALIASES,
            "exectv2_deterministic_all9_dev140",
        }:
            return run
        canonical = {**run, "run_id": "rules", "paper_cell": "rules_only"}
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

    def semantic_support_review_packets(self) -> dict[str, Any]:
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
        shared_letters = self._exect_shared_letters()
        if not isinstance(review_items, list):
            raise ValueError("semantic-support review source is malformed")

        letter_text_by_id = {
            str(letter["letter_id"]): str(letter["letter_text"])
            for letter in shared_letters
            if isinstance(letter.get("letter_text"), str)
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
        dataset_id = self._require_dataset(dataset)
        if dataset_id == "exectv2":
            rows = [
                self._exect_gold_audit_row(index, letter)
                for index, letter in enumerate(self._exect_shared_letters(), start=1)
            ]
        else:
            rows = [
                self._gan_gold_audit_row(index, record)
                for index, record in enumerate(self._gan_records(), start=1)
            ]
        return {
            "dataset": dataset_id,
            "split": _DATASET_SPLITS[dataset_id],
            "total": len(rows),
            "decided": 0,
            "class_counts": {},
            "rows": rows,
        }

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

    def _gan_records(self) -> list[Any]:
        return sorted(
            (
                record
                for record in self._validation_dataset_records.values()
                if str(record.source_row_index) in self._gan_dev_ids
            ),
            key=lambda item: int(item.source_row_index),
        )

    def _exect_shared_letters(self) -> list[dict[str, Any]]:
        shared_letters = self._exectv2_payload.get("shared_letters")
        if not isinstance(shared_letters, list):
            raise ValueError("ExECTv2 shared letters are unavailable")
        return self._filter_exect_letters(
            [letter for letter in shared_letters if isinstance(letter, dict)]
        )

    def _filter_exect_letters(self, letters: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [letter for letter in letters if self._exect_letter_is_browsable(letter)]

    def _exect_letter_is_browsable(self, letter: dict[str, Any]) -> bool:
        letter_id = str(letter.get("letter_id") or letter.get("id") or "")
        if not letter_id or letter_id in self._exect_holdout_ids:
            return False
        if letter_id not in self._exect_dev_ids:
            return False
        split = str(letter.get("split") or "")
        return not _is_locked_split_name(split)

    @staticmethod
    def _gan_letter_summary(record: Any) -> dict[str, Any]:
        note = record.note_text or ""
        return {
            "id": str(record.source_row_index),
            "dataset": "gan2026",
            "split": "dev750",
            "label": record.gold_label,
            "preview": note[:150] + ("..." if len(note) > 150 else ""),
            "gold_summary": record.gold_label,
            "gold_reference": record.gold_reference or "",
            "has_gold_reference": bool(record.gold_reference),
            "row_ok": bool(record.row_ok),
        }

    @staticmethod
    def _exect_letter_summary(letter: dict[str, Any]) -> dict[str, Any]:
        text = str(letter.get("letter_text") or "")
        gold_mentions = letter.get("gold_mentions")
        mention_count = len(gold_mentions) if isinstance(gold_mentions, list) else 0
        return {
            "id": str(letter.get("letter_id")),
            "dataset": "exectv2",
            "split": "dev140",
            "label": str(letter.get("letter_id")),
            "preview": text[:150] + ("..." if len(text) > 150 else ""),
            "gold_summary": f"{mention_count} gold mention{'s' if mention_count != 1 else ''}",
            "gold_reference": "",
            "has_gold_reference": mention_count > 0,
        }

    @staticmethod
    def _gan_gold_audit_row(index: int, record: Any) -> dict[str, Any]:
        return {
            "audit_id": str(record.source_row_index),
            "source_row_index": str(record.source_row_index),
            "validation_order": str(index),
            "split": "dev750",
            "gold_label": record.gold_label,
            "gold_label_kind": "frequency",
            "gold_reference": record.gold_reference or "",
            "row_ok": str(bool(record.row_ok)),
            "reference_found_in_note": str(bool(record.gold_reference)),
        }

    @staticmethod
    def _exect_gold_audit_row(index: int, letter: dict[str, Any]) -> dict[str, Any]:
        letter_id = str(letter.get("letter_id"))
        gold_mentions = letter.get("gold_mentions")
        mentions = gold_mentions if isinstance(gold_mentions, list) else []
        first = next((item for item in mentions if isinstance(item, dict)), {})
        evidence = str(first.get("evidence") or first.get("text") or "")
        return {
            "audit_id": letter_id,
            "fact_id": letter_id,
            "queue_position": index,
            "split": "dev140",
            "letter_id": letter_id,
            "entity": "letter",
            "source_span": evidence,
            "gold_label": f"{len(mentions)} gold mention{'s' if len(mentions) != 1 else ''}",
        }

    @staticmethod
    def _require_dataset(dataset: str) -> DatasetId:
        if dataset in _DATASET_SPLITS:
            return dataset  # type: ignore[return-value]
        raise ValueError(f"unknown dataset {dataset!r}")

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


def _is_locked_split_name(split: str) -> bool:
    key = "".join(character for character in split.casefold() if character.isalnum())
    return key in _LOCKED_SPLIT_KEYS


def _gan_split_ids(repo_root: Path) -> tuple[frozenset[str], frozenset[str]]:
    manifest = load_split_manifest(repo_root / GAN_SPLIT_MANIFEST)
    splits = manifest["splits"]
    return (
        frozenset(str(index) for index in splits["validation"]["source_row_indices"]),
        frozenset(str(index) for index in splits["test"]["source_row_indices"]),
    )


def _exect_split_ids(repo_root: Path) -> tuple[frozenset[str], frozenset[str]]:
    manifest = json.loads((repo_root / EXECT_SPLIT_MANIFEST).read_text(encoding="utf-8"))
    splits = manifest["splits"]
    return (
        frozenset(str(letter_id) for letter_id in splits["dev"]["letter_ids"]),
        frozenset(str(letter_id) for letter_id in splits["test"]["letter_ids"]),
    )
