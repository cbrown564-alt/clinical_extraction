# ExECTv2 Holistic Finding Assembly Research Report

Date: 2026-06-21  
Subject: `exectv2_holistic_finding_assembly_v08_dev140`  
Scope: dev140 component-attributed evidence only  
Model-bearing source family: GPT-4.1-mini focused producers plus no-call deterministic assembly replay

## Executive Summary

The renewed ExECTv2 objective was to use the holistic finding assembly
architecture to push all four key families above `0.900` headline F1, focusing
first on Diagnosis as the weakest component and maximizing Prescription last.
v08 achieves that dev140 objective:

| Family | v08 headline F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 0.9083 | 0.8762 | 0.9428 | 280 | 39 | 17 |
| SeizureFrequency | 0.9053 | 0.9000 | 0.9107 | 153 | 17 | 15 |
| Prescription | 0.9357 | 0.9286 | 0.9430 | 182 | 14 | 11 |
| Investigations | 0.9132 | 0.9380 | 0.8897 | 121 | 8 | 15 |
| Overall | 0.9152 | 0.9037 | 0.9270 | 736 | 78 | 58 |

This is not a full-200, locked-test, benchmark, or deployment claim. It is a
dev-only result over the first 140 dev rows. The report below treats semantic
deterministic rules as prediction-bearing components, not incidental
normalization, and separates clinical-headline gains from benchmark/CUI and
fidelity companion surfaces.

The largest conceptual change was not a single prompt. It was the assembly
discipline: freeze candidate producers, reconcile one family at a time with an
explicit entity lens or arbitration layer, run row-level ledgers after each
phase, reject broad plausible fixes that failed ablations, and promote only
small rule families whose error-reduction mechanism was visible in the data.

## Core Architecture Changes

The final v08 manifest is a manifest-driven assembly over frozen producer
artifacts. Each family owns a producer and lens with explicit ownership and
portability labels:

```yaml
candidate_id: exectv2_holistic_finding_assembly_v08_dev140
pipeline_family: exectv2_holistic_finding_assembly
ownership: component_attributed_holistic_finding_replay
split: dev
row_count: 140
claim_boundary: dev_only_component_evidence
producers:
  diagnosis_reconciler_v01:
    kind: saved_jsonl
    artifact: experiments/exectv2_hybrid_diagnosis_reconciler_v01_dev140_gpt41mini_20260618.jsonl
    ownership_label: hybrid_diagnosis_route
  sf_union_arbitration_v08:
    kind: saved_jsonl
    artifact: experiments/exectv2_hybrid_sf_union_arbitration_v08_dev140_20260621.jsonl
    ownership_label: hybrid_sf_route+deterministic_union_arbitration
  investigations_arbitration_v02:
    kind: saved_jsonl
    artifact: experiments/exectv2_llm_investigations_arbitration_v02_dev140_20260621.jsonl
    ownership_label: llm_investigations_verifier+deterministic_investigations_arbitration
  prescription_repair_v03:
    kind: saved_jsonl
    artifact: experiments/exectv2_deterministic_prescription_repair_v03_dev140_20260621.jsonl
    ownership_label: deterministic_prescription_repair_v03
lenses:
  Diagnosis:
    producer: diagnosis_reconciler_v01
    lens: diagnosis_heading_recovery_residual_benchmark_v05
    portability: benchmark_format
  SeizureFrequency:
    producer: sf_union_arbitration_v08
    lens: sf_state_union_arbitration_v08
    portability: seizure_frequency
  Prescription:
    producer: prescription_repair_v03
    lens: prescription_regimen_v01
    portability: clinical_epilepsy
  Investigations:
    producer: investigations_arbitration_v02
    lens: investigations_result_v01
    portability: clinical_epilepsy
```

The assembly runner builds a per-letter store, applies lenses, and renders every
view from the same finding objects:

```python
rows: list[dict[str, Any]] = []
stores: dict[str, ClinicalFindingStore] = {}
for letter in gold_letters:
    store, row = _assemble_letter(
        letter,
        manifest=manifest,
        producers=producers,
        source_rows=source_rows,
    )
    stores[letter.letter_id] = store
    rows.append(row)

raw_predictions = predictions_from_rows(rows, "raw_lane_mentions")
scored_predictions = predictions_from_rows(rows, "predicted_mentions")
views, score_ladder, target_report = build_scoring_views(
    candidate_name=manifest.candidate_id,
    ownership=manifest.ownership,
    gold_letters=gold_letters,
    raw_predictions=raw_predictions,
    scored_predictions=scored_predictions,
)
```

The scoring spine was deliberately multi-surface. `raw_lane_score` measures raw
producer/lens candidates, `evidence_valid_score` measures exact-evidence
survivors, `cui_projection_companion` measures deterministic CUI projection, and
`headline_target` applies the declared clinical target projection:

```python
score_ladder = {
    "raw_lane_score": _target_surface(raw_arch, projected=False),
    "evidence_valid_score": _target_surface(scored_arch, projected=False),
    "cui_projection_companion": _target_surface(projected_arch, projected=False),
    "headline_target": _target_surface(scored_arch, projected=True),
    "benchmark": benchmark,
    "fidelity_companions": fidelity,
}
```

This was essential because the headline target and the benchmark/CUI surfaces
answer different questions. The headline shows family-level clinical extraction
under the declared target indicator policy; the benchmark and fidelity views
show stricter or differently projected behavior that must not be hidden.

## Phase Score Progression

| Version | Main accepted change | Overall F1 | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| v01 | Behavior-preserving holistic replay | 0.8006 | 0.7572 | 0.8068 | 0.8214 | 0.8615 |
| v02 | Diagnosis focal-epilepsy heading recovery | 0.8038 | 0.7658 | 0.8068 | 0.8214 | 0.8615 |
| v03 | Diagnosis convention cleanup | 0.8130 | 0.7894 | 0.8068 | 0.8214 | 0.8615 |
| v04 | Diagnosis convention alias repair | 0.8278 | 0.8301 | 0.8068 | 0.8214 | 0.8615 |
| v05 | Diagnosis residual benchmark repair | 0.8576 | 0.9083 | 0.8068 | 0.8214 | 0.8615 |
| v06 | SF union arbitration | 0.8789 | 0.9083 | 0.9053 | 0.8214 | 0.8615 |
| v07 | Investigations pending-test arbitration | 0.8873 | 0.9083 | 0.9053 | 0.8214 | 0.9132 |
| v08 | Prescription deterministic regimen repair | 0.9152 | 0.9083 | 0.9053 | 0.9357 | 0.9132 |

The sequence matters. We did not mix many changes into one aggregate rerun. Each
phase kept the already-cleared families fixed, changed one family, wrote a
family-specific error analysis, and compared against ablations before promotion.

## Every v08 Scoring View

The final headline is high, but the other views show why this is still a
bounded development result.

| View | Overall P/R/F1 (TP/FP/FN) | Diagnosis | SeizureFrequency | Prescription | Investigations |
| --- | ---: | ---: | ---: | ---: | ---: |
| `raw_lane_score` | 0.8142/0.8521/0.8328 (680/154/118) | 0.7387/0.7879/0.7625 (234/81/63) | 0.7371/0.8314/0.7814 (143/51/29) | 0.9286/0.9430/0.9357 (182/14/11) | 0.9380/0.8897/0.9132 (121/8/15) |
| `evidence_valid_score` | 0.8657/0.9098/0.8872 (726/112/72) | 0.8762/0.9428/0.9083 (280/39/17) | 0.7371/0.8314/0.7814 (143/51/29) | 0.9286/0.9430/0.9357 (182/14/11) | 0.9380/0.8897/0.9132 (121/8/15) |
| `cui_projection_companion` | 0.8657/0.9098/0.8872 (726/112/72) | 0.8762/0.9428/0.9083 (280/39/17) | 0.7371/0.8314/0.7814 (143/51/29) | 0.9286/0.9430/0.9357 (182/14/11) | 0.9380/0.8897/0.9132 (121/8/15) |
| `headline_target` | 0.9037/0.9270/0.9152 (736/78/58) | 0.8762/0.9428/0.9083 (280/39/17) | 0.9000/0.9107/0.9053 (153/17/15) | 0.9286/0.9430/0.9357 (182/14/11) | 0.9380/0.8897/0.9132 (121/8/15) |

Benchmark and fidelity companions:

| Surface | Value |
| --- | ---: |
| Benchmark raw | 0.3693 |
| Benchmark after CUI/projection | 0.3990 |
| Benchmark raw Diagnosis | 0.2857 |
| Benchmark raw Investigations | 0.4981 |
| Benchmark raw Prescription | 0.2948 |
| Benchmark raw SeizureFrequency | 0.5120 |
| Diagnosis.concept_negation F1 | 0.9083 |
| Diagnosis.concept_negation fidelity gap | 0.0000 |
| SeizureFrequency.active_rate_fidelity F1 | 0.5969 |
| SeizureFrequency.active_rate_fidelity gap | 0.1845 |

Lane diagnostics:

| Entity | Raw mentions | Scored mentions | Call failures | Parse/schema failures | Evidence-invalid dropped | Exact evidence rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Diagnosis | 438 | 421 | 0 | 0 | 2 | 1.0000 |
| SeizureFrequency | 270 | 270 | 0 | 0 | 0 | 1.0000 |
| Prescription | 201 | 201 | 0 | 0 | 0 | 1.0000 |
| Investigations | 129 | 129 | 0 | 0 | 0 | 1.0000 |

Interpretation: exact evidence is strong, but exact evidence is not the same as
clinical correctness. The SF active-rate companion remains low, so the SF claim
is a type/state headline improvement rather than a solved quantitative-rate
fidelity result.

## Phase 0: v01 Holistic Replay Baseline

v01 converted earlier focused artifacts into a common `ClinicalFindingStore`
without trying to improve behavior. Its value was measurement: every family
could now be scored through the same view ladder and every mention carried
source and lens provenance.

v01 baseline:

| Family | Headline F1 | Precision | Recall | Main residual found |
| --- | ---: | ---: | ---: | --- |
| Diagnosis | 0.7572 | 0.7346 | 0.7811 | Generic epilepsy over-emission plus focal/syndrome/seizure-type misses |
| SeizureFrequency | 0.8068 | 0.7717 | 0.8452 | State often right, rate magnitude weaker |
| Prescription | 0.8214 | 0.8090 | 0.8342 | Dose/frequency and future-regimen boundaries |
| Investigations | 0.8615 | 0.9032 | 0.8235 | Completed test result-state misses |

The key architectural result was diagnostic: the raw candidates contained
complementary signal, but broad union or prompt replacement was rarely enough.
The next phases therefore operated family by family.

## Phase 1: Diagnosis First

Diagnosis was the weakest family and stayed the hardest because many residuals
were not clinical ignorance. They were convention and benchmark-surface
decisions: whether to emit generic `epilepsy`, when tonic-clonic facts count as
Diagnosis rather than frequency/history, and how source phrases map to scored
CUIPhrase fragments.

### v02: Focal-Epilepsy Heading Recovery

Accepted change: add a Diagnosis mention only when the `Diagnosis:` heading
itself explicitly contains focal epilepsy.

```python
def _focal_epilepsy_heading_findings(
    store: ClinicalFindingStore,
    *,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> tuple[ClinicalFinding, ...]:
    section_match = _DIAGNOSIS_HEADING.search(store.note_text)
    if section_match is None:
        return ()
    section = section_match.group("section")
    stop = _DIAGNOSIS_HEADING_STOP.search(section)
    if stop is not None:
        section = section[: stop.start()]
    focal_match = _FOCAL_EPILEPSY.search(section)
    if focal_match is None:
        return ()

    evidence = focal_match.group(0)
    attributes = {
        "DiagCategory": diagnosis_category_for_concept("focal epilepsy"),
        "Certainty": "4" if _CERTAINTY_4_CUE.search(section[: focal_match.end()]) else "5",
        "Negation": "Affirmed",
    }
```

Impact:

| View | Overall | Diagnosis | Other families |
| --- | ---: | ---: | --- |
| v01 headline | 0.8006 | 0.7572 | unchanged controls |
| v02 headline | 0.8038 | 0.7658 | unchanged controls |

Why it worked: row-level Diagnosis misses included explicit compact heading
statements. Broader heading insertion was ablated and hurt precision; this
accepted rule was narrow because it required exact heading evidence and one
specific concept family.

Overfitting risk: moderate but controlled. It is dev-derived, but the principle
is portable within epilepsy letters: an explicit `Diagnosis:` heading has higher
assertion weight than surrounding narrative. The exact `focal epilepsy` scope is
safer than a general heading-to-concept expansion.

### v03: Diagnosis Convention Cleanup

The next error ledger showed that GPT-4.1-mini prompt variants were not solving
Diagnosis. A live 32-row residual panel tested two prompt hypotheses:

| Prompt hypothesis | Result | Decision |
| --- | ---: | --- |
| Candidate selector over fixed residual candidates | F1 0.697, delta -0.012 vs v02 panel control | reject |
| Direct re-reader over same panel | F1 0.693, delta -0.016 vs v02 panel control | reject |

The rejected prompt was still useful because it proved the error was not simply
"ask GPT-4.1-mini harder." The prompt contained explicit policy text:

```python
"strict_constraints": [
    "Return final Diagnosis mentions only.",
    "Use exact source substrings for evidence; unsupported mentions are dropped.",
    "Do not include CUI or CUIPhrase in attributes.",
    (
        "Do not emit seizure-frequency facts as Diagnosis unless the source "
        "asserts a diagnosis or seizure type."
    ),
    "Do not infer structural or symptomatic epilepsy from imaging or history alone.",
],
"diagnosis_policy": {
    "generic_epilepsy": (
        "Emit generic epilepsy only when patient-level established epilepsy is "
        "directly asserted. Reject section headers, clinic names, family history, "
        "or medication context alone."
    ),
```

The accepted v03 change was deterministic cleanup of standalone symptom or
non-diagnostic over-emissions:

```python
def _drop_diagnosis_convention_noise(finding: ClinicalFinding) -> bool:
    concept = canonicalize_diagnosis_concept(finding.text)
    normalized_text = normalize_phrase(finding.text)
    if (
        concept in _DIAGNOSIS_STANDALONE_NOISE or normalized_text in _DIAGNOSIS_STANDALONE_NOISE
    ) and finding.attributes.get("DiagCategory") != "Epilepsy":
        return True
    if concept != "epilepsy":
        return False
    evidence = finding.evidence or finding.text
    return bool(_WEAK_GENERIC_EPILEPSY_CONTEXT.search(evidence)) and not bool(
        _STRONG_GENERIC_EPILEPSY_CONTEXT.search(evidence)
    )
```

Impact:

| Artifact | Overall | Diagnosis | Diagnosis P | Diagnosis R | Strict Diagnosis F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v02 | 0.8038 | 0.7658 | 0.7346 | 0.7811 | 0.7061 |
| v03 | 0.8130 | 0.7894 | 0.7944 | 0.7845 | 0.7276 |

Row-level effect: 21 Diagnosis rows changed, all by dropping over-emitted
concepts. Strict Diagnosis false positives dropped from 95 to 73 while strict
true positives dropped only 221 to 219.

Overfitting risk: low to moderate. Dropping `dissociative seizures`,
`myoclonic jerks`, isolated `absences`, and weak generic `epilepsy` contexts is
a clinical-convention rule, not a single-row patch. The risk is that some notes
could use those terms diagnostically, so the rule must remain tied to standalone
noise and weak evidence contexts rather than global term deletion.

### v04: Diagnosis Convention Alias Repair

v04 moved from deletion to phrase repair where the model had already selected
the right clinical neighborhood but not the scored convention term.

```python
class DiagnosisConventionAliasLens(DiagnosisConventionCleanupLens):
    """Apply v04 benchmark/convention alias repair after v03 cleanup."""

    def reconcile(
        self,
        store: ClinicalFindingStore,
        *,
        policy: LensPolicy,
    ) -> LensResult:
        v03 = super().reconcile(store, policy=policy)
        rewritten: list[ClinicalFinding] = []
        kept: list[ClinicalFinding] = []
        dropped: list[ClinicalFinding] = []
        for finding in v03.findings:
            target_text = _diagnosis_convention_alias_target(finding)
            if target_text is not None:
                rewritten_finding = _diagnosis_finding_with_text(
                    finding,
                    target_text,
                    owner_suffix="deterministic_convention_alias_repair",
                    provenance=ProvenanceEvent(
                        stage="entity_lens",
                        action="rewrote_diagnosis_convention_alias",
                        owner="deterministic_convention_alias_repair",
                        portability="benchmark_format",
```

Impact:

| Artifact | Overall | Diagnosis | Diagnosis P | Diagnosis R | Strict Diagnosis F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v03 | 0.8130 | 0.7894 | 0.7944 | 0.7845 | 0.7276 |
| v04 | 0.8278 | 0.8301 | 0.8459 | 0.8148 | 0.7609 |

Accepted actions included `focal dyscognitive seizures -> dyscognitive
seizures`, `grand mal seizure -> grand mal`, `secondarily generalised seizures
-> secondary generalised seizures`, and related structural/syndrome convention
repairs. Broad tonic-clonic, secondary-generalised, JME, and symptomatic
epilepsy additions were tested and rejected or flat.

Overfitting risk: moderate to high if described as clinical generalization,
lower if described correctly as benchmark-format repair. These rewrites are
portable only as a controlled scoring-convention layer, not as evidence that
the model learned better Diagnosis semantics.

### v05: Diagnosis Residual Benchmark Repair

v05 finished the Diagnosis push by attacking residual exact source-phrase
conventions and generic noise.

```python
def _diagnosis_residual_benchmark_target(finding: ClinicalFinding) -> str | None:
    if finding.entity != DIAGNOSIS.name:
        return None
    concept = canonicalize_diagnosis_concept(finding.text)
    evidence = finding.evidence or finding.text
    if (
        concept == "focal epilepsy"
        and re.search(r"\bsymptomatic epilepsy\b", evidence, re.IGNORECASE)
        and not re.search(r"\bfocal\b", evidence, re.IGNORECASE)
    ):
        return "symptomatic epilepsy"
    if concept == "focal epilepsy" and re.search(
        r"\bsymptomatic focal epilepsy\b",
        evidence,
        re.IGNORECASE,
    ):
        return "symptomatic focal epilepsy"
    if concept == "temporal lobe epilepsy" and re.search(
        r"focal seizures, probably temporal lobe",
        evidence,
        re.IGNORECASE,
    ):
        return "temporal lobe seizures"
    if concept == "secondary generalised tonic clonic seizures":
        if re.search(r"secondary generalisation", evidence, re.IGNORECASE):
            return "secondary generalisation"
        if re.search(r"secondary generalised seizures", evidence, re.IGNORECASE):
            return "secondary generalised seizures"
    return None
```

The additions were likewise explicit source-phrase repairs:

```python
def _diagnosis_residual_benchmark_additions(
    store: ClinicalFindingStore,
    *,
    selected: list[ClinicalFinding],
    policy: LensPolicy,
    lens_id: str,
) -> tuple[ClinicalFinding, ...]:
    added: list[ClinicalFinding] = []
    for pattern, text in _RESIDUAL_SOURCE_CONCEPT_PATTERNS:
        match = pattern.search(store.note_text)
        if match is None:
            continue
        if _has_diagnosis_concept([*selected, *added], text=text):
            continue
        finding = _diagnosis_added_finding(
            store,
            text=text,
            evidence=match.group(0),
            selected=[*selected, *added],
            policy=policy,
            lens_id=lens_id,
        )
        if finding is not None:
            added.append(finding)
    return tuple(added)
```

Impact:

| Artifact | Overall | Diagnosis | Diagnosis P | Diagnosis R | Strict Diagnosis F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v04 | 0.8278 | 0.8301 | 0.8459 | 0.8148 | 0.7609 |
| v05 | 0.8576 | 0.9083 | 0.8762 | 0.9428 | 0.8127 |

Accepted action counts: 10 residual rewrites, 41 residual additions, and 22
generic/residual drops. Diagnosis crossed the `>0.900` target, but strict
Diagnosis stayed at `0.8127`, showing the gain is strongly tied to the declared
concept-only headline and benchmark-format convention layer.

Overfitting risk: high unless carefully bounded. v05 uses dev residual
benchmark concepts and should be reported as benchmark-format residual repair.
The portable principle is not the exact list of terms; it is the method:
separate exact source-phrase convention mismatches from genuine clinical
extraction misses, then label the repair as benchmark-facing.

## Phase 2: SeizureFrequency Union Arbitration

v05 SF was `0.8068`. Row-level analysis showed complementary sources: the
current GPT SF lane had high recall but too many type/state false positives,
while deterministic all-entity SF had better precision but lower recall.

The winning design was not naive union. It was union plus deterministic
arbitration:

```python
def arbitrate_sf_mentions(
    *,
    current_mentions: Sequence[Mapping[str, Any]],
    deterministic_mentions: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    kept: list[dict[str, Any]] = []
    actions: list[dict[str, str]] = []
    for source, mentions in (
        ("current", current_mentions),
        ("det", deterministic_mentions),
    ):
        for mention in mentions:
            copied = _mention_to_row(mention)
            drop_rule = _drop_rule(copied, source=source)
            if drop_rule:
                actions.append(_action(drop_rule, "drop", copied, "seizure_frequency"))
                continue
            transformed, rewrite_rule = _rewrite(copied)
            if rewrite_rule:
                actions.append(
                    _action(rewrite_rule, "rewrite", transformed, "benchmark_format")
                )
            kept.append(transformed)
    return _dedupe_mentions(kept), actions
```

The main suppression and rewrite rules were source-aware:

```python
if source == "det" and phrase in _SHORT_GENERIC_ANCHORS and len(evidence.strip()) <= 18:
    return "drop_det_short_generic_anchor"
if _HISTORICAL_OR_ADVICE_RE.search(evidence) and state != "unknown":
    return "drop_historical_or_advice_state"
if (
    source == "current"
    and state == "seizure-free"
    and _BARE_FREE_CONTEXT_RE.search(evidence)
    and not _QUALIFIED_FREE_CONTEXT_RE.search(evidence)
):
    return "drop_bare_seizure_free_context"
if phrase == "cluster of 3":
    copied["text"] = "seizure cluster"
    attrs["CUI"] = "C3203523"
    attrs["CUIPhrase"] = "seizure cluster"
```

Ablation data:

| Ablation | Surface | SF F1 | P | R | TP | FP | FN | Interpretation |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v05 current GPT SF lane | official assembly | 0.8068 | 0.7717 | 0.8452 | 142 | 42 | 26 | High recall, too many state/type FPs |
| deterministic all-entity SF drop-in | assembly diagnostic | 0.8263 | 0.8313 | 0.8214 | 138 | 28 | 30 | Better precision, recall short |
| current and deterministic intersection | assembly diagnostic | 0.8464 | 0.9920 | 0.7381 | 124 | 1 | 44 | Precision oracle, recall too low |
| current and deterministic union | assembly diagnostic | 0.8041 | 0.7022 | 0.9405 | 158 | 67 | 10 | Recall reserve, noisy |
| v08 union arbitration | direct SF artifact | 0.9263 | 0.9181 | 0.9345 | 157 | 14 | 11 | Suppression plus rewrites solve most union noise |
| v06 holistic assembly | official assembly | 0.9053 | 0.9000 | 0.9107 | 153 | 17 | 15 | Promoted dev-only family headline |

Action counts:

| Rule | Count | Category |
| --- | ---: | --- |
| `drop_det_short_generic_anchor` | 84 | seizure_frequency |
| `drop_non_target_event` | 9 | seizure_frequency |
| `drop_historical_or_advice_state` | 8 | seizure_frequency |
| `drop_bare_seizure_free_context` | 6 | seizure_frequency |
| `drop_anaphoric_generic_state` | 5 | seizure_frequency |
| `drop_named_unknown_long_context` | 4 | seizure_frequency |
| `drop_det_generic_short_rate` | 3 | seizure_frequency |
| `drop_diffuse_unknown` | 3 | seizure_frequency |
| `drop_generic_free_history_or_span` | 3 | seizure_frequency |
| other suppression rules | 5 | seizure_frequency |
| benchmark rewrites | 5 | benchmark_format |

Overfitting risk: moderate. Most suppression rules are portable
seizure-frequency principles: reject non-target events, historical advice,
short source anchors, and anaphoric ownership errors. The benchmark rewrites
(`cluster of 3 -> seizure cluster`, `absences -> typical absences`) are
benchmark-format and should stay separately labeled. The active-rate fidelity
companion of `0.5969` is the main residual risk: the headline improved type and
state, not full numeric rate fidelity.

## Phase 3: Investigations Pending-Test Arbitration

Investigations started at `0.8615`. GPT-4.1-mini verifier v0.1 improved recall
but introduced planned/requested test false positives. Its prompt was clinically
reasonable and exact-evidence constrained:

```python
"task": (
    "Review the clinical letter and draft Investigations mentions from "
    "the single structured key-entity extractor. Return final "
    "Investigations mentions only. You may keep, delete, edit, or add "
    "mentions, but every final mention must be supported by exact source "
    "evidence."
),
"clinical_rules": _clinical_rules(),
```

The clinical rules included:

```python
(
    "Emit completed historical tests. Omit planned, requested, arranged, "
    "future, or recommended tests unless a separate completed test is also "
    "stated."
),
(
    "Do not return modality-only mentions for planned tests such as 'I will "
    "arrange an MRI', 'request EEG', or 'organise CT'."
),
```

The model still left eight pending-test residual false positives. The accepted
deterministic arbitration made that policy executable:

```python
_PENDING_TEST_RE = re.compile(
    r"\b(?:will|arrang(?:e|ed|ing)|request(?:ed|ing)?|await(?:ing)?|"
    r"appointment|suggest|recommend|should update|today agreed to chase|"
    r"up to date|not yet (?:performed|received)|planned)\b",
    re.IGNORECASE,
)

def _drop_action(mention: Mapping[str, Any]) -> dict[str, Any] | None:
    attrs = dict(mention.get("attributes") or {})
    evidence = str(mention.get("evidence", ""))
    rationale = str(mention.get("rationale", ""))
    context = f"{evidence} {rationale}"
    if _has_performed_no(attrs) and _PENDING_TEST_RE.search(context):
        return _action(
            rule_id="drop_pending_or_planned_investigation",
            mention=mention,
        )
    if _has_unknown_result(attrs) and _PENDING_TEST_RE.search(context):
        return _action(
            rule_id="drop_requested_unknown_investigation",
            mention=mention,
        )
    return None
```

Ablation data:

| Assembly | Investigations F1 | P | R | TP | FP | FN | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v06 control | 0.8615 | 0.9032 | 0.8235 | 112 | 12 | 24 | superseded |
| verifier v0.1 drop-in | 0.8864 | 0.8832 | 0.8897 | 121 | 16 | 15 | near miss |
| verifier/control intersection | 0.8000 | 0.9787 | 0.6765 | 92 | 2 | 44 | too recall-poor |
| verifier/control union | 0.8372 | 0.7636 | 0.9265 | 126 | 39 | 10 | too noisy |
| v07 verifier plus pending-test arbitration | 0.9132 | 0.9380 | 0.8897 | 121 | 8 | 15 | accepted |

Overfitting risk: low to moderate. Suppressing future/requested tests is a
portable clinical-extraction principle for a completed-test target. However, the
regex initially included an overbroad appointment-style cue that could suppress
valid completed tests in follow-up context; this is the clearest example where
we avoided overfitting by removing a plausible but unsafe rule. The portable
principle is "pending/requested test emissions are not completed historical
tests," not "any appointment context is negative."

## Phase 4: Prescription Deterministic Regimen Repair

Prescription was saved for last because it had the least clinical ambiguity and
the highest expected ceiling. Prompted replacements failed to beat the existing
control by much; the deterministic all-9 parser was the right anchor.

Final accepted lexical and context changes:

```python
_MEDICATION_EXTRA_SURFACE_ALIASES = {
    "lamtorigine": "lamotrigine",
}
_FREQUENCY_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"\b(?:bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+aday|"
            r"twice\s+daily|twice\s+today)\b",
            re.IGNORECASE,
        ),
        "2",
    ),
)
_PRESCRIPTION_FUTURE_LEFT_CONTEXT = re.compile(
    r"\b(?:should\s+be\s+increased|so\s+that\s+(?:he|she|they)\s+is\s+on|"
    r"suggest\s+adding|suggested\s+adding|suggest\s+introducing|"
    r"suggested\s+introducing|to\s+start\s+treatment\s+with)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_WEIGHT_BASED_CONTEXT = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g|grams?)\s*/?\s*kg(?:\s*/?\s*day)?\b",
    re.IGNORECASE,
)
```

The important parser-boundary change was to keep current regimen text while
trimming future titration tails:

```python
def _trim_planned_regimen_tail(text: str) -> str:
    trimmed = re.split(
        r"\s*(?:\((?:to|please|increase|increasing|reduce|reducing)\b|"
        r"\bincreasing\s+by\b|\breducing\s+by\b)",
        text,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0]
    return trimmed.strip(" ,;")
```

And to reject future-left contexts only after checking that the row actually
has a complete current regimen candidate:

```python
def _is_prescription_context(text: str, match: re.Match[str], evidence: str) -> bool:
    local_left = text[max(0, match.start() - 180) : match.start()]
    sentence_left = text[max(0, text.rfind(".", 0, match.start()) + 1) : match.start()]
    if _PRESCRIPTION_NEGATIVE_CONTEXT.search(sentence_left) and not _active_after_negative_context(
        sentence_left
    ):
        return False
    has_complete_regimen = bool(
        _DOSE_PATTERN.search(evidence)
        and (
            _frequency_from_text(evidence)
            or ("/" in evidence and len(_DOSE_PATTERN.findall(evidence)) > 1)
        )
    )
    has_prn_rescue = _frequency_from_text(evidence) == "As_Required"
    if not (has_complete_regimen or has_prn_rescue):
        return False
    if _PRESCRIPTION_FUTURE_LEFT_CONTEXT.search(local_left):
        return False
```

Focused tests encoded the portable parser behaviors rather than individual
letter IDs:

```python
def test_prescription_keeps_current_dose_before_parenthetical_titration() -> None:
    letter = ExectLetter(
        "PRESC-CURRENT-BEFORE-TITRATION",
        "Medication: lamtorigine 250mg bd (to reduce as detailed below).",
    )

    prediction = extract_deterministic_all9(letter)
    prescriptions = [m for m in prediction.mentions if m.entity == PRESCRIPTION.name]

    assert len(prescriptions) == 1
    assert prescriptions[0].text == "lamtorigine 250mg bd"
    assert prescriptions[0].attributes["DrugName"] == "lamotrigine"
    assert prescriptions[0].attributes["DrugDose"] == "250"
    assert prescriptions[0].attributes["Frequency"] == "2"
```

Impact:

| Candidate | Prescription F1 | P | R | TP | FP | FN | Decision |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| v07 control | 0.8214 | 0.8090 | 0.8342 | 161 | 38 | 32 | superseded |
| med/inv verifier drop-in | 0.8166 | 0.7731 | 0.8653 | 167 | 49 | 26 | reject |
| per-entity GPT-4.1-mini drop-in | 0.8201 | 0.7634 | 0.8860 | 171 | 53 | 22 | reject |
| prescription adjudicator v02 drop-in | 0.8308 | 0.7990 | 0.8653 | 167 | 42 | 26 | reject |
| deterministic all9 drop-in | 0.9072 | 0.9293 | 0.8860 | 171 | 13 | 22 | clears target |
| deterministic repair v01 | 0.9243 | 0.9316 | 0.9171 | 177 | 13 | 16 | accepted step |
| deterministic repair v03 / v08 lane | 0.9357 | 0.9286 | 0.9430 | 182 | 14 | 11 | accepted |

Overfitting risk: moderate. The accepted rules are mostly portable medication
parser principles: spelling aliases, left-bound dose forms, AM/PM split doses,
future-plan suppression, and weight-based exclusion. The risk rises in the
remaining residuals, especially letter-specific titration plans and annotation
oddities such as a gold `DrugName=Perampanel` for a brivaracetam-looking text.
Stopping at `0.9357` rather than forcing `0.95` was the right research decision.

## Prompt Changes and Model Usage

The final assembly is no-call replay. GPT-4.1-mini matters because several
source artifacts were produced by focused GPT-4.1-mini programs, but the v08
assembly did not make fresh calls.

Surviving model-bearing components:

| Component | Prompt version / source | Role in final result |
| --- | --- | --- |
| Diagnosis reconciler | `exectv2_hybrid_diagnosis_reconciler_v0.2` source artifact | Frozen Diagnosis producer, then deterministic lenses v02-v05 |
| SF state adjudicator | `exectv2_hybrid_sf_state_adjudicator_v0.5` source artifact | Current GPT SF lane unioned with deterministic all9 |
| Investigations verifier | `exectv2_llm_investigations_verifier_v0.1` | Primary completed-test verifier, then pending-test arbitration |
| Prescription GPT variants | med/inv verifier, per-entity, adjudicator v02 | Tested and rejected in favor of deterministic parser |

Rejected prompt lesson: precise instructions and exact evidence did not
automatically fix convention selection. The Diagnosis residual panel had zero
call/parse failures and exact evidence validity of `1.000`, yet both model
variants underperformed the v02 panel control. This supports the project thesis
that exact grounding is necessary but not sufficient; the scoring policy and
deterministic semantic repair remain controlled variables.

## Overfitting Assessment by Rule Family

| Rule family | Portability category | Overfitting risk | Why |
| --- | --- | --- | --- |
| Diagnosis focal heading recovery | clinical_epilepsy | Moderate | Portable heading principle, but accepted only for one dev-derived concept |
| Diagnosis standalone noise cleanup | clinical_epilepsy | Low-moderate | Symptom/non-epileptic standalone terms are broadly portable, but can be diagnostic in some notes |
| Diagnosis convention aliases | benchmark_format | Moderate-high | Useful for ExECTv2 CUIPhrase conventions; should not be called clinical generalization |
| Diagnosis residual benchmark additions | benchmark_format | High | Directly dev residual and benchmark-surface oriented |
| SF source-short anchor suppression | seizure_frequency | Low-moderate | Short anchors are a common extraction artifact; source-aware rule reduces brittleness |
| SF benchmark rewrites | benchmark_format | Moderate-high | Correct for this scoring surface, not a general clinical inference |
| Investigations pending-test suppression | clinical_epilepsy | Low | Completed-test target should omit planned/requested tests |
| Investigations appointment/context suppression | clinical_epilepsy | High if broad | We removed overbroad variants after they threatened true positives |
| Prescription regimen parser repair | clinical_epilepsy | Moderate | Mostly portable parser boundaries; residual singletons could invite overfit |

The biggest overfitting control was methodological: every accepted family had
negative ablations around it. We did not promote broad rules just because they
were clinically plausible; they had to improve the family surface without
creating a new error family.

## What Actually Produced Stable Improvement

Across all families, the common pattern was:

1. Freeze the candidate source before optimizing. This made each phase a
   controlled assembly/lens change rather than a moving prompt-and-model target.
2. Diagnose at row level before designing rules. The winning rules came from
   visible clusters: generic Diagnosis convention errors, SF short anchors,
   pending Investigation tests, and Prescription regimen boundaries.
3. Prefer family-specific arbitration over global prompting. GPT-4.1-mini was
   useful, but broad live prompt swaps often added plausible false positives.
4. Treat union as a recall reservoir, not a final answer. SF and Investigations
   both showed that union recovered recall but was too noisy; arbitration was
   the real improvement.
5. Label deterministic semantics honestly. Adding, dropping, or rewriting a
   clinical finding is prediction-bearing even when implemented in a lens or
   parser.
6. Separate clinical-headline, benchmark, CUI, and fidelity views. This allowed
   us to claim the achieved target without hiding weaker companion surfaces.
7. Stop when the residual becomes idiosyncratic. Prescription could perhaps be
   pushed closer to `0.95`, but the remaining errors were increasingly
   annotation-specific or plan-boundary singletons.
8. Add tests around principles, not rows. The Prescription tests encode parser
   behaviors such as current-after-prior-trial and future-plan suppression,
   making the repair more portable than a letter-ID patch.

The resulting improvement was significant because it aligned the mechanism with
the family. Diagnosis needed convention-aware benchmark repair; SF needed
source-aware type/state arbitration; Investigations needed completed-vs-planned
test suppression; Prescription needed deterministic regimen parsing. The shared
architecture let those family-specific solutions remain auditable, ablatable,
and comparable under one score ladder.

## Residual Risks and Next Evidence Needed

- The result is dev140 only. Any full-200 or holdout-facing readout needs a
  predeclared protocol before opening row-level failures.
- Diagnosis is above target on the official concept headline, but strict
  assertion/convention behavior remains weaker.
- SF headline is above target, but active-rate fidelity remains `0.5969`.
- Prescription stopped below the hoped-for `~0.95`; further gains risk
  overfitting unless tested on hard-case panels.
- The assembly gate still reports `do-not-promote` because older changed-row
  checks assumed Prescription and Investigations should remain unchanged. The
  renewed goal condition was all four family headlines above `0.900`, which v08
  satisfies.

Canonical artifacts:

- `configs/exectv2/finding_assembly/exectv2_holistic_finding_assembly_v08_dev140.yaml`
- `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.json`
- `experiments/exectv2_holistic_finding_assembly_v08_dev140_20260621.jsonl`
- `docs/experiments/exectv2/key_entities/exectv2_holistic_finding_assembly_v08_dev140_20260621.md`
- `experiments/exectv2_holistic_finding_assembly_v08_error_ledger_dev140_20260621.md`
- `docs/experiments/exectv2/reliability/exectv2_reliability_scorecard_and_phased_plan_2026-06-21.md`
