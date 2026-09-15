"""Deterministic review-group helper; separates membership from model comparison."""

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def make_member(
    sid: str,
    sha: str,
    fid: str | None = None,
    iid: str | None = None,
    cand_idx: int | None = None,
    quote: str = "",
) -> dict[str, Any]:
    if fid is not None:
        mid = f"{sid}/{fid}"
    elif iid is not None:
        mid = f"{sid}/{iid}"
    elif cand_idx is not None:
        mid = f"{sid}/candidate{cand_idx:03d}"
    else:
        mid, quote = f"{sid}/source", ""
    return {
        "member_id": mid,
        "source_id": sid,
        "finding_id": fid,
        "issue_id": iid,
        "candidate_quote": quote,
        "source_sha256": sha,
    }


def make_group(
    check_id: str,
    group_id: str,
    rule: str,
    members: list[dict[str, Any]],
    review_state: str = "pending",
    scope: str = "sources",
    semantic_review: str | None = None,
) -> dict[str, Any]:
    uniq = {m["member_id"]: m for m in members}
    grp: dict[str, Any] = {
        "check_id": check_id,
        "group_id": group_id,
        "selection_rule": rule,
        "members": list(uniq.values()),
        "comparisons": [],
        "review_state": review_state,
        "scope": scope,
    }
    if semantic_review is not None:
        grp["semantic_review"] = semantic_review
    return grp


def load_sources_file(path: Path, expected: int | None = None) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"Sources file not found: {path}")
    sources: dict[str, dict[str, Any]] = {}
    seen_indices: set[int] = set()
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        sid, text, decl_sha = r.get("source_id"), r.get("note_text"), r.get("source_sha256")
        if not sid or text is None or not decl_sha:
            raise ValueError(f"Source row {line_no} missing source_id, note_text, or source_sha256")
        if sid in sources:
            raise ValueError(f"Duplicate source_id in sources: {sid}")
        index = r.get("source_row_index")
        if not isinstance(index, int) or isinstance(index, bool) or index in seen_indices:
            raise ValueError(f"Missing, invalid or duplicate source_row_index for {sid}")
        seen_indices.add(index)
        calc_sha = sha256_text(text)
        if calc_sha != decl_sha:
            raise ValueError(f"Hash mismatch for {sid}: calc {calc_sha} != declared {decl_sha}")
        sources[sid] = r
    if expected is not None and len(sources) != expected:
        raise ValueError(f"Expected {expected} sources, found {len(sources)}")
    return dict(sorted(sources.items(), key=lambda item: (item[1]["source_row_index"], item[0])))


def load_annotations_file(
    path: Path,
    sources: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"Annotations file not found: {path}")
    annotations: dict[str, dict[str, Any]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        sid, decl_sha = r.get("source_id"), r.get("source_sha256")
        if not sid or sid in annotations:
            raise ValueError(f"Annotation row {line_no} invalid or duplicate source_id: {sid}")
        if sid not in sources:
            raise ValueError(f"Annotation for unknown source_id: {sid}")
        if decl_sha != sources[sid]["source_sha256"]:
            raise ValueError(f"Annotation source_sha256 mismatch for {sid}")
        if r.get("source_row_index") != sources[sid]["source_row_index"]:
            raise ValueError(f"Annotation source_row_index mismatch for {sid}")
        note, fids = sources[sid]["note_text"], set()
        for f in r.get("findings", []):
            fid, ev = f.get("id"), f.get("evidence", "")
            if not fid:
                raise ValueError(f"Finding missing id in source {sid}")
            if fid in fids:
                raise ValueError(f"Duplicate finding id {fid} in source {sid}")
            fids.add(fid)
            if f.get("measurement", {}).get("type") not in {
                "rate",
                "count",
                "cluster",
                "qualitative",
                "seizure_free",
                "last_seizure",
            }:
                raise ValueError(f"Unknown measurement type for {sid}/{fid}")
            if not ev or ev not in note:
                raise ValueError(f"Finding evidence not exact slice in source {sid}: {ev!r}")
        for ctx in r.get("finding_context", []):
            for m in ctx.get("mentions", []):
                if m and m not in note:
                    raise ValueError(f"Finding context mention not in source {sid}: {m!r}")
        for c in r.get("source_checks", []):
            ev = c.get("evidence", "")
            if not ev or ev not in note:
                raise ValueError(f"Source check evidence not in source {sid}: {ev!r}")
        for iss in r.get("issues", []):
            ev = iss.get("evidence", "")
            if ev and ev not in note:
                raise ValueError(f"Issue evidence not in source {sid}: {ev!r}")
        annotations[sid] = r
    missing = set(sources.keys()) - set(annotations.keys())
    if missing:
        raise ValueError(f"Missing annotations for sources: {sorted(missing)}")
    return annotations


def load_candidates_file(
    path: Path | None,
    sources: dict[str, dict[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    candidates: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    if not path:
        return candidates
    if not path.is_file():
        raise ValueError(f"Candidates file not found: {path}")
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        r = json.loads(line)
        sid = r.get("source_id")
        if not sid or sid not in sources:
            raise ValueError(f"Candidate at line {line_no} references invalid source_id {sid}")
        note = sources[sid]["note_text"]
        if "candidate_quotes" in r or "quotes" in r:
            quote_list = r.get("candidate_quotes", r.get("quotes"))
            if not isinstance(quote_list, list):
                raise ValueError(f"Candidate list at line {line_no} must be an array")
        else:
            quote_list = [r[k] for k in ["candidate_quote", "evidence", "quote"] if k in r][:1]
            if not quote_list:
                raise ValueError(f"Candidate at line {line_no} contains no quote field")
        for q in quote_list:
            if not q or q not in note:
                raise ValueError(f"Candidate quote not an exact slice in source {sid}: {q!r}")
            candidates[sid].append({"quote": q, "finding_ids": r.get("finding_ids", [])})
    return candidates


def load_patterns(pattern_arg: str | None) -> list[dict[str, Any]]:
    if not pattern_arg:
        return []
    p_path = Path(pattern_arg)
    data = json.loads(p_path.read_text(encoding="utf-8") if p_path.is_file() else pattern_arg)
    if not isinstance(data, list):
        raise ValueError("Correction patterns must be a JSON list")
    seen_pattern_ids: set[str] = set()
    for idx, item in enumerate(data, 1):
        if not isinstance(item, dict) or "regex" not in item:
            raise ValueError(f"Pattern item {idx} missing regex field")
        pattern_id = item.get("id") or f"pattern-{idx:02d}"
        if pattern_id in seen_pattern_ids:
            raise ValueError(f"Duplicate correction pattern ID: {pattern_id}")
        seen_pattern_ids.add(pattern_id)
        try:
            re.compile(item["regex"])
        except re.error as exc:
            msg = f"Correction regex failed to compile ({item['regex']}): {exc}"
            raise ValueError(msg) from exc
    return data


def build_review_groups(
    sources_path: Path,
    annotations_path: Path,
    candidates_path: Path | None,
    all_sources_path: Path | None,
    patterns_arg: str | None,
    out_dir: Path,
    expected: int = 750,
) -> dict[str, Any]:
    sources = load_sources_file(sources_path, expected=expected)
    all_sources = load_sources_file(all_sources_path) if all_sources_path else None
    if all_sources is not None:
        for sid, source in sources.items():
            if (
                sid not in all_sources
                or all_sources[sid]["source_sha256"] != source["source_sha256"]
                or all_sources[sid]["source_row_index"] != source["source_row_index"]
            ):
                raise ValueError(f"Full-source input is not a matching superset for {sid}")
    annotations = load_annotations_file(annotations_path, sources)
    candidates_by_source = load_candidates_file(candidates_path, sources)
    patterns = load_patterns(patterns_arg)

    cand_registry: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    cand_quote_map: dict[str, dict[str, int]] = collections.defaultdict(dict)

    def register_candidate(sid: str, quote: str, fids: list[str] | None = None) -> int:
        if quote in cand_quote_map[sid]:
            idx = cand_quote_map[sid][quote]
            if fids and not cand_registry[sid][idx - 1]["finding_ids"]:
                cand_registry[sid][idx - 1]["finding_ids"] = list(fids)
            return idx
        idx = len(cand_registry[sid]) + 1
        cand_quote_map[sid][quote] = idx
        cand_registry[sid].append(
            {"cand_idx": idx, "quote": quote, "finding_ids": list(fids or [])}
        )
        return idx

    for sid, c_list in candidates_by_source.items():
        for c in c_list:
            register_candidate(sid, c["quote"], c.get("finding_ids"))
    for sid, r in annotations.items():
        for chk in r.get("source_checks", []):
            if chk.get("evidence"):
                register_candidate(sid, chk["evidence"], chk.get("finding_ids"))

    # A raw-text backstop is independent of the annotation/candidate inventories.
    # Segmentation is only a search aid; full sources remain the review authority.
    source_backstop = re.compile(
        r"\b(per|every|daily|weekly|monthly|past|since|cluster\w*|last|none|free|"
        r"unknown|seizures?|convulsions?|absences?|spells?|episodes?|events?|"
        r"occasional\w*|rare\w*|infrequent|mornings?|days?)\b|not documented",
        re.I,
    )
    for sid, source in sources.items():
        for span in re.split(r"(?<=[.!?])\s+|\n+", source["note_text"]):
            quote = span.strip()
            if quote and source_backstop.search(quote):
                register_candidate(sid, quote)

    groups: list[dict[str, Any]] = []

    # C01 Manifest coverage
    c01_members = [make_member(s, sources[s]["source_sha256"]) for s in sources]
    c01_rule = (
        f"Manifest coverage: all {len(sources)} source IDs verified against expected ({expected})"
    )
    groups.append(
        make_group("C01", "C01-coverage", c01_rule, c01_members, scope=f"coverage_{len(sources)}")
    )

    # C02 Repeated wording
    exact_q, norm_q, hash_q = (
        collections.defaultdict(list),
        collections.defaultdict(list),
        collections.defaultdict(list),
    )
    for sid, s in sources.items():
        hash_q[s["source_sha256"]].append(make_member(sid, s["source_sha256"]))
    for sid, c_list in cand_registry.items():
        src_dict = all_sources if (all_sources and sid in all_sources) else sources
        sha = src_dict[sid]["source_sha256"] if sid in src_dict else ""
        for c in c_list:
            m = make_member(sid, sha, cand_idx=c["cand_idx"], quote=c["quote"])
            exact_q[c["quote"]].append(m)
            norm_k = re.sub(r"\b\d+(?:[.,]\d+)?\b", "#", " ".join(c["quote"].lower().split()))
            norm_q[norm_k].append(m)

    for mode, mapping in [
        ("identical_source", hash_q),
        ("exact_candidate", exact_q),
        ("normal_candidate", norm_q),
    ]:
        matches = [(k, v) for k, v in mapping.items() if len({m["source_id"] for m in v}) > 1]
        if not matches:
            groups.append(
                make_group("C02", f"C02-{mode}-none", f"{mode}: no cross-source matches", [])
            )
        else:
            for idx, (k, v) in enumerate(matches, 1):
                groups.append(make_group("C02", f"C02-{mode}-{idx:03d}", f"{mode}: {k}", v))

    # C03 Measurement decisions
    measurements: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for sid, r in annotations.items():
        sha = sources[sid]["source_sha256"]
        for f in r.get("findings", []):
            m = make_member(sid, sha, fid=f["id"], quote=f["evidence"])
            measurements[f.get("measurement", {}).get("type", "unknown")].append(m)
    for t in ["rate", "count", "cluster", "qualitative", "seizure_free", "last_seizure"]:
        groups.append(
            make_group(
                "C03",
                f"C03-{t}",
                f"Every finding whose actual measurement.type equals {t}",
                measurements[t],
            )
        )

    backstop = re.compile(
        r"\b(per|every|daily|weekly|monthly|in|past|since|on|cluster\w*|"
        r"last|none|free|unknown)\b|not documented",
        re.I,
    )
    missing = [
        make_member(sid, sources[sid]["source_sha256"], cand_idx=c["cand_idx"], quote=c["quote"])
        for sid, c_list in cand_registry.items()
        if sid in sources
        for c in c_list
        if not c["finding_ids"] and backstop.search(c["quote"])
    ]
    c03_miss_rule = "Source-read candidates containing lexical backstop terms with no finding link"
    groups.append(make_group("C03", "C03-candidates-without-findings", c03_miss_rule, missing))

    # C04 Quantities and units
    c04_members: list[dict[str, Any]] = []
    for sid, r in annotations.items():
        sha = sources[sid]["source_sha256"]
        for f in r.get("findings", []):
            dumped = json.dumps(f.get("measurement", {}))
            if any(
                x in dumped for x in ["bound", "range", "approximate", "qualitative"]
            ) or re.search(r"\bseizure[ -]days?\b", f.get("evidence", ""), re.I):
                c04_members.append(make_member(sid, sha, fid=f["id"], quote=f["evidence"]))
    for sid, c_list in cand_registry.items():
        if sid in sources and any(
            re.search(r"\bseizure[ -]days?\b", c["quote"], re.I) for c in c_list
        ):
            for c in c_list:
                if re.search(r"\bseizure[ -]days?\b", c["quote"], re.I):
                    c04_members.append(
                        make_member(
                            sid,
                            sources[sid]["source_sha256"],
                            cand_idx=c["cand_idx"],
                            quote=c["quote"],
                        )
                    )
    groups.append(
        make_group(
            "C04",
            "C04-quantities",
            "Every bound/range/approximate/qualitative measurement and seizure-day candidate",
            c04_members,
        )
    )

    # C05 Event and time
    eventtime: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for sid, r in annotations.items():
        sha = sources[sid]["source_sha256"]
        for f in r.get("findings", []):
            st, sc, tm = (
                f.get("event", {}).get("seizure_status", "unspecified"),
                f.get("event", {}).get("scope", "unspecified"),
                f.get("timing", "unclear"),
            )
            eventtime[f"{st}-{sc}-{tm}"].append(
                make_member(sid, sha, fid=f["id"], quote=f["evidence"])
            )
    for k in sorted(eventtime.keys()):
        groups.append(
            make_group(
                "C05", f"C05-{k}", f"Every finding with status-scope-timing {k}", eventtime[k]
            )
        )
    omitted = [
        make_member(sid, sources[sid]["source_sha256"], cand_idx=c["cand_idx"], quote=c["quote"])
        for sid, c_list in cand_registry.items()
        if sid in sources
        for c in c_list
        if not c["finding_ids"]
    ]
    groups.append(
        make_group(
            "C05",
            "C05-potential-omissions",
            "Source candidates omitting status/scope/timing concepts as potential omissions",
            omitted,
        )
    )

    # C06 Identity and evidence
    relations, latest_freedom = [], []
    for sid, r in annotations.items():
        sha = sources[sid]["source_sha256"]
        ctx_map = {c.get("finding_id"): c for c in r.get("finding_context", [])}
        types = {f.get("measurement", {}).get("type") for f in r.get("findings", [])}
        has_lf = "last_seizure" in types and "seizure_free" in types
        for f in r.get("findings", []):
            m = make_member(sid, sha, fid=f["id"], quote=f["evidence"])
            ctx = ctx_map.get(f["id"], {})
            if len(ctx.get("mentions", [])) > 1 or ctx.get("relations"):
                relations.append(m)
            if has_lf:
                latest_freedom.append(m)
    groups.append(
        make_group(
            "C06",
            "C06-mentions-and-relations",
            "Every finding with multiple mentions or any relation",
            relations,
        )
    )
    groups.append(
        make_group(
            "C06",
            "C06-latest-plus-freedom",
            "Findings exhibiting both latest event and seizure freedom assertions",
            latest_freedom,
        )
    )

    # C07 Empty and unusual records, including nested representation enums.
    unusual: list[dict[str, Any]] = []
    enums: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    enum_keys = {
        "type",
        "scope",
        "seizure_status",
        "timing",
        "unit",
        "form",
        "role",
        "disposition",
        "kind",
        "relation",
        "annotation_state",
    }

    def collect_enums(value: Any, path: str, member: dict[str, Any]) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                location = f"{path}.{key}"
                if (
                    key in enum_keys
                    and isinstance(child, str)
                    and not location.endswith("event.type")
                ):
                    enums[(location, child)].append(member)
                elif isinstance(child, (dict, list)):
                    collect_enums(child, location, member)
        elif isinstance(value, list):
            for child in value:
                collect_enums(child, path + "[]", member)

    for sid, r in annotations.items():
        sha = sources[sid]["source_sha256"]
        source_member = make_member(sid, sha)
        for iss in r.get("issues", []):
            unusual.append(make_member(sid, sha, iid=iss["id"], quote=iss.get("evidence", "")))
        if not r.get("findings"):
            unusual.append(source_member)
        for key in ("annotation_state", "document_dates", "source_checks"):
            collect_enums({key: r.get(key)}, "record", source_member)
        for f in r.get("findings", []):
            m = make_member(sid, sha, fid=f["id"], quote=f["evidence"])
            collect_enums(f, "finding", m)
        for context in r.get("finding_context", []):
            fid = context["finding_id"]
            finding = next(f for f in r["findings"] if f["id"] == fid)
            m = make_member(sid, sha, fid=fid, quote=finding["evidence"])
            collect_enums(context.get("relations", []), "context.relations", m)
    for members in enums.values():
        if len(members) == 1:
            unusual.extend(members)
    counts = {sid: len(r.get("findings", [])) for sid, r in annotations.items()}
    if counts:
        extreme = {min(counts.values()), max(counts.values())}
        for sid, count in counts.items():
            if count in extreme:
                unusual.append(make_member(sid, sources[sid]["source_sha256"]))
    batches = {
        s.get("batch") or s.get("batch_id")
        for s in sources.values()
        if s.get("batch") or s.get("batch_id")
    }
    batch_dist = (
        {
            b: sum(1 for s in sources.values() if (s.get("batch") or s.get("batch_id")) == b)
            for b in batches
        }
        if batches
        else "unavailable"
    )
    c07_rule = (
        "All issues, empty records, enum values occurring once, "
        f"min/max finding counts; batch distribution: {batch_dist}"
    )
    groups.append(make_group("C07", "C07-unusual", c07_rule, unusual))

    # C08 Correction propagation
    c08_sources = all_sources if all_sources is not None else sources
    c08_scope_name = "all_sources" if all_sources is not None else "sources"
    if not patterns:
        groups.append(
            make_group(
                "C08",
                "C08-pending",
                "Missing correction patterns; C08 pending, not reviewed",
                [],
                scope=c08_scope_name,
                semantic_review="PENDING",
            )
        )
    else:
        for idx, pat in enumerate(patterns, 1):
            pid, rx = pat.get("id") or f"pattern-{idx:02d}", re.compile(pat["regex"])
            p_members: list[dict[str, Any]] = []
            for sid, s in c08_sources.items():
                sha, text = s["source_sha256"], s["note_text"]
                for mt in rx.finditer(text):
                    snippet = text[max(0, mt.start() - 120) : min(len(text), mt.end() + 160)]
                    c_idx = register_candidate(sid, snippet)
                    p_members.append(make_member(sid, sha, cand_idx=c_idx, quote=snippet))
            c08_rule = f"Correction regex: {pat['regex']}; rule_ids: {pat.get('rule_ids', [])}"
            groups.append(
                make_group(
                    "C08",
                    f"C08-{pid}",
                    c08_rule,
                    p_members,
                    scope=c08_scope_name,
                    semantic_review="PENDING",
                )
            )

    if (out_dir / "groups.jsonl").exists() or (out_dir / "summary.json").exists():
        raise ValueError("Use a new output directory; preserve existing review membership")
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "groups.jsonl").write_text(
        "".join(json.dumps(g, ensure_ascii=False) + "\n" for g in groups), encoding="utf-8"
    )

    tool_sha = hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()
    c08_groups = [g for g in groups if g["check_id"] == "C08"]
    summary = {
        "tool_source_sha256": tool_sha,
        "input_hashes": {
            "sources_sha256": sha256_file(sources_path),
            "annotations_sha256": sha256_file(annotations_path),
            "candidates_sha256": sha256_file(candidates_path) if candidates_path else None,
            "all_sources_sha256": sha256_file(all_sources_path) if all_sources_path else None,
            "correction_patterns_sha256": sha256_file(Path(patterns_arg))
            if (patterns_arg and Path(patterns_arg).is_file())
            else None,
        },
        "expected_sources": expected,
        "sources_count": len(sources),
        "groups_count": len(groups),
        "memberships_count": sum(len(g["members"]) for g in groups),
        "checked": 0,
        "pending": len(groups),
        "semantic_review_state": "pending",
        "c08_source_count": len(c08_sources),
        "c08_groups_count": len(c08_groups),
        "c08_memberships_count": sum(len(g["members"]) for g in c08_groups),
        "scope": "Membership generation only; no semantic review",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Deterministic review group generator")
    parser.add_argument("--sources", required=True, type=Path, help="Path to sources JSONL")
    parser.add_argument("--annotations", required=True, type=Path, help="Path to annotations JSONL")
    parser.add_argument(
        "--candidates", type=Path, default=None, help="Optional independent candidate JSONL"
    )
    parser.add_argument(
        "--all-sources", type=Path, default=None, help="Optional full sources JSONL for C08"
    )
    parser.add_argument(
        "--correction-patterns", default=None, help="Optional JSON list or file path"
    )
    parser.add_argument("--out", required=True, type=Path, help="Output directory")
    parser.add_argument(
        "--expected", type=int, default=750, help="Expected source count (default 750)"
    )
    args = parser.parse_args()

    try:
        summary = build_review_groups(
            sources_path=args.sources,
            annotations_path=args.annotations,
            candidates_path=args.candidates,
            all_sources_path=args.all_sources,
            patterns_arg=args.correction_patterns,
            out_dir=args.out,
            expected=args.expected,
        )
        print(json.dumps(summary, indent=2))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
