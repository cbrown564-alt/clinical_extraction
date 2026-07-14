# Evidence groundedness

Implementation: `src/clinical_extraction/core/evidence.py`.

Evidence groundedness asks whether cited text is present in the note after
format-only text repair. It does not judge whether the text clinically supports
the prediction.

- `evidence_grounded_rate`: exact or safely repaired citations divided by all citations;
- `evidence_exact_rate`: exact substring citations divided by all citations.

`score_evidence_set(note_text, evidence)` accepts one string or a sequence and
returns exact, repaired, absent, or empty grades. New runs use
`evidence_grounded`; older saved files may use `evidence_valid` or
`evidence_text_contained`.

## Grades

| Grade | Meaning | Counts as grounded? |
| --- | --- | :---: |
| `EXACT` | Verbatim substring | Yes |
| `REPAIRED_ARTIFACT` | Found after neutral encoding/control-character cleanup | Yes |
| `REPAIRED_CASE` | Found after case-only repair | Yes |
| `REPAIRED_WHITESPACE` | Found after whitespace repair | Yes |
| `REPAIRED_ELLIPSIS` | Both ends of a bounded omission are present | Yes |
| `REPAIRED_SECTION` | Header and list item occur in one source section | Yes |
| `ABSENT` | Not found | No |
| `EMPTY` | No citation supplied | No |

Every repaired grade is returned only when the repaired text exists in the note.
Prediction filters may still require an exact match; changing such a filter can
change predictions and requires a separate study.

In a selected Qwen replay, neutral repair recovered an encoding error in the
`≤` symbol and explained much of the difference between exact-copy and grounded
rates. The Gan reliability report records the limited result.
