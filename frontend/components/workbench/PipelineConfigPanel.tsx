"use client";

import { Play, Database, Settings2, FileText } from "lucide-react";
import { useConfigStore, useUiStore } from "@/lib/stores";
import { useRunNote, useRules, useRecords, useRecord } from "@/lib/hooks";
import type { PipelineFamily } from "@/lib/types";
import { useEffect } from "react";

const PIPELINE_OPTIONS: { value: PipelineFamily; label: string }[] = [
  { value: "rules_only", label: "Deterministic V1" },
  { value: "deterministic_v1", label: "Deterministic V1 (alias)" },
];

const SPLITS = ["train", "validation", "test"];

export default function PipelineConfigPanel() {
  const {
    noteText,
    pipeline,
    split,
    sourceRowIndex,
    setNoteText,
    setPipeline,
    setSplit,
    setSourceRowIndex,
    ablationConfig,
  } = useConfigStore();
  const { goldOverlay, toggleGoldOverlay } = useUiStore();
  const runNote = useRunNote();
  const rulesQuery = useRules();
  const recordsQuery = useRecords(split);
  const recordQuery = useRecord(split, sourceRowIndex);

  // When a record is loaded from the dataset, update the note text
  useEffect(() => {
    if (recordQuery.data?.note_text) {
      setNoteText(recordQuery.data.note_text);
    }
  }, [recordQuery.data, setNoteText]);

  const handleRun = () => {
    if (!noteText.trim()) return;
    runNote.mutate({
      note_text: noteText,
      pipeline,
      source_row_index: sourceRowIndex ?? 0,
      ablation_config: ablationConfig,
    });
  };

  const selectedRecord = recordsQuery.data?.records.find(
    (r) => r.source_row_index === sourceRowIndex
  );

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-border pb-3">
        <Settings2 className="h-4 w-4 text-deterministic" />
        <h2 className="text-xs font-semibold uppercase tracking-widest text-foreground">
          Configuration
        </h2>
      </div>

      {/* Pipeline selector */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">
          Pipeline
        </label>
        <select
          className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground shadow-sm outline-none transition-colors focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
          value={pipeline}
          onChange={(e) => setPipeline(e.target.value as PipelineFamily)}
        >
          {PIPELINE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {/* Dataset loader */}
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <Database className="h-3.5 w-3.5 text-muted" />
          <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Dataset
          </label>
        </div>
        <div className="flex gap-2">
          <select
            className="flex-1 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground shadow-sm outline-none transition-colors focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
            value={split ?? ""}
            onChange={(e) => setSplit(e.target.value || null)}
          >
            <option value="">Select split…</option>
            {SPLITS.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
          <select
            className="flex-[2] rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground shadow-sm outline-none transition-colors focus:border-deterministic focus:ring-1 focus:ring-deterministic/20 disabled:opacity-50"
            value={sourceRowIndex ?? ""}
            onChange={(e) =>
              setSourceRowIndex(
                e.target.value ? parseInt(e.target.value, 10) : null
              )
            }
            disabled={!recordsQuery.data}
          >
            <option value="">Select row…</option>
            {recordsQuery.data?.records.map((r) => (
              <option key={r.source_row_index} value={r.source_row_index}>
                Row {r.source_row_index} — {r.gold_label}
              </option>
            ))}
          </select>
        </div>
        {recordsQuery.data && (
          <p className="text-[10px] text-muted">
            {recordsQuery.data.count} records available in {split}
          </p>
        )}
      </div>

      {/* Note input */}
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <FileText className="h-3.5 w-3.5 text-muted" />
          <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Note text
          </label>
        </div>
        <textarea
          className="h-28 w-full resize-y rounded-lg border border-border bg-surface p-3 text-sm text-foreground shadow-sm outline-none transition-colors focus:border-deterministic focus:ring-1 focus:ring-deterministic/20 font-sans leading-relaxed"
          placeholder="Paste a clinical note here, or select a dataset row above…"
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
        />
        {selectedRecord && (
          <p className="text-[10px] text-muted">
            Loaded from {split} row {selectedRecord.source_row_index}
            {selectedRecord.row_ok ? "" : " (row_ok=false)"}
          </p>
        )}
      </div>

      {/* Run button */}
      <button
        onClick={handleRun}
        disabled={runNote.isPending || !noteText.trim()}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-deterministic px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-deterministic/90 hover:shadow disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
      >
        <Play className="h-4 w-4" />
        {runNote.isPending ? "Running pipeline…" : "Run Pipeline"}
      </button>

      {runNote.isError && (
        <div className="rounded-lg bg-error/10 p-3 text-xs text-error border border-error/20">
          {runNote.error instanceof Error ? runNote.error.message : "Run failed"}
        </div>
      )}

      {/* Toggles */}
      <div className="space-y-2 rounded-lg border border-border bg-surface-raised/50 p-3">
        <label className="flex cursor-pointer items-center gap-2.5">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-border text-deterministic focus:ring-deterministic"
            checked={goldOverlay}
            onChange={toggleGoldOverlay}
          />
          <span className="text-xs text-foreground">Show gold label overlay</span>
        </label>
      </div>

      {/* Rules summary */}
      {rulesQuery.data && (
        <div className="space-y-2">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Rules ({rulesQuery.data.rules.length} total)
          </p>
          <div className="grid grid-cols-2 gap-1.5">
            {rulesQuery.data.groups.map((group) => {
              const count = rulesQuery.data.rules.filter(
                (r) => r.group === group
              ).length;
              return (
                <div
                  key={group}
                  className="rounded-md bg-surface-raised px-2 py-1.5 text-[10px]"
                >
                  <span className="font-mono text-muted">{group}</span>
                  <span className="ml-1 text-foreground font-medium">{count}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
