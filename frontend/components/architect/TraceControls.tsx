"use client";

import { useEffect, useCallback, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
  Play,
  Database,
  FileText,
  Loader2,
  AlertCircle,
  RotateCcw,
  Film,
  BarChart3,
  Pencil,
  X,
  Blend,
  Bot,
  Braces,
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
import { firstReplayableArtifactPath } from "@/lib/registryArtifacts";
import { adaptDeterministicTrace, adaptTrace, isReplaySupported } from "@/lib/traceAdapter";
import {
  ganPipelineOptionLabel,
  groupGanPipelineOptions,
  isGanAggregateRunId,
  resolveGanPipelineOption,
} from "@/lib/ganPipelineOptions";
import { activeMethodLabel } from "@/lib/plainLanguageLabels";
import RuleConfigPanel from "./RuleConfigPanel";

const SPLITS = ["train", "validation", "test"];

function isDeterministicFamily(family: string): boolean {
  return family === "rules" || family === "rules_only" || family.includes("deterministic");
}

function isLiveFamily(family: string): boolean {
  return isDeterministicFamily(family);
}

export default function TraceControls() {
  const searchParams = useSearchParams();
  const requestedRunId = searchParams.get("run");
  const {
    noteText,
    split,
    sourceRowIndex,
    selectedRunId,
    pipelineFamily,
    ablationConfig,
    replayRowIndex,
    setNoteText,
    setSplit,
    setSourceRowIndex,
    setSelectedRunId,
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

  const [showCustomNoteEditor, setShowCustomNoteEditor] = useState(false);
  const [customNoteDraft, setCustomNoteDraft] = useState("");

  const pipelineOptions = useMemo(
    () => familiesQuery.data?.families ?? [],
    [familiesQuery.data?.families]
  );
  const pipelineGroups = useMemo(
    () => groupGanPipelineOptions(pipelineOptions),
    [pipelineOptions]
  );
  const selectedOption = useMemo(
    () => pipelineOptions.find((option) => option.run_id === selectedRunId),
    [pipelineOptions, selectedRunId]
  );
  const isAggregateOnly =
    selectedOption?.availability === "aggregate_only" ||
    isGanAggregateRunId(selectedRunId);
  const selectedAggregateMetrics = selectedOption?.metrics;
  const isLive = isLiveFamily(pipelineFamily);
  const isReplay = !isLive && !isAggregateOnly;

  // When dataset record loads, update note text
  useEffect(() => {
    if (recordQuery.data?.note_text) {
      setNoteText(recordQuery.data.note_text);
    }
  }, [recordQuery.data, setNoteText]);

  // Restore an exact run from the URL once the Gan comparison catalog arrives.
  useEffect(() => {
    if (pipelineOptions.length === 0) return;
    const requestedOption = pipelineOptions.find(
      (option) => option.run_id === requestedRunId
    );
    if (!requestedOption) return;
    const current = useArchitectStore.getState();
    if (
      requestedOption.run_id !== current.selectedRunId ||
      requestedOption.pipeline_family !== current.pipelineFamily
    ) {
      setSelectedRunId(requestedOption.run_id, requestedOption.pipeline_family);
    }
  }, [pipelineOptions, requestedRunId, setSelectedRunId]);

  // Keep adapter family aligned, or fall back from a legacy registry run id.
  useEffect(() => {
    if (pipelineOptions.length === 0) return;
    if (pipelineOptions.some((option) => option.run_id === requestedRunId)) return;
    const option = resolveGanPipelineOption(pipelineOptions, selectedRunId);
    if (
      option &&
      (option.run_id !== selectedRunId || option.pipeline_family !== pipelineFamily)
    ) {
      setSelectedRunId(option.run_id, option.pipeline_family);
    }
  }, [pipelineOptions, pipelineFamily, requestedRunId, selectedRunId, setSelectedRunId]);

  // When pipeline family changes to non-deterministic, auto-load replay artifacts
  useEffect(() => {
    if (isLive || isAggregateOnly) {
      setReplayArtifactRows(null);
      setReplayRunId(null);
      setReplayRowIndex(null);
      setIsLoading(false);
      setError(null);
      return;
    }

    let cancelled = false;
    async function loadReplay() {
      setIsLoading(true);
      setError(null);
      try {
        const registry = await fetchRegistry();
        const matchingRun = registry.runs.find((r) => r.run_id === selectedRunId);
        if (!matchingRun) {
          setError(`No replay artifact found for ${selectedRunId}`);
          setIsLoading(false);
          return;
        }
        const replayPath = firstReplayableArtifactPath(matchingRun.artifact_paths);
        if (!replayPath) {
          setError(`No replay artifact found for ${selectedRunId}`);
          setIsLoading(false);
          return;
        }
        const artifact = await fetchArtifact(matchingRun.run_id, replayPath, 100);
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
  }, [
    selectedRunId,
    isLive,
    isAggregateOnly,
    setError,
    setIsLoading,
    setReplayArtifactRows,
    setReplayRunId,
    setReplayRowIndex,
  ]);

  const handleRun = useCallback(() => {
    if (!noteText.trim()) return;
    if (!isLiveFamily(pipelineFamily)) return;

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

  const handleOpenCustomNote = () => {
    setCustomNoteDraft(noteText);
    setShowCustomNoteEditor(true);
  };

  const handleSaveCustomNote = () => {
    setNoteText(customNoteDraft);
    setSplit(null);
    setSourceRowIndex(null);
    setShowCustomNoteEditor(false);
  };

  return (
    <div className="shrink-0 border-b border-border bg-surface">
      {/* Single compact row */}
      <div className="flex flex-wrap items-center gap-3 px-4 py-2">
        {/* Specimen selector – dataset mode (live) */}
        {isLive && (
          <div className="flex items-center gap-1.5">
            <Database className="h-3 w-3 text-muted" />
            <select
              aria-label="Dataset split"
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
              aria-label="Dataset row"
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
                  {r.source_row_index} · {r.gold_label}
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Specimen selector – replay mode */}
        {isReplay && replayRows && replayRows.length > 0 && (
          <div className="flex items-center gap-1.5">
            <Film className="h-3 w-3 text-muted" />
            <select
              aria-label="Replay row"
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
                    Row {r.source_row_index ?? idx} · {r.reference?.gold_label ?? "?"}
                  </option>
                );
              })}
            </select>
          </div>
        )}

        {isReplay && isLoading && (
          <div className="flex items-center gap-1 text-xs text-muted">
            <Loader2 className="h-3 w-3 animate-spin" />
            Loading…
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="flex items-center gap-1 rounded-md border border-error/20 bg-error/5 px-2 py-1 text-xs text-error max-w-xs truncate shrink-0">
            <AlertCircle className="h-3 w-3 shrink-0" />
            <span className="truncate">{error}</span>
          </div>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Pipeline family */}
        <div className="flex items-center gap-1.5 shrink-0">
          <label htmlFor="architect-pipeline-select" className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Pipeline
          </label>
          {selectedOption?.kind && (
            <span
              className={`inline-flex items-center gap-1 rounded border px-1.5 py-0.5 text-[11px] font-medium ${
                selectedOption.kind === "llm_with_rules"
                  ? "border-hybrid/25 bg-hybrid/8 text-hybrid"
                  : selectedOption.kind === "llm"
                    ? "border-llm/25 bg-llm/8 text-llm"
                    : "border-deterministic/25 bg-deterministic/8 text-deterministic"
              }`}
            >
              {selectedOption.kind === "llm_with_rules" ? (
                <Blend className="h-3 w-3" aria-hidden="true" />
              ) : selectedOption.kind === "llm" ? (
                <Bot className="h-3 w-3" aria-hidden="true" />
              ) : (
                <Braces className="h-3 w-3" aria-hidden="true" />
              )}
              {activeMethodLabel(selectedOption.kind)}
            </span>
          )}
          <select
            id="architect-pipeline-select"
            className="rounded-md border border-border bg-surface px-2 py-1 text-xs text-foreground outline-none focus:border-deterministic min-w-[220px]"
            value={selectedRunId}
            onChange={(e) => {
              const option = pipelineOptions.find((opt) => opt.run_id === e.target.value);
              if (option) {
                setSelectedRunId(option.run_id, option.pipeline_family);
              }
            }}
          >
            {pipelineGroups.map((group) => (
              <optgroup key={group.method} label={group.label}>
                {group.options.map((opt) => (
                  <option
                    key={opt.run_id}
                    value={opt.run_id}
                    disabled={opt.availability === "not_retained"}
                  >
                    {ganPipelineOptionLabel(opt.label)}
                    {opt.availability === "aggregate_only"
                      ? " · aggregate only"
                      : opt.availability === "not_retained"
                        ? " · not retained"
                        : ""}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </div>

        {/* Paste custom note */}
        {!isAggregateOnly && (
          <button
            type="button"
            onClick={handleOpenCustomNote}
            className="flex items-center justify-center rounded-md border border-border bg-surface p-1.5 text-muted transition-colors hover:text-foreground shrink-0"
            aria-label="Paste custom clinical note"
            aria-expanded={showCustomNoteEditor}
          >
            <Pencil className="h-3.5 w-3.5" />
          </button>
        )}

        {/* Reset */}
        {trace && (
          <button
            type="button"
            onClick={() => useArchitectStore.getState().reset()}
            className="flex items-center justify-center rounded-md border border-border bg-surface p-1.5 text-muted transition-colors hover:text-foreground shrink-0"
            aria-label="Reset trace"
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
            type="button"
            onClick={handleRun}
            disabled={isLoading || !noteText.trim()}
            className="flex items-center gap-1.5 rounded-md bg-deterministic px-3 py-1.5 text-xs font-semibold text-surface transition-colors hover:bg-deterministic/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
          >
            {isLoading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Play className="h-3.5 w-3.5" />
            )}
            Run
          </button>
        ) : isAggregateOnly && selectedAggregateMetrics ? (
          <div className="flex items-center gap-2 rounded-md border border-hybrid/20 bg-hybrid/5 px-2.5 py-1 text-xs text-hybrid shrink-0">
            <BarChart3 className="h-3.5 w-3.5" />
            <span className="font-medium">
              Purist {selectedAggregateMetrics.purist_correct}/{selectedAggregateMetrics.row_count}
            </span>
            <span className="text-muted">·</span>
            <span className="font-medium">
              Pragmatic {selectedAggregateMetrics.pragmatic_correct}/{selectedAggregateMetrics.row_count}
            </span>
          </div>
        ) : replayRows && replayRows.length > 0 ? (
          null
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

      {showCustomNoteEditor && (
        <section className="border-t border-border bg-surface-raised/40 px-4 py-4" aria-labelledby="custom-note-title">
          <div className="mx-auto max-w-3xl">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4 text-muted" />
                <h3 id="custom-note-title" className="text-sm font-semibold text-foreground">Custom clinical note</h3>
              </div>
              <button
                type="button"
                onClick={() => setShowCustomNoteEditor(false)}
                className="rounded-sm text-muted transition-colors hover:text-foreground"
                aria-label="Close custom note editor"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <label htmlFor="custom-note-text" className="mb-1.5 block text-[11px] font-semibold uppercase tracking-wide text-muted">
              Clinical note text
            </label>
            <textarea
              id="custom-note-text"
              className="min-h-[160px] w-full resize-y rounded-md border border-border bg-surface px-3 py-2 font-serif text-sm text-foreground outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
              placeholder="Paste clinical note text here…"
              value={customNoteDraft}
              onChange={(e) => setCustomNoteDraft(e.target.value)}
            />
            <div className="mt-3 flex items-center justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowCustomNoteEditor(false)}
                className="rounded-md border border-border bg-surface px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-surface-raised"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleSaveCustomNote}
                disabled={!customNoteDraft.trim()}
                className="rounded-md bg-deterministic px-3 py-1.5 text-xs font-semibold text-surface transition-colors hover:bg-deterministic/90 disabled:opacity-50"
              >
                Load note
              </button>
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
