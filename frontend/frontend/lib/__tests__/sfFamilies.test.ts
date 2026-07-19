import {
  countLettersByTriage,
  familyTriageStatus,
  letterMatchesTriageFilter,
  letterVerdict,
  neighborLetterIds,
  SF_FAMILIES,
  sortLettersForTriage,
  triageRank,
} from "../sfFamilies";
import type { SfInspectionLetter, SfLayerBComponent } from "../types";

function comp(name: string, fp: number, fn: number): SfLayerBComponent {
  return {
    name,
    info: "",
    has_error: fp + fn > 0,
    verdict: fp + fn > 0 ? "err" : "clean",
    tp: 1,
    fp,
    fn,
    rows: [],
  };
}

function letter(
  id: string,
  opts: {
    activity?: boolean;
    headline?: [number, number];
    change?: [number, number];
    bench?: [number, number];
  } = {}
): SfInspectionLetter {
  const [hFp, hFn] = opts.headline ?? [0, 0];
  const [cFp, cFn] = opts.change ?? [0, 0];
  const [bFp, bFn] = opts.bench ?? [0, 0];
  return {
    letter_id: id,
    has_activity: opts.activity ?? true,
    gold_count: 1,
    pred_count: 1,
    total_errors: hFp + hFn + cFp + cFn + bFp + bFn,
    direction_errors: { fp: 0, fn: 0 },
    magnitude_errors: { fp: 0, fn: 0 },
    layer_a: { pairs: [] },
    layer_b: {
      components: [
        comp("clinical_headline", hFp, hFn),
        comp("active_rate", 0, 0),
        comp("state_profile", cFp, cFn),
        comp("state_profile_directional", 0, 0),
        comp("exact_semantic", bFp, bFn),
        comp("benchmark_with_cui", 0, 0),
      ],
    },
    lineage: { candidate_spans: [], override: null },
    gold_case_ledger: [],
  };
}

describe("letter triage filters", () => {
  const headline = letter("H", { headline: [1, 0] });
  const change = letter("C", { change: [0, 1] });
  const benchOnly = letter("B", { bench: [2, 0] });
  const clean = letter("K");
  const inactive = letter("Z", { activity: false });

  it("treats headline and change as actionable, not bench-only", () => {
    expect(letterMatchesTriageFilter(headline, "actionable")).toBe(true);
    expect(letterMatchesTriageFilter(change, "actionable")).toBe(true);
    expect(letterMatchesTriageFilter(benchOnly, "actionable")).toBe(false);
    expect(letterMatchesTriageFilter(clean, "actionable")).toBe(false);
  });

  it("isolates bench-only from scored-family clean", () => {
    expect(letterMatchesTriageFilter(benchOnly, "bench")).toBe(true);
    expect(letterMatchesTriageFilter(clean, "bench")).toBe(false);
    expect(letterMatchesTriageFilter(benchOnly, "clean")).toBe(false);
    expect(letterMatchesTriageFilter(clean, "clean")).toBe(true);
  });

  it("counts and sorts with actionable first", () => {
    const letters = [clean, benchOnly, change, headline, inactive];
    const counts = countLettersByTriage(letters);
    expect(counts.actionable).toBe(2);
    expect(counts.headline).toBe(1);
    expect(counts.change).toBe(1);
    expect(counts.bench).toBe(1);
    expect(counts.clean).toBe(1);
    expect(counts.all).toBe(5);

    expect(sortLettersForTriage(letters).map((l) => l.letter_id)).toEqual([
      "H",
      "C",
      "B",
      "K",
      "Z",
    ]);
    expect(triageRank(headline)).toBeLessThan(triageRank(change));
  });

  it("walks neighbors in the visible list", () => {
    const sorted = sortLettersForTriage([clean, change, headline]);
    expect(neighborLetterIds(sorted, "H")).toEqual({ prevId: null, nextId: "C", index: 0 });
    expect(neighborLetterIds(sorted, "C")).toEqual({ prevId: "H", nextId: "K", index: 1 });
    expect(neighborLetterIds(sorted, "missing")).toEqual({
      prevId: null,
      nextId: null,
      index: -1,
    });
  });

  it("keeps verdict severity ranking aligned with filters", () => {
    expect(letterVerdict(headline).severity).toBe("headline");
    expect(letterVerdict(change).severity).toBe("change-only");
    expect(letterVerdict(benchOnly).severity).toBe("clean");
    expect(letterVerdict(benchOnly).benchErr).toBe(true);
  });

  it("surfaces child-lens errors in triage cells when root is clean", () => {
    const childOnly = letter("X");
    childOnly.layer_b.components.push({
      name: "active_rate_fidelity",
      info: "",
      has_error: true,
      verdict: "err",
      tp: 1,
      fp: 1,
      fn: 1,
      rows: [],
    });
    expect(letterVerdict(childOnly).severity).toBe("headline");
    expect(letterMatchesTriageFilter(childOnly, "actionable")).toBe(true);
    const status = familyTriageStatus(childOnly, SF_FAMILIES[0]);
    expect(status.clean).toBe(false);
    expect(status.fp + status.fn).toBeGreaterThan(0);
  });
});
