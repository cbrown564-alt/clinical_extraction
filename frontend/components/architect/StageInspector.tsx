"use client";

import { useArchitectStore } from "@/lib/stores";
import JsonTree from "./JsonTree";
import type { TraceStage, TraceItem } from "@/lib/types";
import { formatMonthlyFrequency, monthlyFrequencyFromLabel } from "@/lib/traceAdapter/utils";
import { Highlighter, Scale, Target, Wrench, Trophy, AlertCircle, CheckCircle, Quote } from "lucide-react";

const stageMeta: Record<
  TraceStage,
  { label: string; icon: React.ReactNode; color: string; desc: string }
> = {
  extract: {
    label: "Recognise",
    icon: <Highlighter className="h-3.5 w-3.5" />,
    color: "text-deterministic",
    desc: "Raw candidate events found in the note by recognition rules or LLM claims.",
  },
  normalise: {
    label: "Encode",
    icon: <Scale className="h-3.5 w-3.5" />,
    color: "text-deterministic-alt",
    desc: "Candidates converted to codebook labels with semantic kinds and monthly frequencies.",
  },
  select: {
    label: "Select",
    icon: <Target className="h-3.5 w-3.5" />,
    color: "text-hybrid",
    desc: "The pipeline chooses a single final label from the encoded candidates.",
  },
  repair: {
    label: "Repair",
    icon: <Wrench className="h-3.5 w-3.5" />,
    color: "text-llm",
    desc: "JSON and schema repair applied to the model output.",
  },
  score: {
    label: "Score",
    icon: <Trophy className="h-3.5 w-3.5" />,
    color: "text-success",
    desc: "Comparison of predicted label against gold reference.",
  },
};

function stageEvidence(stage: TraceStage, trace: NonNullable<ReturnType<typeof useArchitectStore.getState>["trace"]>): string | null {
  switch (stage) {
    case "extract": {
      const first = trace.extract.items[0];
      return first?.evidence ?? null;
    }
    case "normalise": {
      const first = trace.normalise.items[0];
      return first?.evidence ?? null;
    }
    case "select":
      return trace.select.evidence || null;
    case "repair": {
      const changes = trace.repair?.changes ?? [];
      if (changes.length === 0) return "No repair changes applied.";
      return changes[0];
    }
    case "score":
      return trace.select.evidence || null;
  }
}

function resolveNormalisationRule(item: TraceItem): { rule: string; description?: string } {
  const ruleId = item.ruleId;
  const raw = (item.rawValue ?? item.evidence ?? "").toLowerCase();
  const norm = (item.normalizedValue ?? "").toLowerCase();

  if (raw.includes("≤") || raw.includes("<=") || raw.includes("up to") || raw.includes("at most")) {
    return {
      rule: "upper_bound_rate_normalisation",
      description: "upper bound quantifier → category upper limit (×30 for daily)",
    };
  }
  if (raw.includes("most day") || raw.includes("most of the days") || raw.includes("nearly every day")) {
    return {
      rule: "frequent_episodes_to_daily_rate",
      description: "idiomatic frequent episodes → daily frequency band (1 per day)",
    };
  }
  if (raw.includes("daily") || raw.includes("per day") || norm.includes("day")) {
    return {
      rule: "per_day_to_monthly_rate",
      description: "daily frequency × 30 days/month",
    };
  }
  if (raw.includes("week") || norm.includes("week")) {
    return {
      rule: "per_week_to_monthly_rate",
      description: "weekly frequency × 4.33 weeks/month",
    };
  }
  if (raw.includes("year") || norm.includes("year")) {
    return {
      rule: "per_year_to_monthly_rate",
      description: "yearly frequency ÷ 12 months/year",
    };
  }
  if (raw.includes("month") || norm.includes("month")) {
    return {
      rule: "per_month_rate",
      description: "monthly frequency rate (1:1)",
    };
  }
  if (raw.includes("free") || norm.includes("free")) {
    return {
      rule: "seizure_free_to_zero",
      description: "seizure free interval → 0 monthly frequency",
    };
  }
  if (norm.includes("unknown") || raw.includes("unknown")) {
    return {
      rule: "unknown_frequency_sentinel",
      description: "unquantified reference → sentinel 1000",
    };
  }
  if (norm.includes("no seizure") || raw.includes("no seizure") || raw.includes("no reference")) {
    return {
      rule: "no_reference_sentinel",
      description: "absence of frequency evidence → sentinel 1000",
    };
  }
  return {
    rule: ruleId && ruleId !== "normalize_frequency_label" ? ruleId : "label_to_frequency_record",
    description: "standard category lookup",
  };
}

function ItemCard({ item, stage }: { item: TraceItem; stage?: TraceStage }) {
  const isNormalise = stage === "normalise";
  const metadata = { ...item.metadata };
  const rawMonthly = metadata.monthly_frequency;
  const monthlyFreq =
    monthlyFrequencyFromLabel(item.normalizedValue ?? "") ??
    (typeof rawMonthly === "number" ? rawMonthly : undefined);
  const validationErrors = Array.isArray(metadata.validation_errors)
    ? metadata.validation_errors.filter((e) => Boolean(e))
    : [];
  const ruleInfo = isNormalise ? resolveNormalisationRule(item) : null;

  return (
    <div className="rounded-lg border border-border bg-surface p-3 space-y-2">
      <div className="flex items-center gap-2">
        <span className="rounded bg-surface-raised px-1.5 py-0.5 text-[11px] font-mono text-muted border border-border">
          {item.id}
        </span>
        <span className="text-xs font-medium text-foreground">{item.kind}</span>
        {!isNormalise && item.ruleId && (
          <span className="rounded bg-deterministic/10 px-1.5 py-0.5 text-[11px] font-mono font-medium text-deterministic">
            {item.ruleId}
          </span>
        )}
      </div>

      {isNormalise ? (
        <>
          {item.normalizedValue && (
            <div className="text-sm font-medium text-deterministic-alt">
              {item.normalizedValue}
            </div>
          )}
          {item.evidence && (
            <div className="text-xs italic text-muted">
              &quot;{item.evidence}&quot;
            </div>
          )}
          <div className="rounded-md border border-border bg-surface-raised/40 p-2.5 font-mono text-[11.5px] leading-relaxed space-y-1">
            {item.rawValue && (
              <div>
                <span className="text-muted">original_label:    </span>
                <span className="text-foreground/90">&quot;{item.rawValue}&quot;</span>
              </div>
            )}
            {monthlyFreq !== undefined && (
              <div>
                <span className="text-muted">monthly_frequency:  </span>
                <span className="text-foreground/90">{formatMonthlyFrequency(monthlyFreq)}</span>
              </div>
            )}
            {ruleInfo && (
              <>
                <div>
                  <span className="text-muted">rule:               </span>
                  <span className="text-foreground/90">{ruleInfo.rule}</span>
                </div>
                {ruleInfo.description && (
                  <div>
                    <span className="text-muted">rule_description:  </span>
                    <span className="text-muted/80">{ruleInfo.description}</span>
                  </div>
                )}
              </>
            )}
          </div>
        </>
      ) : (
        <>
          {item.rawValue && (
            <div className="text-sm font-medium text-deterministic">{item.rawValue}</div>
          )}
          {item.normalizedValue && item.normalizedValue !== item.rawValue && (
            <div className="text-sm text-deterministic-alt">
              → {item.normalizedValue}
            </div>
          )}
          {item.evidence && (
            <div className="text-xs italic text-muted">
              &quot;{item.evidence}&quot;
            </div>
          )}
        </>
      )}

      {validationErrors.length > 0 && (
        <div className="rounded border border-error/20 bg-error/5 p-2 text-xs text-error font-mono">
          <span className="font-semibold">validation_errors:</span> {validationErrors.join("; ")}
        </div>
      )}

      {(() => {
        const extraMeta = { ...metadata };
        if (isNormalise) {
          delete extraMeta.original_label;
          delete extraMeta.monthly_frequency;
          delete extraMeta.validation_errors;
        } else {
          if (Array.isArray(extraMeta.validation_errors) && extraMeta.validation_errors.length === 0) {
            delete extraMeta.validation_errors;
          }
        }
        const entries = Object.entries(extraMeta);
        if (entries.length === 0) return null;

        return (
          <div className="rounded-md border border-border bg-surface-raised/40 p-2.5 font-mono text-[11.5px] leading-relaxed space-y-1">
            {entries.map(([key, val]) => (
              <div key={key}>
                <span className="text-muted">{key}: </span>
                <span className="text-foreground/90">
                  {typeof val === "string" ? `"${val}"` : typeof val === "number" || typeof val === "boolean" ? String(val) : JSON.stringify(val)}
                </span>
              </div>
            ))}
          </div>
        );
      })()}
    </div>
  );
}

export default function StageInspector() {
  const trace = useArchitectStore((s) => s.trace);
  const activeStage = useArchitectStore((s) => s.activeStage);
  const meta = stageMeta[activeStage];
  const evidenceQuote = trace ? stageEvidence(activeStage, trace) : null;

  if (!trace) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <div className="text-center space-y-2">
          <p className="text-sm font-medium">No trace loaded</p>
          <p className="text-xs">Select a note and run the pipeline to see intermediate stages.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Compact header */}
      <div className="shrink-0 border-b border-border bg-surface px-4 py-2">
        <div className="flex items-center gap-2">
          <div className={meta.color}>{meta.icon}</div>
          <h3 className={`text-xs font-semibold ${meta.color}`}>{meta.label}</h3>
          <span className="text-[11px] text-muted">{meta.desc}</span>
        </div>
        {evidenceQuote && (
          <div className="mt-1 flex items-start gap-1.5 rounded border border-border bg-surface-raised/50 px-2 py-1">
            <Quote className="mt-0.5 h-3 w-3 shrink-0 text-muted" />
            <span className="text-[11px] italic text-muted leading-snug truncate">
              {evidenceQuote}
            </span>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {activeStage === "extract" && (
          <>
            {trace.extract.items.length === 0 ? (
              <div className="rounded-lg border border-border bg-surface-raised/30 p-4 text-center text-muted text-sm">
                No candidate events recognised.
              </div>
            ) : (
              trace.extract.items.map((item) => (
                <ItemCard key={item.id} item={item} stage="extract" />
              ))
            )}
          </>
        )}

        {activeStage === "normalise" && (
          <>
            {trace.normalise.items.length === 0 ? (
              <div className="rounded-lg border border-border bg-surface-raised/30 p-4 text-center text-muted text-sm">
                No encoded events.
              </div>
            ) : (
              trace.normalise.items.map((item) => (
                <ItemCard key={item.id} item={item} stage="normalise" />
              ))
            )}
          </>
        )}

        {activeStage === "select" && (
          <div className="rounded-lg border border-border bg-surface p-3 space-y-2">
            <div className="flex items-center gap-2">
              <span className="rounded bg-hybrid/10 px-1.5 py-0.5 text-[11px] font-mono font-medium text-hybrid border border-hybrid/20">
                select
              </span>
              {trace.select.selectedIds && trace.select.selectedIds.length > 0 && (
                <span className="text-xs font-mono text-muted">
                  selected: {trace.select.selectedIds.join(", ")}
                </span>
              )}
            </div>

            <div className="text-sm font-medium text-hybrid">
              {trace.select.finalLabel}
            </div>

            {trace.select.evidence && (
              <div className="text-xs italic text-muted">
                &quot;{trace.select.evidence}&quot;
              </div>
            )}

            <div className="rounded-md border border-border bg-surface-raised/40 p-2.5 font-mono text-[11.5px] leading-relaxed space-y-1">
              {trace.select.monthlyFrequency !== undefined && (
                <div>
                  <span className="text-muted">monthly_frequency: </span>
                  <span className="text-foreground/90">
                    {formatMonthlyFrequency(
                      monthlyFrequencyFromLabel(trace.select.finalLabel) ??
                        trace.select.monthlyFrequency
                    )}
                  </span>
                </div>
              )}
              {trace.select.selectedIds && trace.select.selectedIds.length > 0 && (
                <div>
                  <span className="text-muted">selected_ids:      </span>
                  <span className="text-foreground/90">{JSON.stringify(trace.select.selectedIds)}</span>
                </div>
              )}
              {trace.select.rejectedIds && trace.select.rejectedIds.length > 0 && (
                <div>
                  <span className="text-muted">rejected_ids:      </span>
                  <span className="text-foreground/90">{JSON.stringify(trace.select.rejectedIds)}</span>
                </div>
              )}
              {trace.select.rationale && (
                <div>
                  <span className="text-muted">rationale:         </span>
                  <span className="text-foreground/90">&quot;{trace.select.rationale}&quot;</span>
                </div>
              )}
            </div>
          </div>
        )}

        {activeStage === "score" && (
          <div className="rounded-lg border border-border bg-surface p-3 space-y-2">
            <div className="flex items-center gap-2">
              <span
                className={`inline-flex items-center gap-1 rounded px-1.5 py-0.5 text-[11px] font-mono font-medium border ${
                  trace.score.match
                    ? "bg-success/10 text-success border-success/20"
                    : "bg-error/10 text-error border-error/20"
                }`}
              >
                {trace.score.match ? (
                  <CheckCircle className="h-3 w-3" />
                ) : (
                  <AlertCircle className="h-3 w-3" />
                )}
                {trace.score.match ? "correct" : "incorrect"}
              </span>
            </div>

            <div className="flex items-baseline gap-2">
              <span
                className={`text-sm font-medium ${
                  trace.score.match ? "text-success" : "text-error"
                }`}
              >
                {trace.score.predictedLabel}
              </span>
              {!trace.score.match && (
                <span className="text-xs text-muted">
                  (gold: <span className="font-mono text-foreground">{trace.score.goldLabel}</span>)
                </span>
              )}
            </div>

            {trace.select.evidence && (
              <div className="text-xs italic text-muted">
                &quot;{trace.select.evidence}&quot;
              </div>
            )}

            <div className="rounded-md border border-border bg-surface-raised/40 p-2.5 font-mono text-[11.5px] leading-relaxed space-y-1">
              <div>
                <span className="text-muted">predicted_label: </span>
                <span className="text-foreground/90">&quot;{trace.score.predictedLabel}&quot;</span>
              </div>
              <div>
                <span className="text-muted">gold_label:      </span>
                <span className="text-foreground/90">&quot;{trace.score.goldLabel}&quot;</span>
              </div>
              <div>
                <span className="text-muted">label_match:     </span>
                <span className={trace.score.match ? "text-success" : "text-error"}>
                  {String(trace.score.match)}
                </span>
              </div>
              <div>
                <span className="text-muted">evidence_valid:  </span>
                <span className={trace.score.evidenceValid ? "text-success" : "text-error"}>
                  {String(trace.score.evidenceValid)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
