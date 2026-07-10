"""One-off corpus audit (2026-07-09): re-check every SeizureFrequency mention's
gold TimePeriod/NumberOfTimePeriods against the letter text, to see whether the
EA0079 gold error (TimePeriod/NumberOfTimePeriods coded with no textual basis --
see experiments/gold_data_issues.jsonl) was an isolated mistake or a missed
pattern. Only trusts actual rate-marker phrases ("per X", "every X", "a X") as
textual support -- a bare time word elsewhere in the sentence (e.g. "stable
over the last few years ... per month") is not treated as confirming evidence.

Result: EA0079 is the only genuine instance across all 263 mentions. One
superficially similar row (EA0134 T17, NumberOfSeizures=0, "last seizure was 2
years ago") is not an error -- it's a corpus-wide convention (33 instances)
where NumberOfSeizures=0 + TimePeriod/NumberOfTimePeriods encodes seizure-free
duration since the last event, which is textually grounded.

Also surfaced EA0169's TimePeriod="days" (lowercase/plural) -- a schema-format
quirk, not a content error, already known (docs/research/
exectv2_data_discoveries_log.md D14) but not wired into scoring normalization
until this audit prompted the fix in scoring/normalize.py.
"""

import glob
import json
import os
import re

DATA_DIR = r"data/ExECTv2 (2025)/Gold1-200_corrected_spelling"

TIME_WORDS = {
    "day": "Day", "days": "Day", "daily": "Day",
    "week": "Week", "weeks": "Week", "weekly": "Week", "fortnight": "Week", "fortnightly": "Week",
    "month": "Month", "months": "Month", "monthly": "Month",
    "year": "Year", "years": "Year", "yearly": "Year", "annually": "Year", "annum": "Year",
}

NUM_WORDS = {
    "a": 1, "one": 1, "single": 1, "two": 2, "couple": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "twice": 2, "thrice": 3,
}


def parse_ann(path):
    entities = {}
    attrs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                continue
            parts = line.split("\t")
            tag = parts[0]
            if tag.startswith("T"):
                fields = parts[1].split(" ")
                entities[tag] = {
                    "id": tag,
                    "type": fields[0],
                    "start": int(fields[1]),
                    "end": int(fields[2]),
                    "mention_text": parts[2] if len(parts) > 2 else "",
                }
            elif tag.startswith("A"):
                fields = parts[1].split(" ")
                aname, target, aval = fields[0], fields[1], " ".join(fields[2:])
                attrs.setdefault(target, {})[aname] = aval
    return entities, attrs


SENT_BOUNDARY = re.compile(r"(?<=[.!?])\s+|\n+|\t+")


def extract_window(text, start, end, radius=120):
    lo = max(0, start - radius)
    hi = min(len(text), end + radius)
    return text[lo:hi], lo


def extract_sentence_window(text, start, end):
    """Restrict to the sentence(s) overlapping [start,end), using . ! ? or newline/tab
    as boundaries (clinic letters use tabs/newlines heavily as pseudo-sentence breaks)."""
    bounds = [0]
    for m in SENT_BOUNDARY.finditer(text):
        bounds.append(m.end())
    bounds.append(len(text))
    bounds = sorted(set(bounds))
    lo, hi = 0, len(text)
    for i in range(len(bounds) - 1):
        seg_lo, seg_hi = bounds[i], bounds[i + 1]
        if seg_lo <= start < seg_hi or seg_lo < end <= seg_hi:
            lo, hi = seg_lo, seg_hi
            break
    return text[lo:hi], lo


def find_time_cues(window_text):
    cues = []
    for m in re.finditer(r"\b([a-zA-Z]+)\b", window_text):
        w = m.group(1).lower()
        if w in TIME_WORDS:
            cues.append((m.start(), w, TIME_WORDS[w]))
    return cues


# Explicit multiplier phrase: "every N months", "per N years", "each N weeks" etc.
# Only THIS pattern reliably encodes NumberOfTimePeriods > 1; a bare nearby number
# (e.g. seizure-count "2-4 seizures per month") is NOT the period multiplier.
MULTIPLIER_RE = re.compile(
    r"\b(?:every|per|each)\s+(?:(\d+)|(" + "|".join(NUM_WORDS.keys()) + r"))\s+"
    r"(day|days|daily|week|weeks|weekly|fortnight|fortnightly|month|months|monthly|year|years|yearly|annually|annum)\b",
    re.IGNORECASE,
)

# A time-unit only counts as a periodicity CUE if it's actually functioning as a rate
# marker ("per month", "every 2 years", "a week", "each fortnight", "twice a year") --
# not a bare occurrence like "over the last few years" or "two years ago".
RATE_MARKER_RE = re.compile(
    r"\b(?:per|every|each|a)\s+(?:\d+\s+)?"
    r"(day|days|daily|week|weeks|weekly|fortnight|fortnightly|month|months|monthly|year|years|yearly|annually|annum)\b",
    re.IGNORECASE,
)


def find_rate_cues(window_text):
    cues = []
    for m in RATE_MARKER_RE.finditer(window_text):
        unit = m.group(1).lower()
        cues.append((m.start(), unit, TIME_WORDS[unit]))
    return cues


def find_explicit_multiplier(sentence_text):
    """Return (num, TimePeriod) for an explicit 'every/per/each N <unit>' phrase, else None."""
    m = MULTIPLIER_RE.search(sentence_text)
    if not m:
        return None
    num_digit, num_word, unit = m.groups()
    num = int(num_digit) if num_digit else NUM_WORDS.get(num_word.lower())
    period = TIME_WORDS.get(unit.lower())
    if num is None or period is None:
        return None
    return num, period


def audit_letter(letter_id):
    ann_path = os.path.join(DATA_DIR, f"{letter_id}.ann")
    txt_path = os.path.join(DATA_DIR, f"{letter_id}.txt")
    entities, attrs = parse_ann(ann_path)
    with open(txt_path, encoding="utf-8") as f:
        text = f.read()

    findings = []
    for tid, ent in entities.items():
        if ent["type"] != "SeizureFrequency":
            continue
        a = attrs.get(tid, {})
        gold_tp = a.get("TimePeriod")
        gold_ntp = a.get("NumberOfTimePeriods")
        if not gold_tp:
            continue
        window, lo = extract_sentence_window(text, ent["start"], ent["end"])
        if len(window) < 20:
            window, lo = extract_window(text, ent["start"], ent["end"], radius=150)

        norm_map = {"day": "Day", "week": "Week", "month": "Month", "year": "Year"}
        gold_tp_key = norm_map.get(gold_tp.rstrip("s").lower(), gold_tp)
        if gold_tp != gold_tp_key:
            findings.append({
                "letter_id": letter_id, "mention_id": tid,
                "span": ent["mention_text"], "offsets": [ent["start"], ent["end"]],
                "gold_TimePeriod": gold_tp, "gold_NumberOfTimePeriods": gold_ntp,
                "issue": "schema_case_inconsistency",
                "window": window.replace("\n", " "),
            })

        rate_cues = find_rate_cues(window)
        if not rate_cues:
            bare_cues = find_time_cues(window)
            findings.append({
                "letter_id": letter_id, "mention_id": tid,
                "span": ent["mention_text"], "offsets": [ent["start"], ent["end"]],
                "gold_TimePeriod": gold_tp, "gold_NumberOfTimePeriods": gold_ntp,
                "issue": "no_rate_marker_in_sentence",
                "bare_time_words_present": sorted({c[2] for c in bare_cues}),
                "window": window.replace("\n", " "),
            })
            continue

        matching_cues = [c for c in rate_cues if c[2] == gold_tp_key]
        if not matching_cues:
            findings.append({
                "letter_id": letter_id, "mention_id": tid,
                "span": ent["mention_text"], "offsets": [ent["start"], ent["end"]],
                "gold_TimePeriod": gold_tp, "gold_NumberOfTimePeriods": gold_ntp,
                "rate_markers_found": sorted({c[2] for c in rate_cues}),
                "issue": "time_period_mismatch",
                "window": window.replace("\n", " "),
            })
            continue

        # TimePeriod unit has textual support somewhere in-sentence. Now check
        # NumberOfTimePeriods only against an EXPLICIT "every/per/each N <unit>" phrase
        # (a bare nearby number is usually the seizure-count, not the period multiplier).
        if gold_ntp is not None:
            try:
                gold_ntp_int = int(gold_ntp)
            except ValueError:
                gold_ntp_int = None
            mult = find_explicit_multiplier(window)
            if mult is not None and gold_ntp_int is not None:
                mult_num, mult_period = mult
                if mult_period == gold_tp_key and mult_num != gold_ntp_int:
                    findings.append({
                        "letter_id": letter_id, "mention_id": tid,
                        "span": ent["mention_text"], "offsets": [ent["start"], ent["end"]],
                        "gold_TimePeriod": gold_tp, "gold_NumberOfTimePeriods": gold_ntp,
                        "explicit_multiplier_found": mult_num,
                        "issue": "number_of_time_periods_mismatch",
                        "window": window.replace("\n", " "),
                    })
    return findings


def audit_prescription_drugname(letter_id):
    """The other logged error class (EA0146): DrugName sharing no substring
    with CUIPhrase/span text. Most hits are legitimate brand->generic
    resolutions (Epilim->Sodium Valproate etc); flags for manual triage."""
    ann_path = os.path.join(DATA_DIR, f"{letter_id}.ann")
    entities, attrs = parse_ann(ann_path)

    def norm(s):
        return re.sub(r"[^a-z]", "", (s or "").lower())

    flags = []
    for tid, ent in entities.items():
        if ent["type"] != "Prescription":
            continue
        a = attrs.get(tid, {})
        drugname, cuiphrase = a.get("DrugName"), a.get("CUIPhrase")
        if not drugname or not cuiphrase:
            continue
        dn, cp, sp = norm(drugname), norm(cuiphrase), norm(ent["mention_text"])
        if (
            dn not in cp and cp not in dn
            and dn not in sp and sp not in dn
            and dn[:4] not in cp and cp[:4] not in dn
        ):
            flags.append((letter_id, tid, drugname, cuiphrase, ent["mention_text"]))
    return flags


def main():
    all_findings = []
    for ann_path in sorted(glob.glob(os.path.join(DATA_DIR, "*.ann"))):
        letter_id = os.path.splitext(os.path.basename(ann_path))[0]
        all_findings.extend(audit_letter(letter_id))

    by_issue = {}
    for f in all_findings:
        by_issue.setdefault(f["issue"], []).append(f)

    print(f"Total SF mentions flagged: {len(all_findings)}")
    for k, v in by_issue.items():
        print(f"  {k}: {len(v)}")
    print()
    print("=== TimePeriod word mismatch (no textual support for the gold unit in-sentence) ===")
    for f in by_issue.get("time_period_mismatch", []):
        print(json.dumps(f, indent=None))
    print()
    print("=== Explicit-multiplier NumberOfTimePeriods mismatch ===")
    for f in by_issue.get("number_of_time_periods_mismatch", []):
        print(json.dumps(f, indent=None))
    print()
    print("=== Schema case inconsistency (e.g. 'days' instead of 'Day') ===")
    for f in by_issue.get("schema_case_inconsistency", []):
        print(json.dumps(f, indent=None))

    print()
    print("=== Prescription DrugName/CUIPhrase divergence (EA0146 pattern) ===")
    all_rx_flags = []
    for ann_path in sorted(glob.glob(os.path.join(DATA_DIR, "*.ann"))):
        letter_id = os.path.splitext(os.path.basename(ann_path))[0]
        all_rx_flags.extend(audit_prescription_drugname(letter_id))
    for flag in all_rx_flags:
        print(flag)


if __name__ == "__main__":
    main()
