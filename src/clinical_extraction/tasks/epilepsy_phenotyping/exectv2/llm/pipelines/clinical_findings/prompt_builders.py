"""Stage 1 clinical-findings extraction prompt payload builders."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.prompts.clinical_findings.loader import (
    load_extraction_prompt_corpus,
)


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the clinical-findings prompt payload for one letter."""

    payload = {
        **load_extraction_prompt_corpus(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
