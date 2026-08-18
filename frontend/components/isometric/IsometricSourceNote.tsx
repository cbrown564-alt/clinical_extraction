"use client";

import React, { useState, useMemo } from "react";
import {
  FileText,
  Award,
  AlertTriangle,
  ShieldCheck,
  BookOpen,
  HelpCircle,
} from "lucide-react";
import {
  useIsometricStore,
  getActiveCase,
  getActiveRun,
  getActiveObservation,
} from "@/lib/isometricStore";

export default function IsometricSourceNote() {
  const [activeTab, setActiveTab] = useState<"mechanism" | "gold_policy" | "methods">("mechanism");

  const activeCase = useIsometricStore(getActiveCase);
  const activeRun = useIsometricStore(getActiveRun);
  const activeObs = useIsometricStore(getActiveObservation);

  // Parse and highlight matching spans in the letter text
  const highlightedContent = useMemo(() => {
    if (!activeCase) return null;
    const noteText = activeCase.note_text;
    const goldRef = activeCase.gold_reference;

    let targetSpan = goldRef;
    if (!targetSpan && activeCase.gold) {
      targetSpan = activeCase.gold;
    }

    if (!targetSpan || !noteText.includes(targetSpan)) {
      return <span className="text-foreground">{noteText}</span>;
    }

    const parts = noteText.split(targetSpan);
    return (
      <span className="text-foreground">
        {parts.map((part, i) => (
          <React.Fragment key={i}>
            {part}
            {i < parts.length - 1 && (
              <mark className="rounded bg-amber-200/90 text-amber-950 px-1.5 py-0.5 font-bold ring-1 ring-amber-500/50 shadow-2xs transition-all">
                {targetSpan}
              </mark>
            )}
          </React.Fragment>
        ))}
      </span>
    );
  }, [activeCase]);

  if (!activeCase) {
    return (
      <div className="flex h-full items-center justify-center p-6 text-muted">
        <p className="text-xs font-medium">No clinical letter loaded.</p>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col border-r border-border bg-surface">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border bg-surface-raised px-4 py-3">
        <div className="flex items-center gap-2.5">
          <div className="flex h-6 w-6 items-center justify-center rounded-md bg-surface border border-border shadow-2xs shrink-0">
            <FileText className="h-3.5 w-3.5 text-deterministic" />
          </div>
          <span className="font-mono text-xs font-bold text-foreground">
            {activeCase.letter_id}
          </span>
        </div>
        <span className="rounded-md border border-border bg-surface px-2.5 py-0.5 font-mono text-[10px] font-bold text-muted">
          {activeCase.task_label}
        </span>
      </div>

      {/* Scrollable Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
        {/* Benchmark Gold Reference Card (Top Hero) */}
        <div className="rounded-lg border border-emerald-300/80 bg-emerald-50/80 p-3.5 shadow-2xs">
          <div className="flex items-center justify-between gap-2">
            <span className="flex items-center gap-1.5 font-bold text-emerald-900 text-xs">
              <Award className="h-4 w-4 text-emerald-700 shrink-0" />
              <span>Target Benchmark Truth</span>
            </span>
            <span className="font-mono text-xs font-extrabold text-emerald-950 bg-emerald-200/90 px-2 py-0.5 rounded shadow-2xs shrink-0">
              {activeCase.gold}
            </span>
          </div>
          {activeCase.gold_note && (
            <p className="mt-2 text-[11px] text-emerald-900/90 leading-snug">
              {activeCase.gold_note}
            </p>
          )}
        </div>

        {/* Clinical Letter Paper Document */}
        <div className="rounded-lg border border-border bg-surface-raised p-4 shadow-xs">
          <div className="flex items-center justify-between border-b border-border/80 pb-2 mb-3">
            <span className="font-mono text-[10px] font-bold uppercase tracking-wider text-muted">
              Clinical Note Document
            </span>
            <span className="font-mono text-[10px] text-muted">Original Letterhead</span>
          </div>
          <div className="whitespace-pre-wrap font-serif text-[13.5px] leading-relaxed text-foreground">
            {highlightedContent}
          </div>
        </div>

        {/* Tabbed Case Narrative & Failure Mode Context */}
        <div className="rounded-lg border border-border bg-surface overflow-hidden shadow-xs">
          {/* Tab Navigation with balanced padding and no text wrapping */}
          <div className="flex items-center border-b border-border bg-surface-raised p-1 gap-1">
            <button
              onClick={() => setActiveTab("mechanism")}
              className={`flex-1 flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-[11px] font-semibold transition-all whitespace-nowrap ${
                activeTab === "mechanism"
                  ? "bg-surface text-foreground shadow-2xs ring-1 ring-border"
                  : "text-muted hover:text-foreground"
              }`}
            >
              <AlertTriangle className="h-3.5 w-3.5 text-amber-600 shrink-0" />
              <span>Failure Mode</span>
            </button>
            <button
              onClick={() => setActiveTab("gold_policy")}
              className={`flex-1 flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-[11px] font-semibold transition-all whitespace-nowrap ${
                activeTab === "gold_policy"
                  ? "bg-surface text-foreground shadow-2xs ring-1 ring-border"
                  : "text-muted hover:text-foreground"
              }`}
            >
              <BookOpen className="h-3.5 w-3.5 text-sky-600 shrink-0" />
              <span>Gold Policy</span>
            </button>
            <button
              onClick={() => setActiveTab("methods")}
              className={`flex-1 flex items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-[11px] font-semibold transition-all whitespace-nowrap ${
                activeTab === "methods"
                  ? "bg-surface text-foreground shadow-2xs ring-1 ring-border"
                  : "text-muted hover:text-foreground"
              }`}
            >
              <HelpCircle className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
              <span>All Methods</span>
            </button>
          </div>

          {/* Tab Body */}
          <div className="p-3.5 text-xs leading-relaxed text-foreground/90">
            {activeTab === "mechanism" && (
              <div className="space-y-2">
                <span className="font-bold text-foreground text-xs block">
                  {activeCase.mechanism_title || "Why Model Alone Fails on This Letter"}
                </span>
                <p className="text-[11.5px] text-foreground/90 leading-relaxed">
                  {activeCase.mechanism || activeCase.story}
                </p>
              </div>
            )}

            {activeTab === "gold_policy" && (
              <div className="space-y-2">
                <span className="font-bold text-foreground text-xs block">
                  Benchmark Selection Convention
                </span>
                <p className="text-[11.5px] text-foreground/90 leading-relaxed">
                  {activeCase.gold_note}
                </p>
                {activeCase.gold_reference && (
                  <div className="mt-2.5 rounded-md bg-surface-raised p-2.5 font-mono text-[11px] border border-border shadow-2xs">
                    <span className="text-[9px] uppercase font-bold text-muted block mb-1">
                      Ground Reference Text Span:
                    </span>
                    <span className="text-foreground font-bold">
                      "{activeCase.gold_reference}"
                    </span>
                  </div>
                )}
              </div>
            )}

            {activeTab === "methods" && (
              <div className="space-y-2.5">
                {activeCase.card_why.rules && (
                  <div className="rounded-md border border-border p-2.5 bg-surface-raised/50 shadow-2xs">
                    <span className="font-bold text-emerald-700 text-[11px] block">
                      Deterministic Rules:
                    </span>
                    <p className="text-[11px] text-foreground/85 mt-1 leading-snug">
                      {activeCase.card_why.rules}
                    </p>
                  </div>
                )}
                {activeCase.card_why.llm && (
                  <div className="rounded-md border border-border p-2.5 bg-surface-raised/50 shadow-2xs">
                    <span className="font-bold text-sky-700 text-[11px] block">
                      LLM Alone:
                    </span>
                    <p className="text-[11px] text-foreground/85 mt-1 leading-snug">
                      {activeCase.card_why.llm}
                    </p>
                  </div>
                )}
                {activeCase.card_why.llm_with_rules && (
                  <div className="rounded-md border border-border p-2.5 bg-surface-raised/50 shadow-2xs">
                    <span className="font-bold text-amber-700 text-[11px] block">
                      LLM with Rules (Hybrid):
                    </span>
                    <p className="text-[11px] text-foreground/85 mt-1 leading-snug">
                      {activeCase.card_why.llm_with_rules}
                    </p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer / Safeguard */}
      <div className="border-t border-border bg-surface-raised px-4 py-2.5 text-[11px] flex items-center justify-between text-muted shrink-0">
        <span className="flex items-center gap-1.5 font-medium whitespace-nowrap">
          <ShieldCheck className="h-3.5 w-3.5 text-success shrink-0" />
          <span>Research Safeguard Active</span>
        </span>
        <span className="font-mono text-[10px] text-muted whitespace-nowrap">Synthetic Teaching Case</span>
      </div>
    </div>
  );
}
