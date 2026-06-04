"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  ChevronLeft,
  ChevronRight,
  HelpCircle,
  List,
  PanelLeftClose,
  PanelLeftOpen,
  Save,
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
  { value: "correct" as const, label: "Correct", shortcut: "1", color: "bg-success hover:bg-success/90", text: "text-white", icon: Check },
  { value: "ambiguous" as const, label: "Ambiguous", shortcut: "2", color: "bg-llm hover:bg-llm/90", text: "text-white", icon: HelpCircle },
  { value: "wrong" as const, label: "Wrong", shortcut: "3", color: "bg-error hover:bg-error/90", text: "text-white", icon: X },
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
  const [queueOpen, setQueueOpen] = useState(false);
  const [currentSourceRowIndex, setCurrentSourceRowIndex] = useState<number | null>(null);
  const [simpleClass, setSimpleClass] = useState<"correct" | "ambiguous" | "wrong" | null>(null);
  const [notes, setNotes] = useState("");
  const [correctedGoldLabel, setCorrectedGoldLabel] = useState("");
  const [showMore, setShowMore] = useState(false);

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

  const currentRow: GoldAuditRow | undefined = useMemo(() => {
    if (currentSourceRowIndex == null) {
      // Auto-select first un-audited row on initial load
      const first = sortedRows.find((r) => !decisionsMap.has(Number(r.source_row_index)));
      return first ?? sortedRows[0];
    }
    return sortedRows.find((r) => Number(r.source_row_index) === currentSourceRowIndex);
  }, [sortedRows, currentSourceRowIndex, decisionsMap]);

  // Sync currentSourceRowIndex when currentRow changes from auto-select
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

  // Load existing decision into form when row changes
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
    },
  });

  const goNext = useCallback(() => {
    if (!currentRow) return;
    const idx = sortedRows.findIndex((r) => Number(r.source_row_index) === Number(currentRow.source_row_index));
    if (idx >= 0 && idx < sortedRows.length - 1) {
      setCurrentSourceRowIndex(Number(sortedRows[idx + 1].source_row_index));
    }
  }, [currentRow, sortedRows]);

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
    saveMutation.mutate(decision, {
      onSuccess: () => {
        goNext();
      },
    });
  }, [currentRow, simpleClass, notes, correctedGoldLabel, saveMutation, goNext]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const isTyping =
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable);

      // Number keys 1-3 select simple class (only when not typing)
      if (e.key >= "1" && e.key <= "3" && !e.ctrlKey && !e.metaKey && !e.altKey && !isTyping) {
        const idx = parseInt(e.key, 10) - 1;
        if (idx < SIMPLE_CLASSES.length) {
          e.preventDefault();
          setSimpleClass(SIMPLE_CLASSES[idx].value);
        }
        return;
      }
      // Cmd/Ctrl+Enter save
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        handleSave();
        return;
      }
      // Arrow keys navigate (only when not typing)
      if (!isTyping) {
        if (e.key === "ArrowRight" || e.key === "j" || e.key === "J") {
          e.preventDefault();
          goNext();
          return;
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave, goNext]);

  const highlights = useMemo(() => {
    if (!fullRecord?.note_text || !currentRow?.reference_context) return [];
    return findHighlightSpans(fullRecord.note_text, currentRow.reference_context);
  }, [fullRecord, currentRow]);

  const total = rowsData?.total ?? 0;
  const decided = decisionsMap.size;
  const progress = total > 0 ? decided / total : 0;

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
        <p className="text-sm font-medium">No rows available.</p>
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
          {isDone && (
            <span className={`rounded border px-1.5 py-0 text-[9px] font-medium ${classBadgeStyle(existing?.simple_class ?? "")}`}>
              {existing?.simple_class}
            </span>
          )}
        </div>

        <button
          onClick={goNext}
          disabled={sortedRows.findIndex((r) => Number(r.source_row_index) === sri) >= sortedRows.length - 1}
          className="flex items-center gap-1 rounded-md border border-border bg-surface px-2 py-1 text-[10px] font-medium text-muted hover:text-foreground disabled:opacity-30"
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
                Queue ({sortedRows.length})
              </span>
              <button onClick={() => setQueueOpen(false)} className="rounded p-1 text-muted hover:bg-surface-raised hover:text-foreground">
                <PanelLeftClose className="h-3.5 w-3.5" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto">
              {sortedRows.map((row) => {
                const rowSri = Number(row.source_row_index);
                const active = sri === rowSri;
                const done = decisionsMap.has(rowSri);
                const d = decisionsMap.get(rowSri);
                return (
                  <button
                    key={rowSri}
                    onClick={() => setCurrentSourceRowIndex(rowSri)}
                    className={`w-full border-b border-border px-3 py-2 text-left transition-colors ${
                      active ? "bg-llm/5" : "hover:bg-surface-raised"
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] font-mono text-muted">#{rowSri}</span>
                      {done ? (
                        <span className={`rounded px-1 py-0 text-[9px] font-medium ${classBadgeStyle(d?.simple_class ?? "")}`}>
                          {d?.simple_class}
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

        {/* Center: letter + decision buttons */}
        <div className="flex flex-1 flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            <div className="mx-auto max-w-3xl space-y-4 p-5 pb-8">
              {/* Gold metadata header */}
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h2 className="text-lg font-semibold text-foreground">{currentRow.gold_label}</h2>
                  <p className="text-sm text-muted">{currentRow.gold_reference}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-muted">Kind: <span className="text-foreground">{currentRow.gold_label_kind}</span></p>
                  <p className="text-[10px] text-muted">Ref found: <span className={parseBool(currentRow.reference_found_in_note) ? "text-success" : "text-error"}>{parseBool(currentRow.reference_found_in_note) ? "Yes" : "No"}</span></p>
                </div>
              </div>

              {/* Letter */}
              <LetterRenderer
                text={fullRecord?.note_text ?? currentRow.note_text_single_line.replace(/\\n/g, "\n")}
                highlights={highlights}
              />
            </div>
          </div>

          {/* Decision bar — fixed at bottom */}
          <div className="border-t border-border bg-surface p-4">
            <div className="mx-auto max-w-3xl space-y-3">
              {/* Big three buttons */}
              <div className="grid grid-cols-3 gap-3">
                {SIMPLE_CLASSES.map((c) => {
                  const active = simpleClass === c.value;
                  const Icon = c.icon;
                  return (
                    <button
                      key={c.value}
                      onClick={() => setSimpleClass(c.value)}
                      className={`flex flex-col items-center justify-center gap-1.5 rounded-xl border-2 px-4 py-4 transition-all ${
                        active
                          ? `${c.color} border-transparent shadow-md`
                          : "border-border bg-surface-raised hover:bg-surface text-foreground"
                      }`}
                    >
                      <Icon className={`h-6 w-6 ${active ? c.text : "text-muted"}`} />
                      <span className={`text-sm font-semibold ${active ? c.text : "text-foreground"}`}>{c.label}</span>
                      <span className={`rounded px-1 py-0 text-[9px] font-mono ${active ? "bg-white/20 text-white" : "bg-surface text-muted"}`}>
                        {c.shortcut}
                      </span>
                    </button>
                  );
                })}
              </div>

              {/* Save row */}
              <div className="flex items-center gap-3">
                <button
                  onClick={handleSave}
                  disabled={!simpleClass || saveMutation.isPending}
                  className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-deterministic px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-deterministic/90 disabled:opacity-40"
                >
                  {saveMutation.isPending ? (
                    <span>Saving…</span>
                  ) : (
                    <>
                      <Save className="h-4 w-4" />
                      Save & next
                      <span className="rounded bg-white/20 px-1.5 py-0 text-[10px]">⌘Enter</span>
                    </>
                  )}
                </button>

                <button
                  onClick={() => setShowMore((v) => !v)}
                  className="rounded-lg border border-border bg-surface px-3 py-2.5 text-[11px] font-medium text-muted hover:text-foreground"
                >
                  {showMore ? "Hide options" : "More options"}
                </button>
              </div>

              {/* Optional expanded options */}
              {showMore && (
                <div className="space-y-3 rounded-xl border border-border bg-surface-raised p-4">
                  <div className="space-y-1.5">
                    <label className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                      Adjudication notes
                    </label>
                    <textarea
                      value={notes}
                      onChange={(e) => setNotes(e.target.value)}
                      placeholder="Why this judgment? Any observations…"
                      className="h-20 w-full resize-none rounded-lg border border-border bg-surface px-3 py-2 text-[11px] text-foreground placeholder:text-muted focus:border-deterministic focus:outline-none"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                      Corrected gold label (optional)
                    </label>
                    <input
                      type="text"
                      value={correctedGoldLabel}
                      onChange={(e) => setCorrectedGoldLabel(e.target.value)}
                      placeholder="If gold should be different…"
                      className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-[11px] text-foreground placeholder:text-muted focus:border-deterministic focus:outline-none"
                    />
                  </div>


                </div>
              )}

              {saveMutation.isError && (
                <p className="text-center text-[10px] text-error">
                  Error saving: {String(saveMutation.error)}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
