import type { EnrichedRow, ErrorFilter, ErrorSummary } from "@/lib/gallery-utils";
import { ERROR_TYPE_LABELS } from "@/lib/gallery-utils";

export function ErrorDistributionBar({
  summary,
  activeFilter,
  onFilter,
}: {
  summary: ErrorSummary;
  activeFilter: ErrorFilter;
  onFilter: (filter: ErrorFilter) => void;
}) {
  const errorTotal = summary.total - summary.correct;
  if (errorTotal === 0) return null;

  const segments = (
    [
      { type: "false_negative" as const, count: summary.false_negative, color: "bg-error" },
      { type: "false_positive" as const, count: summary.false_positive, color: "bg-llm-alt" },
      { type: "over_estimate" as const, count: summary.over_estimate, color: "bg-error/70" },
      { type: "under_estimate" as const, count: summary.under_estimate, color: "bg-deterministic-alt" },
      { type: "near_miss" as const, count: summary.near_miss, color: "bg-muted" },
    ] as Array<{ type: EnrichedRow["errorType"]; count: number; color: string }>
  ).filter((s) => s.count > 0);

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
          Error Distribution
        </div>
        <span className="text-[10px] text-muted">{errorTotal} errors total</span>
      </div>

      <div className="flex h-3 rounded-full overflow-hidden bg-surface-raised border border-border">
        {segments.map((seg) => (
          <button
            key={seg.type}
            onClick={() =>
              onFilter(activeFilter === seg.type ? "all_errors" : seg.type)
            }
            className={`${seg.color} hover:opacity-80 transition-opacity ${
              activeFilter === seg.type ? "ring-2 ring-inset ring-foreground/30" : ""
            }`}
            style={{ width: `${(seg.count / errorTotal) * 100}%` }}
            title={`${ERROR_TYPE_LABELS[seg.type]}: ${seg.count}`}
          />
        ))}
      </div>

      <div className="flex flex-wrap gap-3">
        {segments.map((seg) => (
          <button
            key={seg.type}
            onClick={() =>
              onFilter(activeFilter === seg.type ? "all_errors" : seg.type)
            }
            className={`flex items-center gap-1.5 text-[10px] transition-opacity hover:opacity-70 ${
              activeFilter === seg.type ? "font-semibold" : ""
            }`}
          >
            <div className={`h-2 w-2 rounded-full ${seg.color}`} />
            <span className="text-muted">{ERROR_TYPE_LABELS[seg.type]}</span>
            <span className="font-medium text-foreground">{seg.count}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
