import Link from "next/link";
import { ExternalLink } from "lucide-react";
import {
  type EnrichedRow,
  type ComparisonResult,
  CATEGORY_DISPLAY_NAMES,
  CATEGORY_SHORT_NAMES,
  comparisonStatusLabel,
  comparisonStatusColor,
} from "@/lib/gallery-utils";
import { CorrectnessBadge, ComparisonIcon } from "./GalleryShared";

export function ErrorDetail({
  row,
  compareRow,
  compareStatus,
  compareRunId,
}: {
  row: EnrichedRow;
  compareRow: EnrichedRow | null;
  compareStatus: ComparisonResult["status"];
  compareRunId: string | null;
}) {
  const workbenchHref = `/workbench?pipeline=${encodeURIComponent(row.pipelineFamily)}&split=${encodeURIComponent(row.split ?? "validation")}&row=${row.sourceRowIndex}&stage=score`;

  return (
    <div className="px-3 pb-3 pt-1 border-t border-border/50">
      <div className="mt-2 mb-2">
        <Link
          href={workbenchHref}
          className="inline-flex items-center gap-1.5 rounded-md border border-deterministic/20 bg-deterministic/5 px-2.5 py-1 text-[10px] font-medium text-deterministic hover:bg-deterministic/10 transition-colors"
        >
          <ExternalLink className="h-3 w-3" />
          Open in Workbench
        </Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div className="space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Primary Prediction
          </div>
          <div className="rounded-md border border-border bg-surface p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-muted">Run</span>
              <span className="text-[10px] font-mono text-foreground">{row.runId}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-[10px] text-muted">Family</span>
              <span className="text-[10px] font-medium text-foreground">{row.pipelineFamily}</span>
            </div>
            <div className="border-t border-border/50 pt-2 space-y-1.5">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted w-12">Gold</span>
                <span className="text-sm font-mono text-foreground">{row.goldLabel}</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-muted w-12">Pred</span>
                <span
                  className={`text-sm font-mono ${
                    row.puristCorrect ? "text-foreground" : "text-error font-medium"
                  }`}
                >
                  {row.predictedLabel}
                </span>
              </div>
            </div>
            <div className="border-t border-border/50 pt-2 flex items-center gap-3">
              <CorrectnessBadge correct={row.puristCorrect} label="Purist" />
              <CorrectnessBadge correct={row.pragmaticCorrect} label="Pragmatic" />
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
            Category Analysis
          </div>
          <div className="rounded-md border border-border bg-surface p-3 space-y-2">
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-muted">Gold:</span>
              <span className="font-medium text-foreground">
                {CATEGORY_DISPLAY_NAMES[row.goldCategory] ?? row.goldCategory}
              </span>
              <span className="text-[9px] font-mono text-muted">({row.goldCategory})</span>
            </div>
            <div className="flex items-center gap-2 text-[11px]">
              <span className="text-muted">Pred:</span>
              <span
                className={`font-medium ${
                  row.puristCorrect ? "text-foreground" : "text-error"
                }`}
              >
                {CATEGORY_DISPLAY_NAMES[row.predictedCategory] ?? row.predictedCategory}
              </span>
              <span className="text-[9px] font-mono text-muted">({row.predictedCategory})</span>
            </div>
            {row.errorType !== "correct" && (
              <div className="flex items-center gap-2 text-[10px]">
                <span className="text-muted">Severity:</span>
                <span className="font-medium text-error capitalize">{row.severityLevel}</span>
                <span className="text-muted">({row.severity} magnitude levels)</span>
              </div>
            )}

            {compareRow && compareRunId && (
              <div className="border-t border-border/50 pt-2">
                <div className="text-[10px] font-semibold uppercase tracking-wider text-muted mb-1.5">
                  Comparison — {compareRunId.slice(0, 40)}
                  {compareRunId.length > 40 ? "…" : ""}
                </div>
                <div className="flex items-center gap-2 text-[11px]">
                  <span className="text-muted">Pred:</span>
                  <span
                    className={`font-mono ${
                      compareRow.puristCorrect ? "text-success" : "text-error"
                    }`}
                  >
                    {compareRow.predictedLabel}
                  </span>
                  <span
                    className={`inline-flex items-center gap-1 rounded border px-1.5 py-0 text-[9px] font-medium ${comparisonStatusColor(compareStatus)}`}
                  >
                    <ComparisonIcon status={compareStatus} />
                    {comparisonStatusLabel(compareStatus)}
                  </span>
                </div>
                <div className="flex items-center gap-2 text-[10px] mt-1">
                  <span className="text-muted">Category:</span>
                  <span>
                    {CATEGORY_SHORT_NAMES[compareRow.predictedCategory] ?? compareRow.predictedCategory}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {(row.evidence || row.rationale) && (
        <div className="mt-3 space-y-3">
          {row.evidence && (
            <div className="space-y-1.5">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Selected Evidence
              </div>
              <div className="rounded-md border border-border bg-surface p-3">
                <blockquote className="text-[11px] leading-relaxed text-foreground font-serif italic border-l-2 border-deterministic/30 pl-3">
                  {row.evidence}
                </blockquote>
              </div>
            </div>
          )}
          {row.rationale && (
            <div className="space-y-1.5">
              <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Model Rationale
              </div>
              <div className="rounded-md border border-border bg-surface p-3">
                <p className="text-[11px] leading-relaxed text-foreground">{row.rationale}</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
