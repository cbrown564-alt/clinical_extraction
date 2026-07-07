"""Closed-option direction selector primitives for the ExECTv2 SF direction surface.

Library module shared by:
  - ``scripts/run_exectv2_sf_closed_option_direction_probe.py`` (the standalone
    probe that produced the +0.0552 cross-family refute of "fundamental"), and
  - ``scripts/run_exectv2_sf_closed_option_hybrid_integration.py`` (the hybrid-
    lane integration follow-up).

This module is the single source of the closed-option contract: the LLM never
free-writes a direction; it picks a ``candidate_id`` verbatim from a deterministic
menu of the closed 5-value ``FrequencyChange`` vocab plus an ``ABSTAIN`` option,
or abstains. This is the dspy G32 principle (pick-from-menu-or-abstain)
transferred to the ExECTv2 SF direction surface.

The abstention-validated selector contract mirrors gan2026's
``SelectedCandidateDecision`` (``contract/selected_fact.py:32-49``): a defer mode
MUST NOT select an id. The deterministic assembly mirrors gan2026's
``assemble_clinical_assessment``: the model only picks an id; deterministic code
renders the final attribute, with provenance stamped so the hybrid integration
can attribute each direction to its source (research-protocol attribution rule).

Gold closed vocab (``rules/change.py:3``): {Decreased, Frequent, Increased,
Infrequent, Same}. ``Same`` doubles as the abstain outcome (the directional-
neutral bucket).
"""

from __future__ import annotations

import json
from typing import Literal

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.rules.change import (
    CHANGE_EXTRACT_IMPLS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)

# The closed 5-value gold vocab everywhere in code/gold/scorer for FrequencyChange.
DIRECTION_VOCAB: tuple[str, ...] = ("Increased", "Decreased", "Frequent", "Infrequent", "Same")
# rule_id suffix -> the FrequencyChange label it generates (from change.py builders).
_RULE_TO_LABEL: dict[str, str] = {
    "change.increased": "Increased",
    "change.decreased": "Decreased",
    "change.frequent": "Frequent",
    "change.infrequent": "Infrequent",
    "change.same": "Same",
}
ABSTAIN = "ABSTAIN"
DEFER_MODES: tuple[str, ...] = ("no_reliable_candidate", "ambiguous")

# Provenance labels (research-protocol attribution: keep the prediction-bearing
# source clear). Used by the hybrid integration to stamp each direction's source.
PROV_LLM_CLOSED_OPTION = "llm_closed_option_selector"
PROV_DETERMINISTIC_RULES_CHANGE = "deterministic_rules_change"

DirectionSelectorMode = Literal["off", "llm_closed_option"]


# --------------------------------------------------------------------------------------
# Deterministic candidate menu (the closed-option contract substrate).
# --------------------------------------------------------------------------------------
def build_direction_menu(letter_text: str) -> list[dict[str, str]]:
    """Emit the closed-option direction menu for one letter.

    The menu is the **full closed 5-label gold vocab + ABSTAIN, always** -- this
    is the dspy G32 pattern: the LLM picks a label from a fixed deterministic
    menu, never free-writes. The deterministic layer's contribution is the
    *evidence anchor* attached to each label (the rules/change.py regex span if
    one matches, otherwise an explicit no-cue marker). The option set is never
    gated by whether a regex matched: that would make the menu empty for letters
    whose direction is expressed implicitly or via medication-titration language,
    collapsing the experiment into a trivial no-op.
    """

    menu: list[dict[str, str]] = []
    # First pass: collect the first regex evidence span per label (if any).
    evidence_by_label: dict[str, str] = {}
    for rule_id, impl in CHANGE_EXTRACT_IMPLS.items():
        label = _RULE_TO_LABEL.get(rule_id)
        if label is None or label in evidence_by_label:
            continue
        m = impl.pattern.search(letter_text)
        if m:
            evidence_by_label[label] = m.group(0).strip()[:160]
    # Emit every label in the closed vocab, with its evidence or a no-cue marker.
    for label in DIRECTION_VOCAB:
        ev = evidence_by_label.get(label, "(no explicit cue in text)")
        menu.append(
            {"candidate_id": f"C{len(menu)}", "label": label, "evidence_span": ev}
        )
    menu.append({"candidate_id": ABSTAIN, "label": ABSTAIN, "evidence_span": ""})
    return menu


# --------------------------------------------------------------------------------------
# Abstention-validated selector contract (the cross-family architectural difference).
# --------------------------------------------------------------------------------------
class ClosedOptionDirectionSelectorSignature(dspy.Signature):
    """You read a clinical letter and a candidate menu of seizure-frequency
    change-direction labels.

    Select ONE candidate_id from the menu that best describes the direction of
    the patient's seizure-frequency change, or select ABSTAIN if the letter does
    not state a clear direction.

    HARD CONSTRAINTS:
    - Return a candidate_id that appears in the menu exactly. Never invent,
      renumber, or free-write a direction label.
    - If you are not confident, select ABSTAIN.
    - Return a JSON object matching the output schema exactly. No markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    candidate_menu: str = dspy.InputField(
        desc="JSON list of {candidate_id, label, evidence_span}. Pick one candidate_id."
    )
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    selection_json: str = dspy.OutputField(
        desc='One JSON object {"selected_candidate_id": "...", "selection_mode": '
        '"single_candidate|no_reliable_candidate|ambiguous"}. No markdown.'
    )


SELECTION_SCHEMA_JSON = json.dumps(
    {
        "selected_candidate_id": "a candidate_id from the menu, or ABSTAIN",
        "selection_mode": "single_candidate | no_reliable_candidate | ambiguous",
    },
    ensure_ascii=False,
    sort_keys=True,
)


class ClosedOptionDirectionSelector(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.select = dspy.Predict(ClosedOptionDirectionSelectorSignature)

    def forward(self, letter_text: str, candidate_menu: str) -> dspy.Prediction:
        out = self.select(
            letter_text=letter_text,
            candidate_menu=candidate_menu,
            output_schema=SELECTION_SCHEMA_JSON,
        )
        return dspy.Prediction(selection_json=str(getattr(out, "selection_json", "") or ""))


def parse_selection(raw: str) -> tuple[str | None, str]:
    """Parse the selector output; enforce the abstention validator.

    Mirrors gan2026 selected_fact.py:32-49: a defer mode MUST NOT select an id.
    Returns (candidate_id | None, selection_mode).
    """

    try:
        payload = json.loads(extract_json_object(raw))
    except Exception:
        return None, "parse_error"
    cid = str(payload.get("selected_candidate_id", "")).strip() or None
    mode = str(payload.get("selection_mode", "")).strip() or "single_candidate"
    if mode in DEFER_MODES and cid and cid != ABSTAIN:
        # Validator: defer modes forbid a selection. Force abstention.
        return None, mode
    if cid == ABSTAIN:
        return None, mode
    return cid, mode


def assemble_direction(
    cid: str | None, menu: list[dict[str, str]]
) -> tuple[str, str]:
    """Deterministic assembly: candidate_id -> (FrequencyChange label, provenance).

    Mirrors gan2026 assemble_clinical_assessment: the model only picks an id;
    deterministic code renders the final attribute. An invalid id (not in the
    menu) also resolves to ``Same`` with provenance ``abstain`` -- the menu-
    membership check (_validate_candidate_references analogue) is implicit here.
    Returns (label, provenance) so the hybrid integration can stamp each
    direction's source (research-protocol attribution rule).
    """

    if cid is None:
        return "Same", PROV_LLM_CLOSED_OPTION
    for entry in menu:
        if entry["candidate_id"] == cid:
            return entry["label"], PROV_LLM_CLOSED_OPTION
    return "Same", PROV_LLM_CLOSED_OPTION
