from __future__ import annotations

import json
import os
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import model_swap
from scripts.run_exectv2_six_model_comparison import configure_declared_runtime


def test_six_model_configs_freeze_exact_roster_runtime_and_graph() -> None:
    paths = sorted(Path("configs/exectv2/six_model_comparison").glob("*.json"))
    configs = [model_swap.load_model_swap_config(path) for path in paths]
    payloads = [json.loads(path.read_text(encoding="utf-8")) for path in paths]

    assert len(configs) == 6
    assert {config.model for config in configs} == {
        "openai/gpt-4.1-mini",
        "openai/gpt-5.6-luna",
        "openai/gpt-5.6-sol",
        "deepseek/deepseek-v4-flash",
        "ollama_chat/qwen3.6:35b",
        "ollama_chat/gemma4:26b",
    }
    assert all(config.prompt_profile == "full" for config in configs)
    by_config_model = {config.model: config for config in configs}
    assert by_config_model["openai/gpt-5.6-luna"].temperature == 1
    assert by_config_model["openai/gpt-5.6-sol"].temperature == 1
    assert by_config_model["openai/gpt-5.6-luna"].max_tokens == {
        "structured_key_family_event_ledger": 16000,
    }
    assert by_config_model["openai/gpt-5.6-sol"].max_tokens == {
        "structured_key_family_event_ledger": 16000,
    }
    assert by_config_model["deepseek/deepseek-v4-flash"].max_tokens == {
        "structured_key_family_event_ledger": 16000,
    }
    for local_model in ("ollama_chat/qwen3.6:35b", "ollama_chat/gemma4:26b"):
        assert by_config_model[local_model].max_tokens == {
            "structured_key_family_event_ledger": 16000,
        }
    assert all(
        config.temperature == 0
        for config in configs
        if not config.model.startswith("openai/gpt-5.6-")
    )
    assert all(config.assembly.split == "dev140" for config in configs)
    assert all(config.assembly.row_count == 140 for config in configs)
    assert all(config.calls_per_letter == 1 for config in configs)
    assert all(
        config.live_call_components == ("structured_key_family_event_ledger",)
        for config in configs
    )
    assert all(
        config.assembly.lenses["Diagnosis"].producer
        == "structured_key_family_event_ledger"
        for config in configs
    )
    assert all("diagnosis_decomposer" not in config.assembly.producers for config in configs)
    assert all("single_call" in config.candidate_id for config in configs)
    assert all("single_call" in config.output_json.name for config in configs)
    assert all(
        model_swap.validate_model_led_architecture(config)["status"] == "pass"
        for config in configs
    )
    assert model_swap.validate_same_core_configs(configs)["component_graph_identical"] is True

    by_model = {payload["model"]: payload for payload in payloads}
    deepseek = by_model["deepseek/deepseek-v4-flash"]["runtime_metadata"]
    assert deepseek["endpoint"] == "https://api.deepseek.com"
    assert deepseek["thinking"] == "enabled_by_api_default"
    assert deepseek["route_probe"]["reasoning_content_present"] is True
    assert deepseek["route_probe"]["final_content_present"] is True

    qwen = by_model["ollama_chat/qwen3.6:35b"]["runtime_metadata"]
    gemma = by_model["ollama_chat/gemma4:26b"]["runtime_metadata"]
    assert qwen["thinking"] == "disabled_with_think_false"
    assert qwen["num_ctx"] == 32768
    assert qwen["digest"] == (
        "07d35212591fc27746f0a317c975a6d68754fb38e9053d82e25f06057af28522"
    )
    assert gemma["thinking"] == "disabled_with_think_false"
    assert gemma["num_ctx"] == 32768
    assert gemma["digest"] == (
        "5571076f3d70050487b26b341705799e0ab29b808164f90d20d4cf84f699d251"
    )


def test_local_runtime_config_wires_declared_num_ctx(monkeypatch) -> None:
    monkeypatch.delenv("CLINICAL_EXTRACTION_OLLAMA_NUM_CTX", raising=False)

    configure_declared_runtime(
        Path("configs/exectv2/six_model_comparison/qwen36_35b_dev140.json")
    )

    assert os.environ["CLINICAL_EXTRACTION_OLLAMA_NUM_CTX"] == "32768"
