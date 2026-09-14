"""Offline R5 dev750 schema-use audit; never loads datasets or holdout artifacts."""

# Markdown tables retain one row per line.
# ruff: noqa: E501
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, median

from pydantic import ValidationError

from clinical_extraction.tasks.seizure_frequency.gan2026.evaluation import (
    one_shot_measurements_dev as dev,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5

ROOT = Path("runs/one_shot_thinking_r4_r5_r6/dev750")
OUT = Path("results/letter-benchmarks/gan/one_shot_thinking_r4_r5_r6/r5_schema_profile")
LOCAL = ROOT / "r5_schema_profile"
KINDS = [
    "recurring_rate",
    "observed_count",
    "cluster_pattern",
    "seizure_free_interval",
    "last_seizure",
    "qualitative_frequency",
]


def lines(path):
    return [json.loads(s) for s in path.read_text().splitlines()]


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def describe(values):
    nonnull = [v for v in values if v is not None]
    counts = Counter(encoded(v) for v in nonnull)
    result = {
        "eligible": len(values),
        "populated": len(nonnull),
        "null": len(values) - len(nonnull),
        "distinct": len(counts),
        "top": [{"value": json.loads(k), "n": n} for k, n in counts.most_common(5)],
    }
    if nonnull and all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in nonnull):
        result["numeric"] = {
            "min": min(nonnull),
            "median": median(nonnull),
            "mean": mean(nonnull),
            "max": max(nonnull),
        }
    return result


def main():
    OUT.mkdir(exist_ok=True)
    LOCAL.mkdir(exist_ok=True)
    files = [
        ROOT / "requests.jsonl",
        ROOT / "responses.jsonl",
        ROOT / "timeout600/responses.jsonl",
        ROOT / "timeout600/timeout_completed/responses.jsonl",
    ]
    requests = {q["request_id"]: q for q in lines(files[0]) if q["condition"] == "r5_rich"}
    originals = {r["request_id"]: r for r in lines(files[1]) if r["request_id"] in requests}
    reruns = {r["request_id"]: r for r in lines(files[2]) if r["request_id"] in requests}
    mixed = {r["request_id"]: r for r in lines(files[3]) if r["request_id"] in requests}
    assert len(requests) == len(originals) == len(mixed) == 750
    assert len({q["source_row_index"] for q in requests.values()}) == 750
    assert len(reruns) == 40
    for rid, r in mixed.items():
        assert r == reruns.get(rid, originals[rid])
        if rid in reruns:
            assert originals[rid]["error"] == "ReadTimeout" and originals[rid]["response"] is None
    statuses = Counter()
    findings = []
    documents = []
    failures = []
    original_counts = Counter()
    repeat_counts = Counter()
    for rid, q in sorted(requests.items(), key=lambda x: x[1]["source_row_index"]):
        r = mixed[rid]
        base = {
            "source_row_index": q["source_row_index"],
            "request_id": rid,
            "attempt": "timeout600" if rid in reruns else "original",
        }
        content = r["response"]["choices"][0]["message"]["content"] if r.get("response") else ""
        match = dev.ENVELOPE.fullmatch(content or "")
        if not match or "[[ ##" in match[1]:
            statuses["invalid_envelope"] += 1
            failures.append({**base, "failure": "invalid_envelope"})
            continue
        try:
            data = json.loads(match[1], object_pairs_hook=r5.r4.v1._unique_object)
            r5.Rich.model_validate(data)
        except (ValueError, TypeError) as exc:
            statuses["invalid_schema_or_json"] += 1
            errors = (
                exc.errors(include_input=False, include_url=False)
                if isinstance(exc, ValidationError)
                else str(exc)
            )
            failures.append({**base, "failure": "invalid_schema_or_json", "errors": errors})
            continue
        statuses["schema_valid"] += 1
        source = (
            q["body"]["messages"][1]["content"].split("[[ ## prompt_input_json ## ]]")[1].lstrip()
        )
        note = json.JSONDecoder().raw_decode(source)[0]["note_text"]
        selected = set(data["selected_finding_ids"])
        document = {
            **base,
            "n_findings": len(data["findings"]),
            "n_selected": len(selected),
            "answer": data["answer"],
            "answer_evidence_matches_selected": any(
                data["answer"]["evidence"] == f["evidence"]
                for f in data["findings"]
                if f["finding_id"] in selected
            ),
        }
        documents.append(document)
        for f in data["findings"]:
            findings.append(
                {
                    **base,
                    "finding": f,
                    "selected": f["finding_id"] in selected,
                    "exact_evidence": f["evidence"] in note,
                }
            )
            (repeat_counts if rid in reruns else original_counts)[f["measurement"]["kind"]] += 1
    assert sum(statuses.values()) == 750
    schema = r5.Rich.model_json_schema()
    definitions = schema["$defs"]
    fields = defaultdict(list)
    schemas = {}

    def resolve(s):
        return definitions[s["$ref"].split("/")[-1]] if "$ref" in s else s

    def visit(value, s, path, group, seed=False):
        s = resolve(s)
        if "anyOf" in s or "oneOf" in s:
            variants = [
                resolve(v)
                for v in s.get("anyOf", s.get("oneOf"))
                if resolve(v).get("type") != "null"
            ]
            if len(variants) == 1:
                return visit(value, variants[0], path, group, seed)
            schemas[(group, path)] = s
            if seed:
                fields[(group, path)]
                for variant in variants:
                    kind = variant["properties"]["kind"]["const"]
                    visit(None, variant, path + "<" + kind + ">", group, True)
            else:
                fields[(group, path)].append(value)
                if value is not None:
                    variant = next(
                        v for v in variants if v["properties"]["kind"]["const"] == value["kind"]
                    )
                    visit(value, variant, path + "<" + value["kind"] + ">", group)
            return
        schemas[(group, path)] = s
        if seed:
            fields[(group, path)]
        else:
            fields[(group, path)].append(value)
        if s.get("type") == "object" and (seed or value is not None):
            for key, child in s.get("properties", {}).items():
                if not seed:
                    assert key in value
                visit(
                    None if seed else value[key],
                    child,
                    path + "." + key if path else key,
                    group,
                    seed,
                )

    def walk(value, s, path, group):
        visit(None, s, path, group, True)
        visit(value, s, path, group)

    for row in findings:
        kind = row["finding"]["measurement"]["kind"]
        fs = {**definitions["Finding"], "properties": dict(definitions["Finding"]["properties"])}
        ms = fs["properties"]["measurement"]
        fs["properties"]["measurement"] = {
            "oneOf": [v for v in ms["oneOf"] if resolve(v)["properties"]["kind"]["const"] == kind]
        }
        walk(row["finding"], fs, "", kind)
    # Common attributes also get a pooled denominator across all findings.
    for row in findings:
        for key in [
            "finding_id",
            "event",
            "temporal_status",
            "observation_period",
            "condition",
            "evidence",
        ]:
            walk(
                row["finding"][key], definitions["Finding"]["properties"][key], key, "all_findings"
            )
    for d in documents:
        walk(d["answer"], definitions["Answer"], "answer", "documents")
    profile = []
    for (group, path), values in sorted(fields.items()):
        if not path:
            continue
        s = schemas[(group, path)]
        d = describe(values)
        if s.get("type") == "object" or "oneOf" in s or "anyOf" in s:
            d.pop("top", None)
            d["object"] = True
        allowed = s.get(
            "enum",
            [s["const"]] if "const" in s else [False, True] if s.get("type") == "boolean" else None,
        )
        if allowed is not None:
            d["levels"] = [
                {"value": v, "n": sum(x == v for x in values if x is not None)} for v in allowed
            ]
        profile.append({"group": group, "path": path, **d})
    quantities = Counter()
    approximations = Counter()
    timepoints = Counter()
    units = Counter()

    def scan(value):
        if not isinstance(value, dict):
            return
        if value.get("kind") in ["exact", "range", "bound", "qualitative"]:
            quantities[value["kind"]] += 1
            if "approximate" in value:
                approximations[str(value["approximate"])] += 1
        if {"wording", "form", "precision"} <= value.keys():
            timepoints[value["precision"]] += 1
        if {"quantity", "unit"} <= value.keys():
            units[value["unit"]] += 1
        for child in value.values():
            scan(child)

    for row in findings:
        scan(row["finding"])
    bykind = []
    for kind in KINDS:
        rows = [r for r in findings if r["finding"]["measurement"]["kind"] == kind]
        bykind.append(
            {
                "kind": kind,
                "findings": len(rows),
                "letters": len({r["source_row_index"] for r in rows}),
                "selected": sum(r["selected"] for r in rows),
                "original_findings": original_counts[kind],
                "rerun_findings": repeat_counts[kind],
                "observation_period": sum(
                    r["finding"]["observation_period"] is not None for r in rows
                ),
                "condition": sum(r["finding"]["condition"] is not None for r in rows),
                "temporal_status": dict(Counter(r["finding"]["temporal_status"] for r in rows)),
            }
        )
    bydoc = defaultdict(list)
    for r in findings:
        bydoc[r["source_row_index"]].append(r)
    structural = Counter()
    examples = defaultdict(list)

    def hit(name, row, extra=None):
        structural[name] += 1
        if len(examples[name]) < 5:
            examples[name].append(
                {
                    "source_row_index": row["source_row_index"],
                    "finding_id": row["finding"]["finding_id"],
                    "evidence": row["finding"]["evidence"],
                    **(extra or {}),
                }
            )

    for row in findings:
        f = row["finding"]
        m = f["measurement"]
        op = f["observation_period"]
        if op:
            hit("observation_period_present", row)
            if all(op[k] is None for k in ["start", "end", "duration"]):
                hit("observation_period_wording_only", row)
        if m["kind"] == "cluster_pattern":
            hit(
                "cluster_cadence_"
                + str(m["cadence"] is not None)
                + "_size_"
                + str(m["seizures_per_cluster"] is not None),
                row,
            )
        if m["kind"] == "seizure_free_interval":
            hit(
                "seizure_free_duration_"
                + str(m["duration"] is not None)
                + "_since_"
                + str(m["since"] is not None),
                row,
            )
            for other in bydoc[row["source_row_index"]]:
                g = other["finding"]
                n = g["measurement"]
                if (
                    n["kind"] == "last_seizure"
                    and g["event"] == f["event"]
                    and m["since"] is not None
                    and m["since"] == n["when"]
                ):
                    hit(
                        "seizure_free_matching_last_time_and_event",
                        row,
                        {
                            "other_finding_id": g["finding_id"],
                            "same_evidence": f["evidence"] == g["evidence"],
                        },
                    )
                    break
        others = [x["finding"] for x in bydoc[row["source_row_index"]] if x is not row]
        if any(
            {k: v for k, v in f.items() if k != "finding_id"}
            == {k: v for k, v in g.items() if k != "finding_id"}
            for g in others
        ):
            hit("exact_duplicate_except_id", row)
        if any(f["evidence"] == g["evidence"] for g in others):
            hit("shared_evidence_with_another_finding", row)
    summary = {
        "version": "r5_schema_profile_v1",
        "population": (
            "synthetic Gan dev750; all rows; original + timeout reruns, one response per letter"
        ),
        "condition": r5.VERSION,
        "model": next(iter(requests.values()))["body"]["model"],
        "runtime": {
            k: v for k, v in next(iter(requests.values()))["body"].items() if k != "messages"
        },
        "original_valid_letters": sum(d["attempt"] == "original" for d in documents),
        "rerun_valid_letters": sum(d["attempt"] == "timeout600" for d in documents),
        "nonempty_letters": sum(d["n_findings"] > 0 for d in documents),
        "scoring": "none; schema validity only, independent of answer-label validity",
        "repair": "none",
        "statuses": dict(statuses),
        "valid_letters": len(documents),
        "findings": len(findings),
        "findings_per_valid_letter": describe([d["n_findings"] for d in documents]),
        "selected_per_valid_letter": describe([d["n_selected"] for d in documents]),
        "quantities": dict(quantities),
        "approximations": dict(approximations),
        "timepoint_precision": dict(timepoints),
        "duration_units": dict(units),
        "nonexact_evidence_ids": [
            {"source_row_index": r["source_row_index"], "finding_id": r["finding"]["finding_id"]}
            for r in findings
            if not r["exact_evidence"]
        ],
        "exact_evidence": sum(r["exact_evidence"] for r in findings),
        "answer_evidence_matches_selected": sum(
            d["answer_evidence_matches_selected"] for d in documents
        ),
        "by_kind": bykind,
        "structural": dict(structural),
        "examples": dict(examples),
        "failures": failures,
        "source_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "schema_sha256": hashlib.sha256(encoded(schema).encode()).hexdigest(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    (OUT / "attributes.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2) + "\n")
    (LOCAL / "findings.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in findings)
    )
    (LOCAL / "documents.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in documents)
    )
    write_report(summary, profile)
    print(
        json.dumps(
            {k: v for k, v in summary.items() if k not in ["examples", "source_sha256"]}, indent=2
        )
    )


def write_report(summary, profile):
    def pct(n, d):
        return f"{n:,}/{d:,} ({100 * n / d:.1f}%)" if d else "0/0 (not observed)"

    def cell(value):
        return str(value).replace("|", "\\|").replace("\n", " ")

    def details(row):
        if "levels" in row:
            return "; ".join(f"{cell(x['value'])}: {x['n']}" for x in row["levels"])
        if "numeric" in row:
            n = row["numeric"]
            return (
                f"min {n['min']:g}; median {n['median']:g}; max {n['max']:g}; mean {n['mean']:.2f}"
            )
        if row.get("object"):
            return "Object/union; see child fields" if row["eligible"] else "Variant not emitted"
        top = "; ".join(f"{cell(str(x['value'])[:75])}: {x['n']}" for x in row["top"][:3])
        return f"{row['distinct']} distinct; {top}" if row["eligible"] else "Variant not emitted"

    sections = [
        """# R5 dev750 schema-use audit

## Findings and recommended decisions

**All six measurement types have substantial use. This audit does not support
removing any whole measurement type.** It does identify one structurally redundant
field and several candidates for reducing output verbosity or clarifying definitions.
Usage is model behaviour on synthetic letters, not a source-first reference or a
clinical necessity measure. A field can be absent because the source lacks the
information, because the model omitted it, or because the schema discouraged it.

| Component | Observed evidence | Recommendation |
| --- | --- | --- |
| `cluster_pattern.cadence.kind` | 88/88 populated cadence objects say `recurring_rate`; the field location already fixes its type. | Strongest lossless structural simplification: omit this nested discriminator in a new candidate. Retain the outer measurement and quantity discriminators, which select genuinely different structures. |
| Required null fields and `approximate: false` | `condition` is null in 2,091/2,355 findings; `observation_period` is null in 1,383/2,355. Numeric quantities say false for approximation in 1,924/2,079 occurrences. | Consider optional output fields with explicit defaults if the chosen structured-output API supports them. This reduces verbosity, not clinical information. Missing and explicit null must have identical declared semantics before doing this; no savings or accuracy improvement has been measured. |
| Event grouping | 1,279 one-type, 79 explicitly combined and 997 unspecified findings. Both invalid records fail this enum. | Review the definition and spelling guidance; do not remove grouping on low-use grounds. It protects the distinction between a combined count and separately reported event types. |
| Event seizure interpretation | 337 uncertain, 15 explicitly non-seizure and 54 not-specified findings, alongside 1,949 stated-seizure findings. | Retain. These are material distinctions, even if source-first review may revise individual classifications. |
| `temporal_status` | 1,791 current; 324 recent; 232 historical; 6 future; 2 unclear. | Clarify current versus recent with annotation examples. Their overlap is a possible modelling ambiguity, not demonstrated redundancy. Do not merge them based on these counts alone. |
| Unquantified cluster patterns | 130/277 have neither cadence nor size. | Retain cluster meaning. Moving these to generic qualitative wording would remove an explicit cluster category; consider that only as a deliberate redesign, not a lossless deletion. |
| Seizure-free intervals without a time | 237/543 have neither duration nor since. | Retain the event-scoped absence state. A date is not required for a source to state that a seizure type is absent. Review whether the name “interval” adequately covers this use. |
| Observation-period wording | 243/972 populated periods have no start, end or duration. | Retain wording: it is the only structured time content for these periods. Endpoints are sparse but not redundant. |
| `last_seizure` versus seizure-free `since` | Only 6 seizure-free findings have an identical event object and time point in a separate last-seizure finding from the same letter. | Retain both meanings. Matching timestamps do not make “last event at X” and “none since X” interchangeable. This exact-match test is conservative; it does not resolve paraphrased event names. |
| Time-point form and precision | 637 time points; none uses second, minute or hour precision. Day, week, month, year and unspecified all occur. | No observed need for sub-day **date precision** in this run. Keeping these enum options is cheap; removing form/precision would require reconstructing them from wording. Do not confuse date precision with duration units: hourly rates and minute observation windows do occur. |
| Answer evidence and finding evidence | Answer evidence exactly repeats a selected finding's evidence in 525/719 nonempty records (73.0%). | Potential storage deduplication only. Retain independently declared answer evidence in the current comparison; replacing it with links would change the answer-only comparator and fails to cover all records without an additional rule. |
| Finding IDs and answer links | 219/746 letters select multiple findings; 1,098/2,355 findings are selected. | Retain links for attribution. IDs are local to a letter; repeated `f1` values across letters are expected, not duplicate records. |

The sensible next candidate would start with the redundant nested cadence tag and,
if supported, optional null/default serialization. Keep the clinical distinctions
until the source-first annotation can measure whether they are accurate and useful.
No schema changes, new model calls or performance comparisons were made by this audit.

## Population, provenance and checks

- Dataset: synthetic Gan dev750, loader split `validation`; all 750 requested letters,
  including `row_ok=False`. No holdout or real-patient data was loaded.
- Candidate: `one_shot_frequency_v2_measurements_r5`, condition `r5_rich`.
- Runtime: DeepSeek V4.1 Flash (`deepseek-flash`), thinking enabled/low, temperature 0,
  24,000-token limit. Original timeout 300 seconds; 40 separate timeout reruns at
  600 seconds. The mixed view counts each letter once, not both attempts.
- Population used for field statistics: **746 schema-valid letters and 2,355 findings**.
  This includes 706 original responses and 40 rerun responses. There are 719 letters
  with findings and 27 valid empty inventories. Findings per valid letter: mean
  3.16, median 3, range 0–14. One finding per letter would not cover this output.
- Exclusions remain explicit: 2 invalid envelopes and 2 invalid schemas. Both schema
  failures are `event.grouping` enum errors (source rows 6029 and 13122). Envelope
  failures are rows 4624 and 13267. Excluded contents are not repaired or silently
  added to the field statistics. Valid output usage can therefore understate failure-prone fields.
- Scorer: none for this descriptive audit. Schema validity is independent of native
  answer-label validity or Purist/Pragmatic agreement; no benchmark score is inferred.
- Evidence checks: 2,352/2,355 finding quotations are exact source substrings. The
  three exceptions are row 3532/f1 and row 6571/f2 and f3. They remain counted as
  schema-valid output; exact quotation matching is not a correctness review.
- Join checks: unique request IDs and source rows; exactly 750 R5 requests; exactly
  40 originally timed-out R5 replacements; mixed-view bodies equal the corresponding
  original or rerun response. No duplicate findings after removing only finding ID;
  22 findings share evidence with another finding in the same letter, which can be legitimate.
- Source paths and SHA-256 hashes, runtime parameters and excluded-record details
  are in [summary.json](summary.json). Detailed fields are in [attributes.json](attributes.json).
  The authoritative input is saved requests/responses under
  `runs/one_shot_thinking_r4_r5_r6/dev750/`, including `timeout600/`.
- Reproduce from the repository root with
  `.venv/bin/python scripts/benchmarks/profile_r5_measurements.py`.
  [Notebook](profile.ipynb) runs that same code and displays the main results.
  The source-ID-preserving working table remains local under
  `runs/one_shot_thinking_r4_r5_r6/dev750/r5_schema_profile/`.

## Measurement-type counts

Finding shares use 2,355; letter coverage uses 746 schema-valid letters. Letter
counts overlap across measurement types. “Selected” means linked by the model to
its declared answer, not judged correct or necessary by a reviewer.

| Measurement | Findings (% of all) | Letters (% of valid) | Selected (% of type) | Observation period (% of type) | Condition (% of type) |
| --- | --- | --- | --- | --- | --- |
"""
    ]
    for row in summary["by_kind"]:
        n = row["findings"]
        sections.append(
            "| "
            + " | ".join(
                [
                    row["kind"],
                    pct(n, 2355),
                    pct(row["letters"], 746),
                    pct(row["selected"], n),
                    pct(row["observation_period"], n),
                    pct(row["condition"], n),
                ]
            )
            + " |\n"
        )
    sections.append("""
## Quantity variants and date attributes

There are 2,190 quantity objects across counts, cluster counts/sizes and durations:
1,832 exact (83.7%), 184 ranges (8.4%), 63 bounds (2.9%) and 111 qualitative (5.1%).
Approximation is true in 155/2,079 numeric quantities (7.5%). These flags and variants
have observed use; replacing them all with a single number would lose information.
Occurrence counts are not finding counts: one finding may contain several quantities.

There are 637 time points: 378 month, 112 day, 110 unspecified, 27 year and 10 week
precision. Observation periods contain 321 starts, 52 ends and 453 durations among
972 populated period objects. The small end-date count does not make start and end
interchangeable. The schema has no dedicated letter-date field, so zero letter-date
attributes is a schema limitation rather than evidence that letters lack dates.

R7-only compound ranges and `observed_cluster_count` cannot be assessed from R5
outputs: R5 cannot emit them. Their absence here is not evidence against those additions.

## Cluster and seizure-free combinations

| Cluster fields | Findings / 277 |
| --- | --- |
| Neither cadence nor size | 130 (46.9%) |
| Cadence and size | 74 (26.7%) |
| Size only | 59 (21.3%) |
| Cadence only | 14 (5.1%) |

| Seizure-free fields | Findings / 543 |
| --- | --- |
| Neither duration nor since | 237 (43.6%) |
| Since only | 158 (29.1%) |
| Duration only | 130 (23.9%) |
| Duration and since | 18 (3.3%) |

## Every attribute: how to read the tables

**Eligible** means its containing object/variant was emitted. **Populated** excludes
explicit nulls; a missing parent does not create null child fields. For example,
`observation_period.end` has denominator 972, not 2,355. Angle-bracket names such as
`count<range>` denote schema variants, not literal JSON keys. Allowed enum values
with zero use are retained. Rows with 0/0 mark variants never emitted, not failed fields.

Numeric summaries describe raw emitted numbers, with no unit normalization. Consult
the adjacent unit distribution before comparing duration numbers. Numeric means across
units are only a mechanical profile, not a meaningful clinical duration. Text rows show
distinct counts and up to three most common exact strings (long previews truncated to
75 characters); the JSON retains the five leading complete values. Distinctness is
case- and punctuation-sensitive. Top strings are illustrative, not source-reviewed labels.

""")
    for group in ["documents", "all_findings"] + KINDS:
        sections.append(f"### {group}\n\n")
        if group == "documents":
            sections.append(
                "Answer object fields below use 746 records. Finding-list lengths: mean 3.16, median 3, min 0, max 14; selected-ID-list lengths: mean 1.47, median 1, min 0, max 12. There are 500 singleton selections, 219 multiple selections and 27 empty selections. All selected IDs resolve within their record by schema validation.\n\n"
            )
        sections.append(
            "| Attribute | Populated / eligible | Null | Values / numeric summary |\n| --- | --- | --- | --- |\n"
        )
        for row in profile:
            if row["group"] == group:
                sections.append(
                    f"| `{row['path']}` | {pct(row['populated'], row['eligible'])} | {row['null']} | {details(row)} |\n"
                )
        sections.append("\n")
    sections.append("""## Limits of the simplification decision

These statistics describe one model, prompt and synthetic development distribution.
Required fields naturally have 100% population in schema-valid records; that does not
prove utility. Sparse fields may reflect omitted extraction. Identical evidence can
support distinct claims, and unselected findings matter for the planned complete
inventory. No field-ablation experiment, token-saving calculation or clinical review
was performed. Recommendations are candidates for review, not adopted schema rules.
""")
    (OUT / "README.md").write_text("".join(sections))


if __name__ == "__main__":
    main()
