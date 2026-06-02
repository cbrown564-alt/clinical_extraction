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
} from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import {
  useRules,
  useRecords,
  useRecord,
  usePipelineFamilies,
  useRunNote,
} from "@/lib/hooks";
import { fetchRegistry, fetchArtifact, fetchRecord } from "@/lib/api";
import {
  adaptDeterministicTrace,
  adaptHybridTrace,
  adaptLLMTrace,
} from "@/lib/traceAdapter";
import type { PipelineFamily, HybridArtifactRow, LLMArtifactRow } from "@/lib/types";
import RuleConfigPanel from "./RuleConfigPanel";

const SPLITS = ["train", "validation", "test"];

function isDeterministicFamily(family: PipelineFamily): boolean {
  return family === "rules_only" || family === "deterministic_v1";
}

function isHybridFamily(family: PipelineFamily): boolean {
  return family === "hybrid_rules_candidates_llm_adjudicator";
}

function isLLMFamily(family: PipelineFamily): boolean {
  return family.startsWith("llm_only");
}

function familyKindLabel(family: PipelineFamily): string {
  if (isDeterministicFamily(family)) return "Live run";
  if (isHybridFamily(family)) return "Replay from artifact";
  if (isLLMFamily(family)) return "Replay from artifact";
  return "Replay from artifact";
}

export default function TraceControls() {
  const {
    noteText,
    split,
    sourceRowIndex,
    pipelineFamily,
    ablationConfig,
    setNoteText,
    setSplit,
    setSourceRowIndex,
    setPipelineFamily,
    setTrace,
    setIsLoading,
    setError,
    setReplayArtifactRows,
    setReplayRunId,
  } = useArchitectStore();

  const runNote = useRunNote();
  const rulesQuery = useRules();
  const recordsQuery = useRecords(split);
  const recordQuery = useRecord(split, sourceRowIndex);
  const familiesQuery = usePipelineFamilies();

  const [showCustomNoteModal, setShowCustomNoteModal] = useState(false);
  const [customNoteDraft, setCustomNoteDraft] = useState("");

  const isLive = isDeterministicFamily(pipelineFamily);
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
      return;
    }

    let cancelled = false;
    async function loadReplay() {
      setIsLoading(true);
      setError(null);
      try {
        const registry = await fetchRegistry();
        const matchingRun = registry.runs.find(
          (r) => r.pipeline_family === pipelineFamily
        );
        if (!matchingRun) {
          setError(`No replay artifact found for ${pipelineFamily}`);
          setIsLoading(false);
          return;
        }
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
  }, [pipelineFamily, setError, setIsLoading, setReplayArtifactRows, setReplayRunId, isLive]);

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

        let trace;
        if (isHybridFamily(pipelineFamily)) {
          trace = adaptHybridTrace(row as HybridArtifactRow, record);
        } else if (isLLMFamily(pipelineFamily)) {
          trace = adaptLLMTrace(row as LLMArtifactRow, record);
        } else {
          throw new Error("Unsupported replay family");
        }
        setTrace(trace);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load replay row");
      } finally {
        setIsLoading(false);
      }
    },
    [pipelineFamily, sourceRowIndex, split, setNoteText, setSplit, setSourceRowIndex, setTrace, setIsLoading, setError]
  );

  const replayRows = useArchitectStore((s) => s.replayArtifactRows);
  const isLoading = useArchitectStore((s) => s.isLoading);
  const error = useArchitectStore((s) => s.error);
  const trace = useArchitectStore((s) => s.trace);

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

  return (
    <div className="shrink-0 border-b border-border bg-surface">
      {/* ── Tier 1: Specimen + Pipeline ── */}
      <div className="flex items-center gap-4 px-4 py-2.5">
        {/* Mode badge */}
        <div
          className={`flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-wide ${
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
          <div className="flex items-center gap-2">
            <Database className="h-3.5 w-3.5 text-muted" />
            <select
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
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
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20 disabled:opacity-50"
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
          <div className="flex items-center gap-2">
            <Film className="h-3.5 w-3.5 text-muted" />
            <select
              className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-hybrid focus:ring-1 focus:ring-hybrid/20"
              value=""
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
                    Row {r.source_row_index ?? idx} —{" "}
                    {r.reference?.gold_label ?? "?"}
                  </option>
                );
              })}
            </select>
          </div>
        )}

        {isReplay && isLoading && (
          <div className="flex items-center gap-1.5 text-xs text-muted">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Loading artifacts…
          </div>
        )}

        {/* Pipeline family */}
        <div className="ml-auto flex items-center gap-2">
          <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Pipeline
          </label>
          <select
            className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
            value={pipelineFamily}
            onChange={(e) =>
              setPipelineFamily(e.target.value as PipelineFamily)
            }
          >
            {pipelineOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
                {!opt.executable ? " (replay only)" : ""}
              </option>
            ))}
          </select>
        </div>

        {/* Paste custom note */}
        <button
          onClick={handleOpenCustomNote}
          className="flex items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground shadow-sm transition-all hover:bg-surface-raised"
          title="Paste custom clinical note"
        >
          <Pencil className="h-3.5 w-3.5 text-muted" />
          <span className="hidden sm:inline">Custom note</span>
        </button>
      </div>

      {/* ── Tier 2: Config + Primary action ── */}
      <div className="flex items-center gap-3 border-t border-border bg-surface-raised/40 px-4 py-2.5">
        {/* Rule panel toggle (deterministic only) */}
        {isLive && rulesQuery.data && <RuleConfigPanel />}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Primary action */}
        {isLive ? (
          <button
            onClick={handleRun}
            disabled={isLoading || !noteText.trim()}
            className="flex items-center gap-2 rounded-lg bg-deterministic px-5 py-2 text-sm font-semibold text-white shadow-sm transition-all hover:bg-deterministic/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4" />
            )}
            Run deterministic pipeline
          </button>
        ) : replayRows && replayRows.length > 0 ? (
          <div className="flex items-center gap-2 text-sm text-muted">
            <Film className="h-4 w-4 text-hybrid" />
            <span>Select a replay row above to load</span>
          </div>
        ) : isLoading ? (
          <div className="flex items-center gap-2 text-sm text-muted">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading replay artifacts…
          </div>
        ) : (
          <div className="flex items-center gap-2 text-sm text-error">
            <AlertCircle className="h-4 w-4" />
            <span>No replay artifact available</span>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-1.5 rounded-md border border-error/20 bg-error/5 px-2.5 py-1.5 text-xs text-error">
            <AlertCircle className="h-3.5 w-3.5 shrink-0" />
            <span className="max-w-[240px] truncate">{error}</span>
          </div>
        )}

        {/* Reset */}
        {trace && (
          <button
            onClick={() => useArchitectStore.getState().reset()}
            className="text-muted hover:text-foreground transition-colors"
            title="Reset"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* ── Custom note modal ── */}
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
