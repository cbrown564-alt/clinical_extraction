from clinical_extraction.core import schemas


def test_core_schemas_expose_only_task_neutral_models() -> None:
    assert hasattr(schemas, "EvidenceSpan")
    assert hasattr(schemas, "FinalExtraction")
    assert not hasattr(schemas, "SeizureEvent")
