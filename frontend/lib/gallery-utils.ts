import type { RowScore } from "@/lib/types";

// ── Category display names ───────────────────────────────────────────

export const CATEGORY_DISPLAY_NAMES: Record<string, string> = {
  currently_no_seizure: "No seizure",
  seizure_freq_unknown: "Unknown",
  seizure_freq_1_per_yr: "1 per year",
  seizure_freq_1_per_6mon: "1 per 6 months",
  seizure_freq_more1per6mon_less1mon: "1/6mo – 1/mo",
  seizure_freq_1_per_mon: "1 per month",
  seizure_freq_more1mon_less1week: "1/mo – 1/wk",
  seizure_freq_1_per_week: "1 per week",
  seizure_freq_more1week_less1day: "1/wk – 1/day",
  seizure_freq_1ormore_daily: "≥1 per day",
  seizure_infrequent: "Infrequent",
  seizure_frequent: "Frequent",
};

export const CATEGORY_SHORT_NAMES: Record<string, string> = {
  currently_no_seizure: "No seizure",
  seizure_freq_unknown: "Unknown",
  seizure_freq_1_per_yr: "1/yr",
  seizure_freq_1_per_6mon: "1/6mo",
  seizure_freq_more1per6mon_less1mon: "1/6–1/mo",
  seizure_freq_1_per_mon: "1/mo",
  seizure_freq_more1mon_less1week: "1/mo–1/wk",
  seizure_freq_1_per_week: "1/wk",
  seizure_freq_more1week_less1day: "1/wk–1/d",
  seizure_freq_1ormore_daily: "≥1/d",
  seizure_infrequent: "Infreq",
  seizure_frequent: "Freq",
};

// ── Frequency magnitude for severity computation ─────────────────────

// 0 = no frequency information, 1 = very low, 8 = very high
const CATEGORY_MAGNITUDE: Record<string, number> = {
  currently_no_seizure: 0,
  seizure_freq_unknown: 0,
  seizure_freq_1_per_yr: 1,
  seizure_freq_1_per_6mon: 2,
  seizure_freq_more1per6mon_less1mon: 3,
  seizure_freq_1_per_mon: 4,
  seizure_freq_more1mon_less1week: 5,
  seizure_freq_1_per_week: 6,
  seizure_freq_more1week_less1day: 7,
  seizure_freq_1ormore_daily: 8,
  seizure_infrequent: 1,
  seizure_frequent: 8,
};

export function categoryMagnitude(cat: string): number {
  return CATEGORY_MAGNITUDE[cat] ?? 0;
}

// ── Error taxonomy ───────────────────────────────────────────────────

export type ErrorType =
  | "correct"
  | "false_negative"
  | "false_positive"
  | "over_estimate"
  | "under_estimate"
  | "near_miss";

export const ERROR_TYPE_LABELS: Record<ErrorType, string> = {
  correct: "Correct",
  false_negative: "False negative",
  false_positive: "False positive",
  over_estimate: "Over-estimate",
  under_estimate: "Under-estimate",
  near_miss: "Near miss",
};

export const ERROR_TYPE_COLORS: Record<ErrorType, string> = {
  correct: "bg-success/10 text-success border-success/20",
  false_negative: "bg-error/10 text-error border-error/30",
  false_positive: "bg-llm-alt/10 text-llm-alt border-llm-alt/30",
  over_estimate: "bg-error/10 text-error border-error/30",
  under_estimate: "bg-deterministic-alt/10 text-deterministic-alt border-deterministic-alt/30",
  near_miss: "bg-error/5 text-error/80 border-error/15",
};

export function classifyError(row: RowScore): ErrorType {
  if (row.puristCorrect) return "correct";

  const goldMag = categoryMagnitude(row.goldCategory);
  const predMag = categoryMagnitude(row.predictedCategory);

  if (goldMag > 0 && predMag === 0) return "false_negative";
  if (goldMag === 0 && predMag > 0) return "false_positive";
  if (predMag > goldMag) {
    if (predMag - goldMag === 1) return "near_miss";
    return "over_estimate";
  }
  if (predMag < goldMag) {
    if (goldMag - predMag === 1) return "near_miss";
    return "under_estimate";
  }
  return "near_miss";
}

// ── Severity ─────────────────────────────────────────────────────────

export type SeverityLevel = "none" | "near" | "moderate" | "significant" | "severe";

export function computeSeverity(row: RowScore): number {
  if (row.puristCorrect) return 0;
  const goldMag = categoryMagnitude(row.goldCategory);
  const predMag = categoryMagnitude(row.predictedCategory);
  return Math.abs(predMag - goldMag);
}

export function severityLevel(severity: number): SeverityLevel {
  if (severity === 0) return "none";
  if (severity === 1) return "near";
  if (severity <= 3) return "moderate";
  if (severity <= 5) return "significant";
  return "severe";
}

export function severityDotClass(level: SeverityLevel): string {
  switch (level) {
    case "none":
      return "bg-success";
    case "near":
      return "bg-error/40";
    case "moderate":
      return "bg-error/60";
    case "significant":
      return "bg-error/80";
    case "severe":
      return "bg-error";
  }
}

export function severityRowClass(level: SeverityLevel): string {
  switch (level) {
    case "none":
      return "border-border/50 bg-surface";
    case "near":
      return "border-error/10 bg-error/[0.02]";
    case "moderate":
      return "border-error/20 bg-error/[0.04]";
    case "significant":
      return "border-error/30 bg-error/[0.06]";
    case "severe":
      return "border-error/40 bg-error/[0.08]";
  }
}

// ── Enriched row ─────────────────────────────────────────────────────

export interface EnrichedRow extends RowScore {
  runId: string;
  pipelineFamily: string;
  sourceRowIndex: number;
  errorType: ErrorType;
  severity: number;
  severityLevel: SeverityLevel;
}

export function enrichRow(
  row: RowScore & { runId: string; pipelineFamily: string; sourceRowIndex: number }
): EnrichedRow {
  const errorType = classifyError(row);
  const severity = computeSeverity(row);
  return {
    ...row,
    runId: row.runId,
    pipelineFamily: row.pipelineFamily,
    sourceRowIndex: row.sourceRowIndex,
    errorType,
    severity,
    severityLevel: severityLevel(severity),
  };
}

// ── Filter helpers ───────────────────────────────────────────────────

export type ErrorFilter = "all_errors" | ErrorType | "all_rows";

export function filterRows(rows: EnrichedRow[], filter: ErrorFilter): EnrichedRow[] {
  if (filter === "all_rows") return rows;
  if (filter === "all_errors") return rows.filter((r) => r.errorType !== "correct");
  return rows.filter((r) => r.errorType === filter);
}

export type SortKey = "severity" | "error_type" | "gold_category" | "run";

export function sortRows(rows: EnrichedRow[], key: SortKey): EnrichedRow[] {
  const sorted = [...rows];
  switch (key) {
    case "severity":
      sorted.sort((a, b) => b.severity - a.severity || a.errorType.localeCompare(b.errorType));
      break;
    case "error_type":
      sorted.sort((a, b) => a.errorType.localeCompare(b.errorType) || b.severity - a.severity);
      break;
    case "gold_category":
      sorted.sort((a, b) => a.goldCategory.localeCompare(b.goldCategory) || b.severity - a.severity);
      break;
    case "run":
      sorted.sort((a, b) => a.runId.localeCompare(b.runId) || b.severity - a.severity);
      break;
  }
  return sorted;
}

// ── Summary stats ────────────────────────────────────────────────────

export interface ErrorSummary {
  total: number;
  correct: number;
  false_negative: number;
  false_positive: number;
  over_estimate: number;
  under_estimate: number;
  near_miss: number;
}

export function computeSummary(rows: EnrichedRow[]): ErrorSummary {
  const summary: ErrorSummary = {
    total: rows.length,
    correct: 0,
    false_negative: 0,
    false_positive: 0,
    over_estimate: 0,
    under_estimate: 0,
    near_miss: 0,
  };
  for (const row of rows) {
    summary[row.errorType]++;
  }
  return summary;
}

// ── Run comparison ───────────────────────────────────────────────────

export interface ComparisonResult {
  rowIdx: number;
  primary: EnrichedRow;
  compare: EnrichedRow | null;
  status: "fix" | "regression" | "both_wrong" | "both_right" | "no_compare";
}

export function compareRuns(
  primaryRows: EnrichedRow[],
  compareRows: EnrichedRow[]
): ComparisonResult[] {
  const results: ComparisonResult[] = [];
  for (let i = 0; i < primaryRows.length; i++) {
    const primary = primaryRows[i];
    const compare = compareRows[i] ?? null;
    let status: ComparisonResult["status"] = "no_compare";

    if (compare) {
      if (!primary.puristCorrect && compare.puristCorrect) status = "fix";
      else if (primary.puristCorrect && !compare.puristCorrect) status = "regression";
      else if (!primary.puristCorrect && !compare.puristCorrect) status = "both_wrong";
      else status = "both_right";
    }

    results.push({ rowIdx: i, primary, compare, status });
  }
  return results;
}

export function comparisonStatusLabel(status: ComparisonResult["status"]): string {
  switch (status) {
    case "fix":
      return "Fixed";
    case "regression":
      return "Regressed";
    case "both_wrong":
      return "Still wrong";
    case "both_right":
      return "Still correct";
    case "no_compare":
      return "No compare";
  }
}

export function comparisonStatusColor(status: ComparisonResult["status"]): string {
  switch (status) {
    case "fix":
      return "bg-success/10 text-success border-success/20";
    case "regression":
      return "bg-error/10 text-error border-error/20";
    case "both_wrong":
      return "bg-error/5 text-error/70 border-error/10";
    case "both_right":
      return "bg-success/5 text-success/70 border-success/10";
    case "no_compare":
      return "bg-muted/10 text-muted border-muted/20";
  }
}

// ── Analytical helpers ───────────────────────────────────────────────

export interface ConfusedPair {
  gold: string;
  predicted: string;
  count: number;
}

export function getTopConfusedPairs(rows: EnrichedRow[], n = 5): ConfusedPair[] {
  const map = new Map<string, ConfusedPair>();
  for (const row of rows) {
    if (row.puristCorrect) continue;
    const key = `${row.goldCategory}→${row.predictedCategory}`;
    const existing = map.get(key);
    if (existing) {
      existing.count++;
    } else {
      map.set(key, { gold: row.goldCategory, predicted: row.predictedCategory, count: 1 });
    }
  }
  return Array.from(map.values())
    .sort((a, b) => b.count - a.count)
    .slice(0, n);
}

export interface FamilyBreakdown {
  family: string;
  total: number;
  errors: number;
  errorRate: number;
  dominantErrorType: ErrorType | null;
}

export function getFamilyBreakdown(rows: EnrichedRow[]): FamilyBreakdown[] {
  const map = new Map<string, { total: number; errors: number; typeCounts: Map<ErrorType, number> }>();
  for (const row of rows) {
    const entry = map.get(row.pipelineFamily) ?? { total: 0, errors: 0, typeCounts: new Map<ErrorType, number>() };
    entry.total++;
    if (row.errorType !== "correct") {
      entry.errors++;
      entry.typeCounts.set(row.errorType, (entry.typeCounts.get(row.errorType) ?? 0) + 1);
    }
    map.set(row.pipelineFamily, entry);
  }

  return Array.from(map.entries())
    .map(([family, data]) => {
      let dominantErrorType: ErrorType | null = null;
      let maxCount = 0;
      for (const [type, count] of data.typeCounts) {
        if (count > maxCount) {
          maxCount = count;
          dominantErrorType = type;
        }
      }
      return {
        family,
        total: data.total,
        errors: data.errors,
        errorRate: data.total > 0 ? data.errors / data.total : 0,
        dominantErrorType,
      };
    })
    .sort((a, b) => b.errorRate - a.errorRate);
}

export interface SeverityDistribution {
  level: SeverityLevel;
  count: number;
}

export function getSeverityDistribution(rows: EnrichedRow[]): SeverityDistribution[] {
  const counts = new Map<SeverityLevel, number>();
  for (const row of rows) {
    counts.set(row.severityLevel, (counts.get(row.severityLevel) ?? 0) + 1);
  }
  const order: SeverityLevel[] = ["severe", "significant", "moderate", "near", "none"];
  return order
    .map((level) => ({ level, count: counts.get(level) ?? 0 }))
    .filter((d) => d.count > 0);
}

export function getDominantErrorType(summary: ErrorSummary): { type: ErrorType; count: number } | null {
  let max = 0;
  let type: ErrorType | null = null;
  const errorTypes: ErrorType[] = ["false_negative", "false_positive", "over_estimate", "under_estimate", "near_miss"];
  for (const t of errorTypes) {
    const count = summary[t];
    if (count > max) {
      max = count;
      type = t;
    }
  }
  return type ? { type, count: max } : null;
}

export function familyColorClass(family: string): string {
  if (family.includes("rules_only") || family.includes("deterministic")) {
    return "text-deterministic bg-deterministic/10 border-deterministic/20";
  }
  if (family.includes("hybrid")) {
    return "text-hybrid bg-hybrid/10 border-hybrid/20";
  }
  return "text-llm bg-llm/10 border-llm/20";
}
