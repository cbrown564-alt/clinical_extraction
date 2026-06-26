import { ArrowRight } from "lucide-react";
import {
  type ErrorSummary,
  type ConfusedPair,
  ERROR_TYPE_LABELS,
  CATEGORY_SHORT_NAMES,
  getDominantErrorType,
} from "@/lib/gallery-utils";

export function ExecutiveSummary({
  summary,
  topPair,
}: {
  summary: ErrorSummary;
  topPair: ConfusedPair | null;
}) {
  const errorCount = summary.total - summary.correct;
  const errorRate = summary.total > 0 ? errorCount / summary.total : 0;
  const dominant = getDominantErrorType(summary);

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Error Rate
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-2xl font-semibold text-error">
            {(errorRate * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-muted">
            {errorCount} of {summary.total}
          </span>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Dominant Error
        </div>
        <div className="flex items-baseline gap-1.5">
          <span className="text-lg font-semibold text-foreground">
            {dominant ? ERROR_TYPE_LABELS[dominant.type] : "—"}
          </span>
          <span className="text-[10px] text-muted">{dominant?.count ?? 0}</span>
        </div>
      </div>

      <div className="rounded-lg border border-border bg-surface p-3">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1">
          Top Confusion
        </div>
        {topPair ? (
          <div className="flex items-center gap-1 text-[11px]">
            <span className="font-medium text-foreground">
              {CATEGORY_SHORT_NAMES[topPair.gold] ?? topPair.gold}
            </span>
            <ArrowRight className="h-2.5 w-2.5 text-muted" />
            <span className="font-medium text-error">
              {CATEGORY_SHORT_NAMES[topPair.predicted] ?? topPair.predicted}
            </span>
            <span className="text-[10px] text-muted ml-1">×{topPair.count}</span>
          </div>
        ) : (
          <span className="text-[11px] text-muted">—</span>
        )}
      </div>
    </div>
  );
}
