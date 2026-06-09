"use client";

import { useArchitectStore } from "@/lib/stores";
import JsonTree from "./JsonTree";
import type { TraceStage, TraceItem } from "@/lib/types";
import { Highlighter, Scale, Target, Wrench, Trophy, AlertCircle, CheckCircle, Quote } from "lucide-react";

const stageMeta: Record<
  TraceStage,
  { label: string; icon: React.ReactNode; color: string; desc: string }
> = {
  extract: {
    label: "Extract",
    icon: <Highlighter className="h-3.5 w-3.5" />,
    color: "text-deterministic",
    desc: "Raw candidate events found in the note by extraction rules or LLM claims.",
  },
  normalise: {
    label: "Normalise",
    icon: <Scale className="h-3.5 w-3.5" />,
    color: "text-deterministic-alt",
    desc: "Candidates converted to normalised labels with semantic kinds and monthly frequencies.",
  },
  select: {
    label: "Select",
    icon: <Target className="h-3.5 w-3.5" />,
    color: "text-hybrid",
    desc: "The pipeline chooses a single final label from the normalised candidates.",
  },
  repair: {
    label: "Repair",
    icon: <Wrench className="h-3.5 w-3.5" />,
    color: "text-llm",
    desc: "Format repair and benchmark-normalisation adjustments.",
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

function ItemCard({ item }: { item: TraceItem }) {
  const hasSpan = item.startChar !== null && item.endChar !== null;
  return (
    <div className="rounded-lg border border-border bg-surface p-3 space-y-1.5">
      <div className="flex items-center gap-2">
        <span className="rounded bg-surface-raised px-1.5 py-0 text-[10px] font-mono text-muted border border-border">
          {item.id}
        </span>
        <span className="text-[11px] font-medium text-foreground">{item.kind}</span>
        {item.ruleId && (
          <span className="text-[10px] font-mono text-deterministic">{item.ruleId}</span>
        )}
      </div>
      {item.rawValue && (
        <div className="text-sm text-foreground">{item.rawValue}</div>
      )}
      {item.normalizedValue && item.normalizedValue !== item.rawValue && (
        <div className="text-sm text-deterministic-alt">
          → {item.normalizedValue}
        </div>
      )}
      {hasSpan && (
        <div className="text-[10px] text-muted font-mono">
          chars {item.startChar}–{item.endChar}
        </div>
      )}
      {item.evidence && (
        <div className="text-[11px] text-muted italic border-l-2 border-border pl-2">
          "{item.evidence}"
        </div>
      )}
      {item.metadata && Object.keys(item.metadata).length > 0 && (
        <div className="mt-1">
          <JsonTree data={item.metadata} />
        </div>
      )}
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
          <span className="text-[10px] text-muted">{meta.desc}</span>
        </div>
        {evidenceQuote && (
          <div className="mt-1 flex items-start gap-1.5 rounded bg-surface-raised/50 pl-2 pr-2 py-1 border-l-2 border-border">
            <Quote className="mt-0.5 h-3 w-3 shrink-0 text-muted" />
            <span className="text-[10px] italic text-muted leading-snug truncate">
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
                No candidate events extracted.
              </div>
            ) : (
              trace.extract.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))
            )}
          </>
        )}

        {activeStage === "normalise" && (
          <>
            {trace.normalise.items.length === 0 ? (
              <div className="rounded-lg border border-border bg-surface-raised/30 p-4 text-center text-muted text-sm">
                No normalised events.
              </div>
            ) : (
              trace.normalise.items.map((item) => (
                <ItemCard key={item.id} item={item} />
              ))
            )}
          </>
        )}

        {activeStage === "select" && (
          <div className="space-y-3">
            <div className="rounded-lg border border-hybrid/20 bg-hybrid/5 p-4 space-y-2">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-hybrid">Final Label</div>
              <div className="text-lg font-semibold text-foreground">{trace.select.finalLabel}</div>
              {trace.select.monthlyFrequency !== undefined && (
                <div className="text-sm text-muted">
                  Monthly frequency: <span className="font-mono">{trace.select.monthlyFrequency.toFixed(2)}</span>
                </div>
              )}
            </div>
            <div className="rounded-lg border border-border bg-surface p-3 space-y-1">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-muted">Rationale</div>
              <div className="text-sm text-foreground leading-relaxed">{trace.select.rationale}</div>
            </div>
            <div className="rounded-lg border border-border bg-surface p-3 space-y-1">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-muted">Evidence</div>
              <div className="text-sm text-foreground italic">"{trace.select.evidence}"</div>
            </div>
            {trace.select.selectedIds && trace.select.selectedIds.length > 0 && (
              <div className="rounded-lg border border-border bg-surface p-3">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-1">Selected IDs</div>
                <div className="flex flex-wrap gap-1">
                  {trace.select.selectedIds.map((id) => (
                    <span key={id} className="rounded bg-success/10 px-2 py-0.5 text-[11px] font-mono text-success border border-success/20">
                      {id}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {trace.select.rejectedIds && trace.select.rejectedIds.length > 0 && (
              <div className="rounded-lg border border-border bg-surface p-3">
                <div className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-1">Rejected IDs</div>
                <div className="flex flex-wrap gap-1">
                  {trace.select.rejectedIds.map((id) => (
                    <span key={id} className="rounded bg-error/10 px-2 py-0.5 text-[11px] font-mono text-error border border-error/20">
                      {id}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeStage === "repair" && (
          <>
            {trace.repair && trace.repair.changes.length > 0 ? (
              <div className="space-y-3">
                {trace.repair.changes.map((change, idx) => (
                  <div key={idx} className="rounded-lg border border-llm/20 bg-llm/5 p-3">
                    <div className="text-sm text-foreground">{change}</div>
                  </div>
                ))}
                {trace.repair.beforeLabel && trace.repair.afterLabel && (
                  <div className="rounded-lg border border-border bg-surface p-3 space-y-1">
                    <div className="text-[11px] font-semibold uppercase tracking-wide text-muted">Before → After</div>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-muted line-through">{trace.repair.beforeLabel}</span>
                      <span className="text-llm">→</span>
                      <span className="text-foreground font-medium">{trace.repair.afterLabel}</span>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="rounded-lg border border-border bg-surface-raised/30 p-4 text-center text-muted text-sm">
                No repair changes applied.
              </div>
            )}
          </>
        )}

        {activeStage === "score" && (
          <div className="space-y-3">
            <div className={`rounded-lg border p-4 space-y-2 ${trace.score.match ? "border-success/20 bg-success/5" : "border-error/20 bg-error/5"}`}>
              <div className="flex items-center gap-2">
                {trace.score.match ? (
                  <CheckCircle className="h-4 w-4 text-success" />
                ) : (
                  <AlertCircle className="h-4 w-4 text-error" />
                )}
                <span className={`text-sm font-semibold ${trace.score.match ? "text-success" : "text-error"}`}>
                  {trace.score.match ? "Correct" : "Incorrect"}
                </span>
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <div className="text-[10px] uppercase tracking-wide text-muted">Predicted</div>
                  <div className="text-sm font-medium text-foreground">{trace.score.predictedLabel}</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wide text-muted">Gold</div>
                  <div className="text-sm font-medium text-foreground">{trace.score.goldLabel}</div>
                </div>
              </div>
            </div>
            <div className="rounded-lg border border-border bg-surface p-3">
              <div className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-1">Evidence Valid</div>
              <span className={`text-sm font-medium ${trace.score.evidenceValid ? "text-success" : "text-error"}`}>
                {trace.score.evidenceValid ? "Yes" : "No"}
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
