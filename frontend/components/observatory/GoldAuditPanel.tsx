"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Check,
  ChevronDown,
  ChevronUp,
  Flag,
  Save,
  ShieldAlert,
  SkipForward,
  Target,
} from "lucide-react";
import {
  fetchGoldAuditRows,
  fetchGoldAuditDecisions,
  postGoldAuditDecision,
  fetchRecord,
} from "@/lib/api";
import type { GoldAuditRow, GoldAuditDecision, RQ10Class, FullRecordResponse } from "@/lib/types";
import LetterRenderer from "./LetterRenderer";

const RQ10_CLASSES: { value: RQ10Class; label: string; shortcut: string; color: string }[] = [
  { value: "true_extraction_failure", label: "True extraction failure", shortcut: "1", color: "text-error" },
  { value: "benchmark_convention_dominated", label: "Benchmark convention dominated", shortcut: "2", color: "text-llm" },
  { value: "underdetermined_note", label: "Underdetermined note", shortcut: "3", color: "text-muted" },
  { value: "clinically_defensible_alternative", label: "Clinically defensible alternative", shortcut: "4", color: "text-success" },
  { value: "possible_gold_weakness", label: "Possible gold weakness", shortcut: "5", color: "text-gold-ghost" },
  { value: "instrumentation_gap", label: "Instrumentation gap", shortcut: "6", color: "text-deterministic-alt" },
];

function classBadgeColor(c: RQ10Class): string {
  switch (c) {
    case "true_extraction_failure":
      return "bg-error/10 text-error border-error/20";
    case "benchmark_convention_dominated":
      return "bg-llm/10 text-llm border-llm/20";
    case "underdetermined_note":
      return "bg-muted/10 text-muted border-muted/20";
    case "clinically_defensible_alternative":
      return "bg-success/10 text-success border-success/20";
    case "possible_gold_weakness":
      return "bg-gold-ghost/10 text-gold-ghost border-gold-ghost/20";
    case "instrumentation_gap":
      return "bg-deterministic-alt/10 text-deterministic-alt border-deterministic-alt/20";
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
  // Remove leading/trailing "..." ellipsis and trim
  let core = context.trim();
  if (core.startsWith("...")) core = core.slice(3);
  if (core.endsWith("...")) core = core.slice(0, -3);
  return core.trim();
}

function findHighlightSpans(noteText: string, referenceContext: string): { start: number; end: number; kind: "gold"; label: string }[] {
  const core = extractCoreContext(referenceContext);
  if (!core || core.length < 10) return [];
  // Try exact match first
  let idx = noteText.indexOf(core);
  if (idx >= 0) {
    return [{ start: idx, end: idx + core.length, kind: "gold", label: "Gold reference context" }];
  }
  // Try case-insensitive
  const lowerNote = noteText.toLowerCase();
  const lowerCore = core.toLowerCase();
  idx = lowerNote.indexOf(lowerCore);
  if (idx >= 0) {
    return [{ start: idx, end: idx + core.length, kind: "gold", label: "Gold reference context" }];
  }
  // Try first sentence of core
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
  const [currentSourceRowIndex, setCurrentSourceRowIndex] = useState<number | null>(null);
  const [selectedClass, setSelectedClass] = useState<RQ10Class | null>(null);
  const [notes, setNotes] = useState("");
  const [correctedGoldLabel, setCorrectedGoldLabel] = useState("");
  const [flags, setFlags] = useState({
    benchmark_convention_flag: false,
    all_system_fail: false,
    exact_evidence_but_scorer_wrong: false,
    clinically_defensible_alternative: false,
    likely_gold_defect: false,
  });
  const [hideAudited, setHideAudited] = useState(false);
  const [showShortcuts, setShowShortcuts] = useState(true);

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

  const visibleRows = useMemo(() => {
    if (!hideAudited) return sortedRows;
    return sortedRows.filter((r) => !decisionsMap.has(Number(r.source_row_index)));
  }, [sortedRows, hideAudited, decisionsMap]);

  const currentRow: GoldAuditRow | undefined = useMemo(() => {
    if (currentSourceRowIndex == null) return undefined;
    return visibleRows.find((r) => Number(r.source_row_index) === currentSourceRowIndex);
  }, [visibleRows, currentSourceRowIndex]);

  const { data: fullRecord } = useQuery<FullRecordResponse>({
    queryKey: ["record", "validation", currentRow?.source_row_index],
    queryFn: () => fetchRecord("validation", Number(currentRow!.source_row_index)),
    enabled: !!currentRow,
  });

  // Load existing decision into form when row changes
  useEffect(() => {
    if (!currentRow) {
      setSelectedClass(null);
      setNotes("");
      setCorrectedGoldLabel("");
      setFlags({
        benchmark_convention_flag: false,
        all_system_fail: false,
        exact_evidence_but_scorer_wrong: false,
        clinically_defensible_alternative: false,
        likely_gold_defect: false,
      });
      return;
    }
    const existing = decisionsMap.get(Number(currentRow.source_row_index));
    if (existing) {
      setSelectedClass(existing.rq10_class);
      setNotes(existing.notes ?? "");
      setCorrectedGoldLabel(existing.corrected_gold_label ?? "");
      setFlags({
        benchmark_convention_flag: existing.benchmark_convention_flag ?? false,
        all_system_fail: existing.all_system_fail ?? false,
        exact_evidence_but_scorer_wrong: existing.exact_evidence_but_scorer_wrong ?? false,
        clinically_defensible_alternative: existing.clinically_defensible_alternative ?? false,
        likely_gold_defect: existing.likely_gold_defect ?? false,
      });
    } else {
      setSelectedClass(null);
      setNotes("");
      setCorrectedGoldLabel("");
      setFlags({
        benchmark_convention_flag: false,
        all_system_fail: false,
        exact_evidence_but_scorer_wrong: false,
        clinically_defensible_alternative: false,
        likely_gold_defect: false,
      });
    }
  }, [currentRow, decisionsMap]);

  const saveMutation = useMutation({
    mutationFn: postGoldAuditDecision,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gold-audit-decisions"] });
      queryClient.invalidateQueries({ queryKey: ["gold-audit-rows"] });
    },
  });

  const handleSave = useCallback(() => {
    if (!currentRow || !selectedClass) return;
    const decision: GoldAuditDecision = {
      source_row_index: Number(currentRow.source_row_index),
      split: currentRow.split,
      rq10_class: selectedClass,
      notes,
      corrected_gold_label: correctedGoldLabel || null,
      ...flags,
    };
    saveMutation.mutate(decision);
  }, [currentRow, selectedClass, notes, correctedGoldLabel, flags, saveMutation]);

  const goNext = useCallback(() => {
    if (!currentRow) return;
    const idx = visibleRows.findIndex((r) => Number(r.source_row_index) === Number(currentRow.source_row_index));
    if (idx >= 0 && idx < visibleRows.length - 1) {
      setCurrentSourceRowIndex(Number(visibleRows[idx + 1].source_row_index));
    }
  }, [currentRow, visibleRows]);

  const goPrev = useCallback(() => {
    if (!currentRow) return;
    const idx = visibleRows.findIndex((r) => Number(r.source_row_index) === Number(currentRow.source_row_index));
    if (idx > 0) {
      setCurrentSourceRowIndex(Number(visibleRows[idx - 1].source_row_index));
    }
  }, [currentRow, visibleRows]);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null;
      const isTyping =
        target &&
        (target.tagName === "INPUT" ||
          target.tagName === "TEXTAREA" ||
          target.isContentEditable);

      // Number keys 1-6 select class (only when not typing)
      if (e.key >= "1" && e.key <= "6" && !e.ctrlKey && !e.metaKey && !e.altKey && !isTyping) {
        const idx = parseInt(e.key, 10) - 1;
        if (idx < RQ10_CLASSES.length) {
          e.preventDefault();
          setSelectedClass(RQ10_CLASSES[idx].value);
        }
        return;
      }
      // Cmd/Ctrl+Enter save (always works, but not when typing in textarea unless explicitly desired)
      if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
        e.preventDefault();
        handleSave();
        return;
      }
      // Arrow keys / J K navigate (only when not typing)
      if (!isTyping) {
        if (e.key === "ArrowDown" || e.key === "j" || e.key === "J") {
          e.preventDefault();
          goNext();
          return;
        }
        if (e.key === "ArrowUp" || e.key === "k" || e.key === "K") {
          e.preventDefault();
          goPrev();
          return;
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [handleSave, goNext, goPrev]);

  const highlights = useMemo(() => {
    if (!fullRecord?.note_text || !currentRow?.reference_context) return [];
    return findHighlightSpans(fullRecord.note_text, currentRow.reference_context);
  }, [fullRecord, currentRow]);

  const total = rowsData?.total ?? 0;
  const decided = rowsData?.decided ?? 0;
  const progress = total > 0 ? decided / total : 0;
  const classCounts = rowsData?.class_counts ?? {};

  if (rowsLoading || decisionsLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading gold audit queue…</p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      {/* Top bar */}
      <div className="flex items-center gap-4 border-b border-border bg-surface px-4 py-2">
        <div className="flex items-center gap-2">
          <Target className="h-4 w-4 text-llm" />
          <span className="text-xs font-semibold uppercase tracking-wider text-foreground">
            Gold Audit
          </span>
        </div>
        <div className="flex-1">
          <div className="h-2 w-full overflow-hidden rounded-full bg-surface-raised">
            <div
              className="h-full rounded-full bg-llm transition-all"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <div className="mt-0.5 flex justify-between text-[10px] text-muted">
            <span>{decided} / {total} audited</span>
            <span>{(progress * 100).toFixed(1)}%</span>
          </div>
        </div>
        <button
          onClick={() => setHideAudited((v) => !v)}
          className={`rounded-md border px-2 py-1 text-[10px] font-medium transition-colors ${
            hideAudited
              ? "border-llm/30 bg-llm/10 text-llm"
              : "border-border bg-surface text-muted hover:text-foreground"
          }`}
        >
          {hideAudited ? "Show audited" : "Hide audited"}
        </button>
        <button
          onClick={() => setShowShortcuts((v) => !v)}
          className="rounded-md border border-border bg-surface px-2 py-1 text-[10px] font-medium text-muted hover:text-foreground"
        >
          Shortcuts
        </button>
      </div>

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left sidebar: queue */}
        <div className="flex w-[260px] flex-col border-r border-border bg-surface">
          <div className="flex items-center justify-between border-b border-border px-3 py-2">
            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              Queue ({visibleRows.length})
            </span>
            <div className="flex gap-1">
              <button
                onClick={goPrev}
                disabled={!currentRow}
                className="rounded p-1 text-muted hover:bg-surface-raised hover:text-foreground disabled:opacity-30"
                title="Previous (K)"
              >
                <ChevronUp className="h-3.5 w-3.5" />
              </button>
              <button
                onClick={goNext}
                disabled={!currentRow}
                className="rounded p-1 text-muted hover:bg-surface-raised hover:text-foreground disabled:opacity-30"
                title="Next (J)"
              >
                <ChevronDown className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {visibleRows.map((row) => {
              const sri = Number(row.source_row_index);
              const isActive = currentSourceRowIndex === sri;
              const isDone = decisionsMap.has(sri);
              const decision = decisionsMap.get(sri);
              return (
                <button
                  key={sri}
                  onClick={() => setCurrentSourceRowIndex(sri)}
                  className={`w-full border-b border-border px-3 py-2 text-left transition-colors ${
                    isActive
                      ? "bg-llm/5"
                      : "hover:bg-surface-raised"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-mono text-muted">#{sri}</span>
                    {isDone ? (
                      <Check className="h-3 w-3 text-success" />
                    ) : (
                      <span className="h-3 w-3 rounded-full border border-border" />
                    )}
                    <span className="flex-1 truncate text-[11px] font-medium text-foreground">
                      {row.gold_label}
                    </span>
                    <span className="text-[10px] text-muted">{row.priority_score}</span>
                  </div>
                  {decision && (
                    <div className="mt-1">
                      <span
                        className={`inline-block rounded border px-1.5 py-0 text-[9px] font-medium ${classBadgeColor(decision.rq10_class)}`}
                      >
                        {RQ10_CLASSES.find((c) => c.value === decision.rq10_class)?.label ?? decision.rq10_class}
                      </span>
                    </div>
                  )}
                  {!isDone && row.codex_initial_ambiguity_label === "ambiguous" && (
                    <div className="mt-0.5 text-[9px] text-error">
                      {row.codex_ambiguity_reasons}
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {/* Mini class distribution */}
          <div className="border-t border-border p-3">
            <p className="mb-1.5 text-[10px] font-semibold uppercase tracking-wider text-muted">
              Distribution
            </p>
            <div className="space-y-1">
              {RQ10_CLASSES.map((c) => {
                const count = classCounts[c.value] ?? 0;
                const pct = decided > 0 ? (count / decided) * 100 : 0;
                return (
                  <div key={c.value} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: `var(--color-${c.color.replace("text-", "")})` }} />
                    <span className="w-24 truncate text-[9px] text-muted">{c.label}</span>
                    <div className="flex-1 h-1.5 overflow-hidden rounded-full bg-surface-raised">
                      <div className="h-full rounded-full bg-current transition-all" style={{ width: `${pct}%`, color: `var(--color-${c.color.replace("text-", "")})` }} />
                    </div>
                    <span className="w-4 text-right text-[9px] font-medium text-foreground">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Center: letter */}
        <div className="flex flex-1 flex-col overflow-hidden">
          {currentRow ? (
            <div className="flex-1 overflow-y-auto p-5">
              <div className="mx-auto max-w-3xl space-y-4">
                {showShortcuts && (
                  <div className="flex flex-wrap items-center gap-2 rounded-lg border border-border bg-surface-raised px-3 py-2">
                    <span className="text-[10px] font-semibold text-muted">Shortcuts:</span>
                    {RQ10_CLASSES.map((c) => (
                      <span key={c.value} className="rounded bg-surface px-1.5 py-0.5 text-[9px] text-muted border border-border">
                        {c.shortcut} = {c.label}
                      </span>
                    ))}
                    <span className="rounded bg-surface px-1.5 py-0.5 text-[9px] text-muted border border-border">
                      ⌘Enter = Save
                    </span>
                    <span className="rounded bg-surface px-1.5 py-0.5 text-[9px] text-muted border border-border">
                      J/K = Prev/Next
                    </span>
                    <button
                      onClick={() => setShowShortcuts(false)}
                      className="ml-auto text-[9px] text-muted hover:text-foreground"
                    >
                      Dismiss
                    </button>
                  </div>
                )}

                <LetterRenderer
                  text={fullRecord?.note_text ?? currentRow.note_text_single_line.replace(/\\n/g, "\n")}
                  highlights={highlights}
                >
                  {/* Gold label overlay card */}
                  <div className="mt-4 rounded-lg border border-gold-ghost/30 bg-gold-ghost/5 p-3">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-gold-ghost">Gold label:</span>
                      <span className="font-mono text-sm text-foreground">{currentRow.gold_label}</span>
                    </div>
                    <div className="mt-1 text-xs text-muted">
                      Reference: <span className="text-foreground">{currentRow.gold_reference}</span>
                    </div>
                    {parseBool(currentRow.reference_found_in_note) && currentRow.reference_context && (
                      <div className="mt-1 text-[11px] text-muted italic">
                        Context: "{currentRow.reference_context}"
                      </div>
                    )}
                  </div>
                </LetterRenderer>
              </div>
            </div>
          ) : (
            <div className="flex h-full items-center justify-center text-muted">
              <div className="text-center">
                <Target className="mx-auto mb-3 h-8 w-8 text-muted/40" />
                <p className="text-sm font-medium">Select a row from the queue</p>
                <p className="mt-1 text-[11px] text-muted">
                  {visibleRows.length} rows available. Start with the highest-priority un-audited row.
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right sidebar: classification form */}
        <div className="flex w-[320px] flex-col border-l border-border bg-surface">
          <div className="border-b border-border px-4 py-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-foreground">
              Adjudication
            </h3>
            <p className="mt-0.5 text-[10px] text-muted">
              RQ10 class (first applicable)
            </p>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* RQ10 class buttons */}
            <div className="space-y-1.5">
              {RQ10_CLASSES.map((c) => {
                const active = selectedClass === c.value;
                return (
                  <button
                    key={c.value}
                    onClick={() => setSelectedClass(c.value)}
                    className={`flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left transition-colors ${
                      active
                        ? `border-current bg-current/5 ${c.color}`
                        : "border-border bg-surface hover:bg-surface-raised text-foreground"
                    }`}
                  >
                    <span
                      className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[9px] font-bold ${
                        active ? "border-current bg-current text-white" : "border-border text-muted"
                      }`}
                    >
                      {c.shortcut}
                    </span>
                    <span className={`text-[11px] font-medium ${active ? c.color : "text-foreground"}`}>
                      {c.label}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Flags */}
            <div className="space-y-2">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-muted">Benchmark flags</p>
              {(
                [
                  { key: "benchmark_convention_flag", label: "Benchmark convention dominated", icon: Flag },
                  { key: "all_system_fail", label: "All-system fail", icon: ShieldAlert },
                  { key: "exact_evidence_but_scorer_wrong", label: "Exact evidence but scorer wrong", icon: Target },
                  { key: "clinically_defensible_alternative", label: "Clinically defensible alternative", icon: Check },
                  { key: "likely_gold_defect", label: "Likely gold defect", icon: SkipForward },
                ] as const
              ).map(({ key, label, icon: Icon }) => (
                <label
                  key={key}
                  className="flex cursor-pointer items-center gap-2 rounded-md border border-border bg-surface px-2 py-1.5 hover:bg-surface-raised"
                >
                  <input
                    type="checkbox"
                    checked={flags[key as keyof typeof flags]}
                    onChange={(e) =>
                      setFlags((prev) => ({ ...prev, [key]: e.target.checked }))
                    }
                    className="h-3.5 w-3.5 rounded border-border text-deterministic focus:ring-deterministic"
                  />
                  <Icon className="h-3 w-3 text-muted" />
                  <span className="text-[10px] text-foreground">{label}</span>
                </label>
              ))}
            </div>

            {/* Notes */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                Adjudication notes
              </label>
              <textarea
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="Why this class? Any observations…"
                className="h-24 w-full resize-none rounded-lg border border-border bg-surface px-3 py-2 text-[11px] text-foreground placeholder:text-muted focus:border-deterministic focus:outline-none"
              />
            </div>

            {/* Corrected gold label */}
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

            {/* Row metadata */}
            {currentRow && (
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
                  <span className="text-muted">Row OK</span>
                  <span className={parseBool(currentRow.row_ok) ? "text-success" : "text-error"}>
                    {parseBool(currentRow.row_ok) ? "Yes" : "No"}
                  </span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-muted">Heuristic</span>
                  <span className={currentRow.codex_initial_ambiguity_label === "ambiguous" ? "text-error" : "text-success"}>
                    {currentRow.codex_initial_ambiguity_label}
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Save bar */}
          <div className="border-t border-border p-3">
            <button
              onClick={handleSave}
              disabled={!currentRow || !selectedClass || saveMutation.isPending}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-deterministic px-3 py-2 text-xs font-medium text-white transition-colors hover:bg-deterministic/90 disabled:opacity-40 disabled:hover:bg-deterministic"
            >
              {saveMutation.isPending ? (
                <span>Saving…</span>
              ) : (
                <>
                  <Save className="h-3.5 w-3.5" />
                  Save decision
                  <span className="rounded bg-white/20 px-1 text-[9px]">⌘Enter</span>
                </>
              )}
            </button>
            {saveMutation.isError && (
              <p className="mt-2 text-center text-[10px] text-error">
                Error saving: {String(saveMutation.error)}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
