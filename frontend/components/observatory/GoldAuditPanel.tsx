"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  ChevronRight,
  HelpCircle,
  PanelLeftClose,
  PanelLeftOpen,
  X,
} from "lucide-react";
import {
  fetchGoldAuditRows,
  fetchGoldAuditDecisions,
  postGoldAuditDecision,
  fetchRecord,
} from "@/lib/api";
import type { GoldAuditRow, GoldAuditDecision, FullRecordResponse } from "@/lib/types";
import LetterRenderer from "./LetterRenderer";

const SIMPLE_CLASSES = [
  { value: "correct" as const, label: "Correct", shortcut: "1", color: "border-success text-success bg-success/10" },
  { value: "ambiguous" as const, label: "Ambiguous", shortcut: "2", color: "border-llm text-llm bg-llm/10" },
  { value: "wrong" as const, label: "Wrong", shortcut: "3", color: "border-error text-error bg-error/10" },
];

function classBadgeStyle(c: string): string {
  switch (c) {
    case "correct":
      return "bg-success/10 text-success border-success/20";
    case "ambiguous":
      return "bg-llm/10 text-llm border-llm/20";
    case "wrong":
      return "bg-error/10 text-error border-error/20";
    default:
      return "bg-surface-raised text-muted border-border";
  }
}

function parseBool(v: string | boolean | undefined): boolean {
  if (typeof v === "boolean") return v;
  if (typeof v === "string") return v.toLowerCase() === "true";
  return false;
}

function extractCoreContext(context: string): string {
  let core = context.trim();
  if (core.startsWith("...")) core = core.slice(3);
  if (core.endsWith("...")) core = core.slice(0, -3);
  return core.trim();
}

function findHighlightSpans(noteText: string, referenceContext: string): { start: number; end: number; kind: "gold"; label: string }[] {
  const core = extractCoreContext(referenceContext);
  if (!core || core.length < 10) return [];
  let idx = noteText.indexOf(core);
  if (idx >= 0) {
    return [{ start: idx, end: idx + core.length, kind: "gold", label: "Gold reference context" }];
  }
  const lowerNote = noteText.toLowerCase();
  const lowerCore = core.toLowerCase();
  idx = lowerNote.indexOf(lowerCore);
  if (idx >= 0) {
    return [{ start: idx, end: idx + core.length, kind: "gold", label: "Gold reference context" }];
  }
  const firstSentence = core.split(/[.!?]/)[0];
  if (firstSentence && firstSentence.length > 15) {
    idx = lowerNote.indexOf(firstSentence.toLowerCase());
    if (idx >= 0) {
      return [{ start: idx, end: idx + firstSentence.length, kind: "gold", label: "Gold reference context" }];
    }
  }
  return [];
}

export default function GoldAuditPanel() {
  const queryClient = useQueryClient();
  const [mode, setMode] = useState<"adjudicate" | "review">("adjudicate");
  const [queueOpen, setQueueOpen] = useState(false);
  const [currentSourceRowIndex, setCurrentSourceRowIndex] = useState<number | null>(null);
  const [simpleClass, setSimpleClass] = useState<"correct" | "ambiguous" | "wrong" | null>(null);
  const [notes, setNotes] = useState("");
  const [correctedGoldLabel, setCorrectedGoldLabel] = useState("");

  const { data: rowsData, isLoading: rowsLoading } = useQuery({
    queryKey: ["gold-audit-rows"],
    queryFn: () => fetchGoldAuditRows("validation"),
  });

  const { data: decisionsData, isLoading: decisionsLoading } = useQuery({
    queryKey: ["gold-audit-decisions"],
    queryFn: () => fetchGoldAuditDecisions("validation"),
  });

  const decisionsMap = useMemo(() => {
    const map = new Map<number, GoldAuditDecision>();
    if (decisionsData?.decisions) {
      for (const d of decisionsData.decisions) {
        map.set(d.source_row_index, d);
      }
    }
    return map;
  }, [decisionsData]);

  const allRows = rowsData?.rows ?? [];

  const sortedRows = useMemo(() => {
    const list = [...allRows];
    list.sort((a, b) => {
      const aDone = decisionsMap.has(Number(a.source_row_index));
      const bDone = decisionsMap.has(Number(b.source_row_index));
      if (aDone !== bDone) return aDone ? 1 : -1;
      return (b.priority_score ?? 0) - (a.priority_score ?? 0);
    });
    return list;
  }, [allRows, decisionsMap]);

  const reviewRows = useMemo(() => {
    return sortedRows.filter((r) => {
      const d = decisionsMap.get(Number(r.source_row_index));
      return d && (d.simple_class === "ambiguous" || d.simple_class === "wrong");
    });
  }, [sortedRows, decisionsMap]);

  const visibleRows = mode === "review" ? reviewRows : sortedRows;

  const currentRow: GoldAuditRow | undefined = useMemo(() => {
    if (currentSourceRowIndex == null) {
      const first = visibleRows.find((r) => !decisionsMap.has(Number(r.source_row_index)));
      return first ?? visibleRows[0];
    }
    return visibleRows.find((r) => Number(r.source_row_index) === currentSourceRowIndex);
  }, [visibleRows, currentSourceRowIndex, decisionsMap]);

  useEffect(() => {
    if (currentRow && currentSourceRowIndex == null) {
      setCurrentSourceRowIndex(Number(currentRow.source_row_index));
    }
  }, [currentRow, currentSourceRowIndex]);

  const { data: fullRecord } = useQuery<FullRecordResponse>({
    queryKey: ["record", "validation", currentRow?.source_row_index],
    queryFn: () => fetchRecord("validation", Number(currentRow!.source_row_index)),
    enabled: !!currentRow,
  });

  useEffect(() => {
    if (!currentRow) {
      setSimpleClass(null);
      setNotes("");
      setCorrectedGoldLabel("");
      return;
    }
    const existing = decisionsMap.get(Number(currentRow.source_row_index));
    if (existing) {
      setSimpleClass(existing.simple_class);
      setNotes(existing.notes ?? "");
      setCorrectedGoldLabel(existing.corrected_gold_label ?? "");
    } else {
      setSimpleClass(null);
      setNotes("");
      setCorrectedGoldLabel("");
    }
  }, [currentRow, decisionsMap]);

  const saveMutation = useMutation({
    mutationFn: postGoldAuditDecision,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gold-audit-decisions"] });
      queryClient.invalidateQueries({ queryKey: ["gold-audit-rows"] });
      setCurrentSourceRowIndex(null);
    },
  });

  const goNext = useCallback(() => {
    if (!currentRow) return;
    const idx = visibleRows.findIndex((r) => Number(r.source_row_index) === Number(currentRow.source_row_index));
    if (idx >= 0 && idx < visibleRows.length - 1) {
      setCurrentSourceRowIndex(Number(visibleRows[idx + 1].source_row_index));
    }
  }, [currentRow, visibleRows]);

  const handleSave = useCallback(() => {
    if (!currentRow || !simpleClass) return;
    const decision: GoldAuditDecision = {
      source_row_index: Number(currentRow.source_row_index),
      split: currentRow.split,
      simple_class: simpleClass,
      rq10_class: null,
      notes,
      corrected_gold_label: correctedGoldLabel || null,
      benchmark_convention_flag: false,
      all_system_fail: false,
      exact_evidence_but_scorer_wrong: false,
      clinically_defensible_alternative: false,
      likely_gold_defect: false,
    };
    saveMutation.mutate(decision);
  }, [currentRow, simpleClass, notes, correctedGoldLabel, saveMutation]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key >= "1" && e.key <= "3" && !e.ctrlKey && !e.metaKey && !e.altKey) {
        const idx = parseInt(e.key, 10) - 1;
        if (idx < SIMPLE_CLASSES.length) {
          e.preventDefault();
          setSimpleClass(SIMPLE_CLASSES[idx].value);
        }
        return;
      }
      if (e.key === "Enter" && !e.ctrlKey && !e.metaKey && !e.altKey && simpleClass) {
        e.preventDefault();
        handleSave();
        return;
      }
      if (e.key === "ArrowRight" || e.key === "j" || e.key === "J") {
        e.preventDefault();
        goNext();
        return;
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave, goNext, simpleClass]);

  const highlights = useMemo(() => {
    if (!fullRecord?.note_text || !currentRow?.reference_context) return [];
    return findHighlightSpans(fullRecord.note_text, currentRow.reference_context);
  }, [fullRecord, currentRow]);

  const total = rowsData?.total ?? 0;
  const decided = decisionsMap.size;
  const progress = total > 0 ? decided / total : 0;
  const reviewCount = reviewRows.length;
  const samplingModel = rowsData?.sampling_model;

  if (rowsLoading || decisionsLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading gold audit queue…</p>
      </div>
    );
  }

  if (!currentRow) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">
          {mode === "review" ? "No ambiguous or wrong rows to review." : "No rows available."}
        </p>
      </div>
    );
  }

  const sri = Number(currentRow.source_row_index);
  const isDone = decisionsMap.has(sri);
  const existing = decisionsMap.get(sri);

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Top bar */}
      <div className="flex items-center gap-3 border-b border-border bg-surface px-4 py-2">
        <button
          onClick={() => setQueueOpen((v) => !v)}
          className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors ${
            queueOpen ? "border-llm/30 bg-llm/10 text-llm" : "border-border bg-surface text-muted hover:text-foreground"
          }`}
        >
          {queueOpen ? <PanelLeftClose className="h-3.5 w-3.5" /> : <PanelLeftOpen className="h-3.5 w-3.5" />}
        </button>

        {/* Mode switcher */}
        <div className="flex items-center rounded-md border border-border bg-surface-raised overflow-hidden">
          <button
            onClick={() => { setMode("adjudicate"); setCurrentSourceRowIndex(null); }}
            className={`px-3 py-1.5 text-[10px] font-medium transition-colors ${
              mode === "adjudicate" ? "bg-surface text-foreground" : "text-muted hover:text-foreground"
            }`}
          >
            Adjudicate
          </button>
          <button
            onClick={() => { setMode("review"); setCurrentSourceRowIndex(null); }}
            className={`px-3 py-1.5 text-[10px] font-medium transition-colors ${
              mode === "review" ? "bg-surface text-foreground" : "text-muted hover:text-foreground"
            }`}
          >
            Review ({reviewCount})
          </button>
        </div>

        <div className="flex-1">
          <div className="h-2 w-full overflow-hidden rounded-full bg-surface-raised">
            <div className="h-full rounded-full bg-llm transition-all" style={{ width: `${progress * 100}%` }} />
          </div>
          <div className="mt-0.5 flex justify-between text-[10px] text-muted">
            <span>{decided} / {total}</span>
            <span>{(progress * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="flex items-center gap-1.5 text-[11px] text-muted">
          <span className="font-mono">#{sri}</span>
          {currentRow.predicted_simple_class && (
            <span
              className={`rounded border px-1.5 py-0 text-[9px] font-medium ${classBadgeStyle(currentRow.predicted_simple_class)}`}
              title={currentRow.active_learning_reason}
            >
              model {currentRow.predicted_simple_class}{" "}
              {Math.round((currentRow.prediction_confidence ?? 0) * 100)}%
            </span>
          )}
          {isDone && (
            <span className={`rounded border px-1.5 py-0 text-[9px] font-medium ${classBadgeStyle(existing?.simple_class ?? "")}`}>
              {existing?.simple_class}
            </span>
          )}
        </div>

        {samplingModel && (
          <div
            className={`hidden items-center rounded-md border px-2 py-1 text-[10px] font-medium md:flex ${
              samplingModel.is_calibrated_enough
                ? "border-success/20 bg-success/10 text-success"
                : "border-border bg-surface-raised text-muted"
            }`}
            title={samplingModel.claim_language}
          >
            {samplingModel.decision_count} labels
          </div>
        )}

        {/* Class toggle legend */}
        <div className="flex items-center gap-1">
          {SIMPLE_CLASSES.map((c) => {
            const active = simpleClass === c.value;
            const Icon = c.value === "correct" ? Check : c.value === "wrong" ? X : HelpCircle;
            return (
              <button
                key={c.value}
                onClick={() => setSimpleClass(c.value)}
                className={`flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-[11px] font-medium transition-all duration-200 ease-out hover:scale-[1.03] active:scale-[0.97] ${
                  active
                    ? `${c.color} shadow-sm`
                    : "border-border bg-surface text-muted hover:text-foreground hover:bg-surface-raised"
                }`}
                title={`${c.label} (${c.shortcut})`}
              >
                <Icon className="h-3.5 w-3.5" />
                <span className="hidden sm:inline">{c.label}</span>
                <span className="rounded px-1 py-0 text-[9px] font-mono opacity-70">{c.shortcut}</span>
              </button>
            );
          })}
        </div>

        <button
          onClick={goNext}
          disabled={visibleRows.findIndex((r) => Number(r.source_row_index) === sri) >= visibleRows.length - 1}
          className="flex items-center gap-1 rounded-md border border-border bg-surface px-2 py-1.5 text-[10px] font-medium text-muted hover:text-foreground disabled:opacity-30"
        >
          Next <ChevronRight className="h-3 w-3" />
        </button>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Collapsible queue drawer */}
        {queueOpen && (
          <div className="flex w-[240px] flex-col border-r border-border bg-surface">
            <div className="flex items-center justify-between border-b border-border px-3 py-2">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Queue ({visibleRows.length})
              </span>
              <button onClick={() => setQueueOpen(false)} className="rounded p-1 text-muted hover:bg-surface-raised hover:text-foreground">
                <PanelLeftClose className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              {visibleRows.map((row) => {
                const rowSri = Number(row.source_row_index);
                const active = sri === rowSri;
                const done = decisionsMap.has(rowSri);
                const d = decisionsMap.get(rowSri);
                return (
                  <button
                    key={rowSri}
                    onClick={() => setCurrentSourceRowIndex(rowSri)}
                    className={`w-full border-b border-border pl-3 pr-3 py-2 text-left transition-all border-l-2 ${
                      active ? "bg-llm/5 border-l-llm" : "hover:bg-surface-raised border-l-transparent"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-muted">#{rowSri}</span>
                      {done ? (
                        <span className={`flex items-center gap-0.5 rounded border px-1 py-0 text-[9px] font-medium ${classBadgeStyle(d?.simple_class ?? "")}`}>
                          <Check className="h-2.5 w-2.5" /> {d?.simple_class}
                        </span>
                      ) : (
                        <span className="h-2 w-2 rounded-full border border-border" />
                      )}
                      <span className="flex-1 truncate text-[11px] font-medium text-foreground">{row.gold_label}</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {/* Center: letter */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-5xl space-y-4 p-5 pb-8">
              {/* Gold metadata header */}
              <div className="sticky top-0 bg-background/80 backdrop-blur-md z-10 flex items-start justify-between gap-4 border-b border-border pb-3 pt-2 px-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-semibold text-foreground">{currentRow.gold_label}</h2>
                    {isDone && (
                      <span className={`flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium ${classBadgeStyle(existing?.simple_class ?? "")}`}>
                        <Check className="h-3 w-3" /> Reviewed
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-muted">{currentRow.gold_reference}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-muted">Kind: <span className="text-foreground">{currentRow.gold_label_kind}</span></p>
                  <p className="text-[10px] text-muted">Ref found: <span className={parseBool(currentRow.reference_found_in_note) ? "text-success" : "text-error"}>{parseBool(currentRow.reference_found_in_note) ? "Yes" : "No"}</span></p>
                </div>
              </div>

              <LetterRenderer
                text={fullRecord?.note_text ?? currentRow.note_text_single_line.replace(/\\n/g, "\n")}
                highlights={highlights}
              />
            </div>
          </div>
        </div>

        {/* Review mode: dominant right sidebar */}
        {mode === "review" && (
          <div className="flex w-[340px] flex-col border-l border-border bg-surface">
            <div className="border-b border-border px-4 py-3">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
                Review notes
              </h3>
              <p className="mt-0.5 text-[10px] text-muted">
                Row #{sri} — {currentRow.gold_label}
              </p>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                  Why is this ambiguous or wrong?
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  placeholder="Describe the issue…"
                  className="h-40 w-full resize-none rounded-lg border border-border bg-surface px-3 py-2 text-[12px] text-foreground placeholder:text-muted focus:border-deterministic focus:outline-none"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                  Corrected gold label
                </label>
                <input
                  type="text"
                  value={correctedGoldLabel}
                  onChange={(e) => setCorrectedGoldLabel(e.target.value)}
                  placeholder="What should the gold label be?"
                  className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-[12px] text-foreground placeholder:text-muted focus:border-deterministic focus:outline-none"
                />
              </div>

              <div className="rounded-lg border border-border bg-surface-raised p-3 space-y-1">
                <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">Row metadata</p>
                <div className="flex justify-between text-[10px]">
                  <span className="text-muted">Kind</span>
                  <span className="text-foreground">{currentRow.gold_label_kind}</span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-muted">Monthly freq</span>
                  <span className="text-foreground">{Number(currentRow.gold_monthly_frequency).toFixed(2)}</span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-muted">Yearly bounds</span>
                  <span className="text-foreground">{currentRow.gold_yearly_bounds}</span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-muted">Ref found</span>
                  <span className={parseBool(currentRow.reference_found_in_note) ? "text-success" : "text-error"}>
                    {parseBool(currentRow.reference_found_in_note) ? "Yes" : "No"}
                  </span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-muted">Heuristic</span>
                  <span className={currentRow.codex_initial_ambiguity_label === "ambiguous" ? "text-error" : "text-success"}>
                    {currentRow.codex_initial_ambiguity_label}
                  </span>
                </div>
              </div>
            </div>

            <div className="border-t border-border p-3">
              <button
                onClick={handleSave}
                disabled={!simpleClass || saveMutation.isPending}
                className="w-full rounded-lg bg-deterministic px-3 py-2.5 text-sm font-medium text-white transition-all duration-200 ease-out hover:scale-[1.01] active:scale-[0.99] hover:bg-deterministic/90 disabled:opacity-40"
              >
                {saveMutation.isPending ? "Saving…" : "Save & next"}
              </button>
              {saveMutation.isError && (
                <p className="mt-2 text-center text-[10px] text-error">
                  Error saving: {String(saveMutation.error)}
                </p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
