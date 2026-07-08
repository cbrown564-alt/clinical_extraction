"use client";

import { useMemo, useState, type ReactNode } from "react";
import { AlertOctagon, AlertTriangle, CheckCircle2, ChevronRight, CircleDashed } from "lucide-react";
import type { SfCandidateSpan, SfInspectionLetter } from "@/lib/types";
import { connectOverridesToErrors, letterVerdict } from "@/lib/sfFamilies";
import { STATUS_META, componentShortLabel } from "@/lib/sfPresentation";

export { COMPONENT_ORDER } from "@/lib/sfInspectionUi";
export { FamilyCards, FamilyLegend, LetterMatrix, ScorecardTable } from "./SfInspectionOverview";
export { LayerA } from "./SfInspectionLayerA";
export { LayerB } from "./SfInspectionLayerB";

function scrollToFailingLens(componentName: string) {
  document.getElementById(`sf-lens-${componentName}`)?.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
  });
}

function VerdictComponentRef({ name, stat }: { name: string; stat: string }) {
  return (
    <>
      {" · "}
      <button
        type="button"
        onClick={() => scrollToFailingLens(name)}
        className="font-mono underline decoration-dotted underline-offset-2 hover:text-foreground"
        title="Jump to scorer breakdown"
      >
        {componentShortLabel(name)} ({stat})
      </button>
    </>
  );
}

export function VerdictBanner({ letter }: { letter: SfInspectionLetter }) {
  const verdict = useMemo(() => letterVerdict(letter), [letter]);

  if (verdict.severity === "no-activity") {
    return (
      <VerdictShell tone="muted" icon={<CircleDashed className="h-4 w-4" />}>
        No SF activity
      </VerdictShell>
    );
  }

  if (verdict.severity === "clean") {
    return (
      <VerdictShell tone="success" icon={<CheckCircle2 className="h-4 w-4" />}>
        Clean
        {verdict.benchErr ? (
          <span className="ml-2 font-normal text-muted">· bench disagrees (expected)</span>
        ) : null}
      </VerdictShell>
    );
  }

  const comp = verdict.primaryComponent;
  const stat = comp ? `fp${comp.fp}/fn${comp.fn}` : "";

  if (verdict.severity === "change-only") {
    return (
      <VerdictShell tone="hybrid" icon={<AlertTriangle className="h-4 w-4" />}>
        Change miss
        {comp ? <VerdictComponentRef name={comp.name} stat={stat} /> : null}
      </VerdictShell>
    );
  }

  return (
    <VerdictShell tone="error" icon={<AlertOctagon className="h-4 w-4" />}>
      Headline miss
      {comp ? <VerdictComponentRef name={comp.name} stat={stat} /> : null}
    </VerdictShell>
  );
}

const VERDICT_TONE: Record<string, string> = {
  success: "border-l-success bg-success/10 text-success",
  hybrid: "border-l-hybrid bg-hybrid/10 text-hybrid",
  error: "border-l-error bg-error/10 text-error",
  muted: "border-l-border bg-surface-raised text-muted",
};

function VerdictShell({
  tone,
  icon,
  children,
}: {
  tone: keyof typeof VERDICT_TONE;
  icon: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className={`flex items-center gap-2 border-l-[3px] px-3 py-2 ${VERDICT_TONE[tone]}`}>
      <span className="shrink-0">{icon}</span>
      <p className="text-[13px] font-semibold text-foreground">{children}</p>
    </div>
  );
}

export function CandidateSpansContext({ spans }: { spans: SfCandidateSpan[] }) {
  if (spans.length === 0) return null;

  return (
    <section>
      <h3 className="mb-2 text-[10px] font-bold uppercase tracking-wider text-muted">Letter context</h3>
      <ul className="flex flex-col gap-2">
        {spans.map((span, i) => (
          <li key={i} className="overflow-hidden rounded-md border border-border bg-surface-raised">
            <div className="flex items-stretch">
              <span className="w-1 shrink-0 bg-hybrid" aria-hidden />
              <div className="min-w-0 flex-1 px-3 py-2.5">
                <p className="font-mono text-[13px] font-semibold leading-snug text-foreground">{span.text_hint}</p>
                {span.evidence && span.evidence !== span.text_hint && (
                  <p className="mt-1 text-[11px] leading-relaxed text-muted">{span.evidence}</p>
                )}
                <p className="mt-1.5 font-mono text-[9px] text-muted">
                  {span.candidate_type}
                  {span.source ? ` · ${span.source}` : ""}
                </p>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}

export function LineagePanel({
  letter,
  hideSpans = false,
}: {
  letter: SfInspectionLetter;
  hideSpans?: boolean;
}) {
  const { lineage } = letter;
  const spans = lineage.candidate_spans;
  const override = lineage.override;
  const [spansOpen, setSpansOpen] = useState(false);
  const connections = useMemo(
    () => connectOverridesToErrors(letter, override?.applied ? override.items : undefined),
    [letter, override]
  );

  const hasOverride = !!override?.applied && (override.items?.length ?? 0) > 0;
  if (!hasOverride && spans.length === 0 && !(override && !override.applied)) {
    return <p className="text-[11px] text-muted">No lineage recorded</p>;
  }

  return (
    <div className="space-y-2">
      {hasOverride && (
        <div className="border-l-[3px] border-l-hybrid bg-hybrid/5 px-3 py-2">
          <p className="mb-1 text-[10px] font-bold uppercase tracking-wide text-hybrid">Magnitude override</p>
          <ul className="space-y-1">
            {override!.items!.map((item, i) => {
              const hit = connections.find((c) => c.item === item);
              return (
                <li key={i} className="font-mono text-[11px] text-foreground">
                  <span className="font-semibold">{item.applies_to}</span>
                  <span className="mx-1.5 text-muted">
                    <span className="text-error line-through">{item.prior_frequency_change || "—"}</span>
                    {" → "}
                    {item.assembled_magnitude}
                  </span>
                  {hit && (
                    <span className="ml-1 text-[10px] font-bold text-error">
                      → {STATUS_META[hit.row.status].label} {hit.component}
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {override && !override.applied && (
        <p className="font-mono text-[10px] text-muted">
          FreqChg drift · baseline {JSON.stringify(override.baseline)} vs complement{" "}
          {JSON.stringify(override.complement)}
        </p>
      )}

      {!hideSpans && spans.length > 0 && (
        <div>
          <button
            type="button"
            onClick={() => setSpansOpen((v) => !v)}
            className="flex items-center gap-1 text-[10px] font-semibold text-muted hover:text-foreground"
          >
            <ChevronRight className={`h-2.5 w-2.5 transition-transform ${spansOpen ? "rotate-90" : ""}`} />
            {spans.length} candidate span{spans.length === 1 ? "" : "s"}
          </button>
          {spansOpen && (
            <ul className="mt-1 space-y-0.5 border-l border-border pl-2">
              {spans.map((span, i) => (
                <li key={i} className="text-[10px]">
                  <span className="font-mono text-foreground">{span.text_hint}</span>
                  <span className="ml-1.5 text-muted">
                    {span.candidate_type}
                    {span.evidence ? ` · ${span.evidence}` : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
