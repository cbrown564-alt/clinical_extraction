"use client";

import { useEffect, useCallback } from "react";
import { Play, Database, FileText, Loader2, AlertCircle, RotateCcw } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import { useRules, useRecords, useRecord, usePipelineFamilies, useRunNote } from "@/lib/hooks";
import { fetchRegistry, fetchArtifact, fetchRecord } from "@/lib/api";
import { adaptDeterministicTrace, adaptHybridTrace, adaptLLMTrace } from "@/lib/traceAdapter";
import type { PipelineFamily, HybridArtifactRow, LLMArtifactRow } from "@/lib/types";

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
    toggleRuleGroup,
  } = useArchitectStore();

  const runNote = useRunNote();
  const rulesQuery = useRules();
  const recordsQuery = useRecords(split);
  const recordQuery = useRecord(split, sourceRowIndex);
  const familiesQuery = usePipelineFamilies();

  // When dataset record loads, update note text
  useEffect(() => {
    if (recordQuery.data?.note_text) {
      setNoteText(recordQuery.data.note_text);
    }
  }, [recordQuery.data, setNoteText]);

  // When pipeline family changes to non-deterministic, auto-load replay artifacts
  useEffect(() => {
    if (isDeterministicFamily(pipelineFamily)) {
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
        const matchingRun = registry.runs.find((r) => r.pipeline_family === pipelineFamily);
        if (!matchingRun) {
          setError(`No replay artifact found for ${pipelineFamily}`);
          setIsLoading(false);
          return;
        }
        const jsonlPath = matchingRun.artifact_paths.find((p) => p.endsWith(".jsonl"));
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
    return () => { cancelled = true; };
  }, [pipelineFamily, setError, setIsLoading, setReplayArtifactRows, setReplayRunId]);

  const handleRun = useCallback(() => {
    if (!noteText.trim()) return;
    if (!isDeterministicFamily(pipelineFamily)) return;

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
  }, [noteText, pipelineFamily, sourceRowIndex, split, ablationConfig, recordQuery.data, runNote, setTrace, setIsLoading, setError]);

  const handleLoadReplayRow = useCallback(async (rowIndex: number) => {
    const rows = useArchitectStore.getState().replayArtifactRows;
    if (!rows || rowIndex < 0 || rowIndex >= rows.length) return;

    const row = rows[rowIndex];
    const rowSourceIndex = (row as { source_row_index?: number }).source_row_index ?? sourceRowIndex ?? 0;
    const rowSplit = (row as { split?: string }).split ?? split ?? "validation";

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
  }, [pipelineFamily, sourceRowIndex, split, setNoteText, setSplit, setSourceRowIndex, setTrace, setIsLoading, setError]);

  const replayRows = useArchitectStore((s) => s.replayArtifactRows);
  const isLoading = useArchitectStore((s) => s.isLoading);
  const error = useArchitectStore((s) => s.error);
  const trace = useArchitectStore((s) => s.trace);

  const pipelineOptions = familiesQuery.data?.families ?? [];
  const canRun = isDeterministicFamily(pipelineFamily);

  return (
    <div className="flex items-center gap-4 px-4 py-2 border-b border-border bg-surface">
      {/* Pipeline family */}
      <div className="flex items-center gap-2">
        <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">Pipeline</label>
        <select
          className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
          value={pipelineFamily}
          onChange={(e) => setPipelineFamily(e.target.value as PipelineFamily)}
        >
          {pipelineOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
              {!opt.executable ? " (replay only)" : ""}
            </option>
          ))}
        </select>
      </div>

      {/* Specimen selector */}
      <div className="flex items-center gap-2">
        <Database className="h-3.5 w-3.5 text-muted" />
        <select
          className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
          value={split ?? ""}
          onChange={(e) => setSplit(e.target.value || null)}
        >
          <option value="">Split…</option>
          {SPLITS.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20 disabled:opacity-50"
          value={sourceRowIndex ?? ""}
          onChange={(e) => setSourceRowIndex(e.target.value ? parseInt(e.target.value, 10) : null)}
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

      {/* Note text input (compact) */}
      <div className="flex items-center gap-2 flex-1">
        <FileText className="h-3.5 w-3.5 text-muted" />
        <input
          type="text"
          className="flex-1 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
          placeholder="Note text or paste a clinical note…"
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
        />
      </div>

      {/* Run or Replay row selector */}
      {canRun ? (
        <button
          onClick={handleRun}
          disabled={isLoading || !noteText.trim()}
          className="flex items-center gap-1.5 rounded-lg bg-deterministic px-3 py-1.5 text-xs font-medium text-white shadow-sm transition-all hover:bg-deterministic/90 active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5" />}
          Run
        </button>
      ) : replayRows && replayRows.length > 0 ? (
        <select
          className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-foreground shadow-sm outline-none focus:border-hybrid focus:ring-1 focus:ring-hybrid/20"
          value=""
          onChange={(e) => {
            if (e.target.value) handleLoadReplayRow(parseInt(e.target.value, 10));
          }}
        >
          <option value="">Load replay row…</option>
          {replayRows.map((row, idx) => {
            const r = row as { source_row_index?: number; reference?: { gold_label?: string } };
            return (
              <option key={idx} value={idx}>
                Row {r.source_row_index ?? idx} — {r.reference?.gold_label ?? "?"}
              </option>
            );
          })}
        </select>
      ) : isLoading ? (
        <div className="flex items-center gap-1.5 text-xs text-muted">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          Loading artifacts…
        </div>
      ) : null}

      {/* Rule toggles (compact, deterministic only) */}
      {canRun && rulesQuery.data && (
        <div className="flex items-center gap-1">
          {rulesQuery.data.groups.slice(0, 4).map((group) => {
            const enabled = ablationConfig.enabled_groups
              ? ablationConfig.enabled_groups.includes(group)
              : true;
            return (
              <button
                key={group}
                onClick={() => toggleRuleGroup(group)}
                className={`rounded px-1.5 py-0.5 text-[10px] border transition-colors ${
                  enabled
                    ? "bg-surface-raised text-foreground border-border"
                    : "bg-surface-raised/40 text-muted border-border/40 line-through"
                }`}
                title={group}
              >
                {group.replace(/_/g, " ").slice(0, 12)}…
              </button>
            );
          })}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-center gap-1.5 text-xs text-error">
          <AlertCircle className="h-3.5 w-3.5" />
          <span className="max-w-[200px] truncate">{error}</span>
        </div>
      )}

      {/* Reset */}
      {trace && (
        <button
          onClick={() => useArchitectStore.getState().reset()}
          className="text-muted hover:text-foreground transition-colors"
          title="Reset"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
