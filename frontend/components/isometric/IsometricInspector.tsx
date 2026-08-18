"use client";

import React, { useState, useMemo } from "react";
import {
  Activity,
  CheckCircle,
  XCircle,
  FlaskConical,
  ArrowRight,
  Sparkles,
  ChevronDown,
  ChevronRight,
  ShieldCheck,
  Cpu,
  Binary,
  Scale,
  MessageSquareQuote,
  Lightbulb,
} from "lucide-react";
import {
  useIsometricStore,
  getActiveCase,
  getActiveRun,
  getActiveObservation,
  getActiveManifest,
  getStageManifest,
} from "@/lib/isometricStore";
import FormattedPayloadViewer from "./FormattedPayloadViewer";

const EFFECT_STYLES: Record<
  string,
  { label: string; desc: string; badgeClass: string; cardClass: string }
> = {
  transport_or_schema: {
    label: "Transport & Schema",
    desc: "Changes transport format or JSON container only. Does not alter clinical findings.",
    badgeClass: "bg-slate-100 text-slate-800 border-slate-300",
    cardClass: "border-slate-200 bg-slate-50/50",
  },
  representation: {
    label: "Representation Format",
    desc: "Normalizes rates and units (e.g. rate canonicalization) without changing the clinical fact.",
    badgeClass: "bg-sky-100 text-sky-900 border-sky-300 font-semibold",
    cardClass: "border-sky-200 bg-sky-50/30",
  },
  clinical_meaning: {
    label: "CLINICAL MEANING SHIFT ★",
    desc: "CRITICAL: Overrules, selects, drops, or modifies a clinical finding.",
    badgeClass: "bg-amber-100 text-amber-950 border-amber-400 font-extrabold ring-1 ring-amber-400/50",
    cardClass: "border-amber-300 bg-amber-50/60 shadow-xs",
  },
  validation_gate: {
    label: "Validation Gatekeeper",
    desc: "Enforces exact verbatim text match. Drops ungrounded facts.",
    badgeClass: "bg-emerald-100 text-emerald-950 border-emerald-400 font-bold",
    cardClass: "border-emerald-200 bg-emerald-50/30",
  },
  benchmark_projection: {
    label: "Benchmark Scorer View",
    desc: "Projects internal ledger into final benchmark metrics (Purist/Pragmatic/F1).",
    badgeClass: "bg-purple-100 text-purple-950 border-purple-300 font-semibold",
    cardClass: "border-purple-200 bg-purple-50/30",
  },
};

export default function IsometricInspector() {
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);

  const activeCase = useIsometricStore(getActiveCase);
  const activeRun = useIsometricStore(getActiveRun);
  const activeObs = useIsometricStore(getActiveObservation);
  const activeManifest = useIsometricStore(getActiveManifest);

  const stageManifest = activeObs
    ? getStageManifest(activeManifest, activeObs.stage_id)
    : undefined;

  const effectMeta = activeObs
    ? EFFECT_STYLES[activeObs.effect_class] || {
        label: activeObs.effect_class,
        desc: "",
        badgeClass: "bg-surface-raised text-foreground border-border",
        cardClass: "border-border bg-surface",
      }
    : null;

  // Format delta snippet for clean display
  const deltaSummary = useMemo(() => {
    if (!activeObs || !activeObs.changed) return null;

    const clean = (val: string) => {
      let v = val.trim();
      if (v.startsWith("[") && v.endsWith("]")) {
        try {
          const arr = JSON.parse(v);
          if (Array.isArray(arr)) {
            return arr.map((item) => (typeof item === "string" ? item : JSON.stringify(item)));
          }
        } catch {
          // fallback
        }
      }
      return [v];
    };

    const beforeList = clean(activeObs.input);
    const afterList = clean(activeObs.output);

    return { beforeList, afterList };
  }, [activeObs]);

  if (!activeRun || !activeObs) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-muted">
        <p className="text-xs font-medium">Select a pipeline station to inspect its transformation trace.</p>
      </div>
    );
  }

  const ownerIcon =
    activeObs.owner === "model" ? (
      <Cpu className="h-3.5 w-3.5 text-sky-600 shrink-0" />
    ) : activeObs.owner === "scorer" ? (
      <Scale className="h-3.5 w-3.5 text-purple-600 shrink-0" />
    ) : (
      <Binary className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
    );

  return (
    <div className="flex h-full w-full flex-col border-l border-border bg-surface">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border bg-surface-raised px-4 py-3">
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-surface border border-border shadow-2xs shrink-0">
            <Activity className="h-3.5 w-3.5 text-deterministic" />
          </div>
          <div className="min-w-0">
            <h3 className="font-mono text-xs font-bold text-foreground truncate">
              {activeObs.stage_name}
            </h3>
            <span className="font-mono text-[10px] text-muted truncate block">
              {activeObs.stage_id}
            </span>
          </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        {/* Effect Class & Ownership Banner */}
        {effectMeta && (
          <div className={`rounded-lg border p-3 shadow-2xs ${effectMeta.cardClass}`}>
            <div className="flex items-center justify-between gap-2">
              <span className={`rounded-full border px-2.5 py-0.5 font-mono text-[10px] ${effectMeta.badgeClass}`}>
                {effectMeta.label}
              </span>
              <span className="flex items-center gap-1.5 font-mono text-[11px] font-semibold text-foreground/80 shrink-0">
                {ownerIcon}
                <span className="capitalize">{activeObs.owner}</span>
              </span>
            </div>
            <p className="mt-2 text-[11px] leading-snug text-foreground/85">
              {effectMeta.desc}
            </p>
          </div>
        )}

        {/* Hero State Transformation Delta */}
        <div className="rounded-lg border border-border bg-surface-raised p-3.5 shadow-xs">
          <div className="flex items-center justify-between gap-2 mb-2">
            <span className="font-bold text-foreground text-xs">Transformation Delta</span>
            <span
              className={`rounded-full px-2.5 py-0.5 font-mono text-[10px] font-bold ${
                activeObs.changed
                  ? "bg-amber-100 border border-amber-300 text-amber-900 shadow-2xs"
                  : "bg-surface border border-border text-muted"
              }`}
            >
              {activeObs.changed ? "★ State Mutated" : "Passthrough"}
            </span>
          </div>

          {activeObs.changed && deltaSummary ? (
            <div className="rounded-md border border-amber-300/90 bg-amber-50/70 p-3 text-xs text-amber-950 shadow-2xs space-y-2">
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 sm:gap-3">
                {/* Before side */}
                <div className="rounded border border-amber-200 bg-white/70 p-2">
                  <span className="font-mono text-[9px] uppercase font-extrabold text-amber-800/90 block mb-1">
                    Before
                  </span>
                  <div className="space-y-1">
                    {deltaSummary.beforeList.map((item, idx) => (
                      <p key={idx} className="font-mono text-[11px] text-amber-950 font-medium leading-tight">
                        {item}
                      </p>
                    ))}
                  </div>
                </div>

                {/* After side */}
                <div className="rounded border border-emerald-200 bg-white/70 p-2">
                  <span className="font-mono text-[9px] uppercase font-extrabold text-emerald-800/90 block mb-1">
                    After (Repaired)
                  </span>
                  <div className="space-y-1">
                    {deltaSummary.afterList.map((item, idx) => (
                      <p key={idx} className="font-mono text-[11px] text-emerald-950 font-bold leading-tight">
                        {item}
                      </p>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex items-center gap-2 rounded bg-surface p-2 border border-border/60 text-[11px] text-muted">
              <CheckCircle className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
              <span>Input payload validated directly without mutations.</span>
            </div>
          )}
        </div>

        {/* Narrative / Context Callout */}
        {activeObs.note && (
          <div className="rounded-lg border-l-3 border-deterministic/70 border border-border bg-surface p-3 shadow-xs">
            <div className="flex items-center gap-1.5 font-bold text-foreground text-xs mb-1">
              <Lightbulb className="h-3.5 w-3.5 text-amber-600 shrink-0" />
              <span>Mechanism Note</span>
            </div>
            <p className="text-[11.5px] text-foreground/90 leading-relaxed">
              {activeObs.note}
            </p>
          </div>
        )}

        {/* Formatted Payloads (Input / Output) */}
        <div className="space-y-3">
          <FormattedPayloadViewer label="Input Data Stream" raw={activeObs.input} />
          <FormattedPayloadViewer label="Output Result" raw={activeObs.output} />
        </div>

        {/* Collapsible Research & Technical Meta */}
        {stageManifest && (
          <div className="rounded-lg border border-border bg-surface-raised overflow-hidden shadow-xs">
            <button
              onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
              className="flex w-full items-center justify-between px-3.5 py-2.5 text-left font-medium text-foreground hover:bg-surface transition-colors"
            >
              <div className="flex items-center gap-2 text-xs font-semibold">
                <FlaskConical className="h-3.5 w-3.5 text-deterministic" />
                <span>Verification & Code Contract</span>
              </div>
              {showTechnicalDetails ? (
                <ChevronDown className="h-4 w-4 text-muted" />
              ) : (
                <ChevronRight className="h-4 w-4 text-muted" />
              )}
            </button>

            {showTechnicalDetails && (
              <div className="border-t border-border p-3.5 space-y-2.5 text-[11px] bg-surface">
                <div>
                  <span className="font-mono text-[9px] font-bold uppercase tracking-wider text-muted block">
                    Governing Test:
                  </span>
                  <p className="font-mono text-foreground font-medium break-all mt-0.5">
                    {stageManifest.governing_test}
                  </p>
                </div>
                <div>
                  <span className="font-mono text-[9px] font-bold uppercase tracking-wider text-muted block">
                    Implementation Symbol:
                  </span>
                  <p className="font-mono text-foreground font-medium break-all mt-0.5">
                    {stageManifest.implementation.symbol}
                  </p>
                </div>
                {stageManifest.paper_wording && (
                  <div>
                    <span className="font-mono text-[9px] font-bold uppercase tracking-wider text-muted block">
                      Paper Wording:
                    </span>
                    <p className="text-foreground/90 mt-0.5 leading-snug">
                      {stageManifest.paper_wording}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Final Method Result Card */}
        <div className="rounded-lg border border-border bg-surface-raised p-3.5 shadow-xs">
          <div className="flex items-center justify-between text-xs font-semibold text-foreground">
            <span>Overall Method Verdict</span>
            {activeRun.correct !== null && (
              <span
                className={`flex items-center gap-1 font-mono text-[10px] font-bold ${
                  activeRun.correct ? "text-success" : "text-error"
                }`}
              >
                {activeRun.correct ? (
                  <>
                    <CheckCircle className="h-3.5 w-3.5" />
                    <span>CORRECT</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-3.5 w-3.5" />
                    <span>MISMATCH</span>
                  </>
                )}
              </span>
            )}
          </div>
          <p className="mt-1.5 font-mono text-sm font-bold text-foreground">
            {activeRun.final_answer}
          </p>
          {activeRun.correctness_note && (
            <p className="mt-1 text-[10px] text-muted leading-tight">
              {activeRun.correctness_note}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
