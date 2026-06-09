"use client";

import { useEffect, useCallback, useState } from "react";
import {
  Play,
  Database,
  FileText,
  Loader2,
  AlertCircle,
  RotateCcw,
  Zap,
  Film,
  Pencil,
  X,
  Settings2,
} from "lucide-react";
import { useArchitectStore, useUiStore } from "@/lib/stores";
import {
  useRules,
  useRecords,
  useRecord,
  usePipelineFamilies,
  useRunNote,
} from "@/lib/hooks";
import { fetchRegistry, fetchArtifact, fetchRecord } from "@/lib/api";
import { adaptDeterministicTrace, adaptTrace, isReplaySupported } from "@/lib/traceAdapter";
import type { PipelineFamily } from "@/lib/types";
import RuleConfigPanel from "./RuleConfigPanel";

const SPLITS = ["train", "validation", "test"];

function isDeterministicFamily(family: string): boolean {
  return family === "rules_only" || family.includes("deterministic");
}

function isHybridFamily(family: string): boolean {
  return family.includes("hybrid");
}

function isLLMFamily(family: string): boolean {
  return family.startsWith("llm_only");
}

function isLiveFamily(family: string): boolean {
  return isDeterministicFamily(family);
}

function familyKindLabel(family: PipelineFamily): string {
  if (isLiveFamily(family)) return "Live";
  return "Replay";
}

export default function TraceControls() {
  const {
    noteText,
    split,
    sourceRowIndex,
    pipelineFamily,
    ablationConfig,
    replayRowIndex,
    setNoteText,
    setSplit,
    setSourceRowIndex,
    setPipelineFamily,
    setTrace,
    setIsLoading,
    setError,
    setReplayRunId,
    setReplayArtifactRows,
    setReplayRowIndex,
  } = useArchitectStore();



  const runNote = useRunNote();
  const rulesQuery = useRules();
  const recordsQuery = useRecords(split);
  const recordQuery = useRecord(split, sourceRowIndex);
  const familiesQuery = usePipelineFamilies();

  const [showCustomNoteModal, setShowCustomNoteModal] = useState(false);
  const [customNoteDraft, setCustomNoteDraft] = useState("");

  const isLive = isLiveFamily(pipelineFamily);
  const isReplay = !isLive;

  // When dataset record loads, update note text
  useEffect(() => {
    if (recordQuery.data?.note_text) {
      setNoteText(recordQuery.data.note_text);
    }
  }, [recordQuery.data, setNoteText]);

  // When pipeline family changes to non-deterministic, auto-load replay artifacts
  useEffect(() => {
    if (isLive) {
      setReplayArtifactRows(null);
      setReplayRunId(null);
      setReplayRowIndex(null);
      return;
    }

    let cancelled = false;
    async function loadReplay() {
      setIsLoading(true);
      setError(null);
      try {
        const registry = await fetchRegistry();
        // Find all runs for this family that have JSONL artifacts
        const matchingRuns = registry.runs.filter(
          (r) =>
            r.pipeline_family === pipelineFamily &&
            r.artifact_paths.some((p) => p.endsWith(".jsonl"))
        );
        if (matchingRuns.length === 0) {
          setError(`No replay artifact found for ${pipelineFamily}`);
          setIsLoading(false);
          return;
        }
        // Prefer the run with the most rows (largest corpus)
        const matchingRun = matchingRuns.reduce((a, b) =>
          (a.row_count || 0) > (b.row_count || 0) ? a : b
        );
        const jsonlPath = matchingRun.artifact_paths.find((p) =>
          p.endsWith(".jsonl")
        );
        if (!jsonlPath) {
          setError(`No JSONL artifact found for ${pipelineFamily}`);
          setIsLoading(false);
          return;
        }
        const artifact = await fetchArtifact(matchingRun.run_id, jsonlPath, 100);
        if (!cancelled) {
          setReplayRunId(matchingRun.run_id);
          setReplayArtifactRows(artifact.content as unknown[]);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Failed to load replay");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }
    loadReplay();
    return () => {
      cancelled = true;
    };
  }, [pipelineFamily, setError, setIsLoading, setReplayArtifactRows, setReplayRunId, setReplayRowIndex, isLive]);

  const handleRun = useCallback(() => {
    if (!noteText.trim()) return;
    if (!isLive) return;

    setIsLoading(true);
    setError(null);
    runNote.mutate(
      {
        note_text: noteText,
        pipeline: pipelineFamily,
        source_row_index: sourceRowIndex ?? 0,
        gold_label: recordQuery.data?.gold_label,
        ablation_config: ablationConfig,
      },
      {
        onSuccess: (data) => {
          const trace = adaptDeterministicTrace(
            data,
            noteText,
            sourceRowIndex ?? 0,
            split ?? "unknown"
          );
          setTrace(trace);
          setIsLoading(false);
        },
        onError: (e) => {
          setError(e instanceof Error ? e.message : "Run failed");
          setIsLoading(false);
        },
      }
    );
  }, [
    noteText,
    pipelineFamily,
    sourceRowIndex,
    split,
    ablationConfig,
    recordQuery.data,
    runNote,
    setTrace,
    setIsLoading,
    setError,
    isLive,
  ]);

  const handleLoadReplayRow = useCallback(
    async (rowIndex: number) => {
      const rows = useArchitectStore.getState().replayArtifactRows;
      if (!rows || rowIndex < 0 || rowIndex >= rows.length) return;

      const row = rows[rowIndex];
      const rowSourceIndex =
        (row as { source_row_index?: number }).source_row_index ??
        sourceRowIndex ??
        0;
      const rowSplit =
        (row as { split?: string }).split ?? split ?? "validation";

      setIsLoading(true);
      setError(null);
      try {
        const record = await fetchRecord(rowSplit, rowSourceIndex);
        setNoteText(record.note_text);
        setSplit(rowSplit);
        setSourceRowIndex(rowSourceIndex);
        setReplayRowIndex(rowIndex);

        let trace;
        if (isReplaySupported(pipelineFamily)) {
          trace = adaptTrace(row, pipelineFamily, record);
        } else {
          setError(`Replay not yet supported for ${pipelineFamily}. The artifact format for this family is not yet mapped to the trace viewer.`);
          setIsLoading(false);
          return;
        }
        setTrace(trace);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load replay row");
      } finally {
        setIsLoading(false);
      }
    },
    [pipelineFamily, sourceRowIndex, split, setNoteText, setSplit, setSourceRowIndex, setTrace, setIsLoading, setError, setReplayRowIndex]
  );

  const replayRows = useArchitectStore((s) => s.replayArtifactRows);
  const isLoading = useArchitectStore((s) => s.isLoading);
  const error = useArchitectStore((s) => s.error);
  const trace = useArchitectStore((s) => s.trace);

  // Auto-run when live specimen changes or is loaded initially
  useEffect(() => {
    if (isLive && noteText && recordQuery.data && !isLoading) {
      // Check if the current trace matches the selected index and split
      const currentTraceMatches = trace && trace.sourceRowIndex === sourceRowIndex && trace.split === split && trace.noteText === noteText;
      if (!currentTraceMatches) {
        handleRun();
      }
    }
  }, [isLive, noteText, recordQuery.data, sourceRowIndex, split, handleRun, trace, isLoading]);

  // Auto-select replay row matching sourceRowIndex when artifacts load
  useEffect(() => {
    if (
      !isLive &&
      replayRows &&
      replayRows.length > 0 &&
      sourceRowIndex !== null &&
      replayRowIndex === null
    ) {
      const matchIndex = replayRows.findIndex(
        (r) => (r as { source_row_index?: number }).source_row_index === sourceRowIndex
      );
      if (matchIndex !== -1) {
        handleLoadReplayRow(matchIndex);
      }
    }
  }, [isLive, replayRows, sourceRowIndex, replayRowIndex, handleLoadReplayRow]);

  const pipelineOptions = familiesQuery.data?.families ?? [];

  const handleOpenCustomNote = () => {
    setCustomNoteDraft(noteText);
    setShowCustomNoteModal(true);
  };

  const handleSaveCustomNote = () => {
    setNoteText(customNoteDraft);
    setSplit(null);
    setSourceRowIndex(null);
    setShowCustomNoteModal(false);
  };

  // Derived: currently selected replay row label
  const selectedReplayLabel = (() => {
    if (replayRowIndex === null || !replayRows) return null;
    const row = replayRows[replayRowIndex] as {
      source_row_index?: number;
      reference?: { gold_label?: string };
    };
    return `Row ${row?.source_row_index ?? replayRowIndex} · ${row?.reference?.gold_label ?? "?"}`;
  })();

  return (
    <div className="shrink-0 border-b border-border bg-surface">
      {/* Single compact row */}
      <div className="flex items-center gap-3 px-4 py-2">
        {/* Mode badge */}
        <div
          className={`flex items-center gap-1 rounded border px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wide shrink-0 ${
            isLive
              ? "border-deterministic/20 bg-deterministic/5 text-deterministic"
              : "border-hybrid/20 bg-hybrid/5 text-hybrid"
          }`}
        >
          {isLive ? <Zap className="h-3 w-3" /> : <Film className="h-3 w-3" />}
          {familyKindLabel(pipelineFamily)}
        </div>

        {/* Specimen selector — dataset mode (live) */}
        {isLive && (
          <div className="flex items-center gap-1.5">
            <Database className="h-3 w-3 text-muted" />
            <select
              className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-deterministic"
              value={split ?? ""}
              onChange={(e) => setSplit(e.target.value || null)}
            >
              <option value="">Split…</option>
              {SPLITS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
            <select
              className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-deterministic disabled:opacity-50"
              value={sourceRowIndex ?? ""}
              onChange={(e) =>
                setSourceRowIndex(
                  e.target.value ? parseInt(e.target.value, 10) : null
                )
              }
              disabled={!recordsQuery.data}
            >
              <option value="">Row…</option>
              {recordsQuery.data?.records.map((r) => (
                <option key={r.source_row_index} value={r.source_row_index}>
                  {r.source_row_index} — {r.gold_label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Specimen selector — replay mode */}
        {isReplay && replayRows && replayRows.length > 0 && (
          <div className="flex items-center gap-1.5">
            <Film className="h-3 w-3 text-muted" />
            <select
              className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-hybrid min-w-[160px]"
              value={replayRowIndex ?? ""}
              onChange={(e) => {
                if (e.target.value)
                  handleLoadReplayRow(parseInt(e.target.value, 10));
              }}
            >
              <option value="">Load replay row…</option>
              {replayRows.map((row, idx) => {
                const r = row as {
                  source_row_index?: number;
                  reference?: { gold_label?: string };
                };
                return (
                  <option key={idx} value={idx}>
                    Row {r.source_row_index ?? idx} — {r.reference?.gold_label ?? "?"}
                  </option>
                );
              })}
            </select>
            {selectedReplayLabel && (
              <span className="text-[11px] text-muted font-mono truncate max-w-[180px]">
                {selectedReplayLabel}
              </span>
            )}
          </div>
        )}

        {isReplay && isLoading && (
          <div className="flex items-center gap-1 text-[11px] text-muted">
            <Loader2 className="h-3 w-3 animate-spin" />
            Loading…
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-1 rounded-md border border-error/20 bg-error/5 px-2 py-1 text-[11px] text-error max-w-xs truncate shrink-0">
            <AlertCircle className="h-3 w-3 shrink-0" />
            <span className="truncate">{error}</span>
          </div>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Pipeline family */}
        <div className="flex items-center gap-1.5 shrink-0">
          <label className="text-[10px] font-semibold uppercase tracking-wide text-muted">
            Pipeline
          </label>
          <select
            className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-deterministic"
            value={pipelineFamily}
            onChange={(e) =>
              setPipelineFamily(e.target.value as PipelineFamily)
            }
          >
            {pipelineOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
                {!opt.executable ? " (replay)" : ""}
              </option>
            ))}
          </select>
        </div>

        {/* Paste custom note */}
        <button
          onClick={handleOpenCustomNote}
          className="flex items-center justify-center rounded-md border border-border bg-surface p-1.5 text-muted hover:text-foreground transition-all shrink-0"
          title="Paste custom clinical note"
        >
          <Pencil className="h-3.5 w-3.5" />
        </button>

        {/* Reset */}
        {trace && (
          <button
            onClick={() => useArchitectStore.getState().reset()}
            className="flex items-center justify-center rounded-md border border-border bg-surface p-1.5 text-muted hover:text-foreground transition-all shrink-0"
            title="Reset"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        )}

        {/* Rule panel toggle (deterministic only) */}
        {isLive && rulesQuery.data && (
          <div className="shrink-0">
            <RuleConfigPanel />
          </div>
        )}

        {/* Primary action / status */}
        {isLive ? (
          <button
            onClick={handleRun}
            disabled={isLoading || !noteText.trim()}
            className="flex items-center gap-1.5 rounded-md bg-deterministic px-3 py-1.5 text-xs font-semibold text-white shadow-sm transition-all hover:bg-deterministic/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            {isLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Play className="h-3.5 w-3.5" />
            )}
            Run
          </button>
        ) : selectedReplayLabel ? (
          <div className="flex items-center gap-1.5 rounded-md border border-hybrid/20 bg-hybrid/5 px-2.5 py-1 text-xs text-hybrid shrink-0">
            <Film className="h-3.5 w-3.5" />
            <span className="font-medium truncate max-w-[200px]">{selectedReplayLabel}</span>
          </div>
        ) : replayRows && replayRows.length > 0 ? (
          <span className="text-xs text-muted shrink-0">Select a replay row</span>
        ) : isLoading ? (
          <span className="flex items-center gap-1 text-xs text-muted shrink-0">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Loading…
          </span>
        ) : (
          <span className="flex items-center gap-1 text-xs text-error shrink-0">
            <AlertCircle className="h-3.5 w-3.5" />
            No replay artifact
          </span>
        )}
      </div>

      {/* Custom note modal */}
      {showCustomNoteModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm">
          <div className="w-full max-w-2xl rounded-xl border border-border bg-surface p-5 shadow-xl">
            <div className="mb-3 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted" />
                <h3 className="text-sm font-semibold text-foreground">
                  Paste custom clinical note
                </h3>
              </div>
              <button
                onClick={() => setShowCustomNoteModal(false)}
                className="text-muted hover:text-foreground transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <textarea
              className="w-full rounded-lg border border-border bg-surface-raised px-3 py-2 text-sm text-foreground outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20 min-h-[200px] resize-y font-serif"
              placeholder="Paste clinical note text here…"
              value={customNoteDraft}
              onChange={(e) => setCustomNoteDraft(e.target.value)}
            />
            <div className="mt-3 flex items-center justify-end gap-2">
              <button
                onClick={() => setShowCustomNoteModal(false)}
                className="rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground hover:bg-surface-raised transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleSaveCustomNote}
                disabled={!customNoteDraft.trim()}
                className="rounded-lg bg-deterministic px-3 py-1.5 text-xs font-semibold text-white hover:bg-deterministic/90 disabled:opacity-50 transition-colors"
              >
                Load note
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
