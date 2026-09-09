"""The provisional longitudinal format must preserve evidence and time boundaries.

Always-on admission: this new track has no existing schema/evidence coverage.
These checks protect authored references from invalid spans, reversed bounds and
future evidence; they do not test clinical correctness or old benchmark labels.
"""

from copy import deepcopy
from pathlib import Path

import pytest

from scripts.longitudinal.check_annotations import check_annotations, load_example

EXAMPLE = Path("examples/longitudinal/authored_patient_001")


def test_authored_annotations_preserve_original_sources_and_all_families() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    check_annotations(annotations, documents, schema)
    assert {a["content"]["family"] for a in annotations["assertions"]} == {
        "diagnosis", "seizure", "medication", "investigation"
    }


def test_reject_invalid_evidence_and_future_letter() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    altered = deepcopy(annotations)
    altered["assertions"][0]["evidence"][0]["text"] = "Invented evidence"
    with pytest.raises(ValueError, match="span"):
        check_annotations(altered, documents, schema)
    with pytest.raises(ValueError, match="cutoff"):
        check_annotations(annotations, documents, schema, cutoff="2025-01-15")


def test_reject_reversed_time_and_dangling_link() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    altered = deepcopy(annotations)
    altered["assertions"][0]["time"]["start"] = {
        "earliest": "2025-02-01", "latest": "2025-01-01"
    }
    with pytest.raises(ValueError, match="bounds"):
        check_annotations(altered, documents, schema)
    altered = deepcopy(annotations)
    altered["links"][0]["earlier_assertion"] = "missing"
    with pytest.raises(ValueError, match="endpoint"):
        check_annotations(altered, documents, schema)


def test_preserve_unknown_and_cluster_quantities_without_point_imputation() -> None:
    annotations, documents, schema = load_example(EXAMPLE)
    altered = deepcopy(annotations)
    seizure = next(a for a in altered["assertions"] if a["content"]["family"] == "seizure")
    # Shape probe only: the source sentence is not claimed to support these values.
    seizure["content"]["burden"] = {
        "kind": "clusters", "text": "unknown spacing, 2 to 4 events per cluster",
        "count": {"lower": None, "upper": None}, "period": None,
        "events_per_cluster": {"lower": 2, "upper": 4}, "approximate": False,
    }
    check_annotations(altered, documents, schema)
    assert seizure["content"]["burden"]["count"]["lower"] is None
    seizure["content"]["burden"]["events_per_cluster"]["lower"] = 5
    with pytest.raises(ValueError, match="quantity"):
        check_annotations(altered, documents, schema)
