"use client";

import { Play, Database, Settings2, FileText, GitCompare, AlertCircle, Ban, Loader2 } from "lucide-react";
import { useConfigStore, useUiStore } from "@/lib/stores";
import { useRunNote, useRules, useRecords, useRecord, usePipelineFamilies } from "@/lib/hooks";
import type { PipelineFamily } from "@/lib/types";
import { useEffect } from "react";

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
    toggleRuleGroup,
    toggleRuleId,
    comparePipeline,
    compareAblationConfig,
    setComparePipeline,
    setCompareAblationConfig,
  } = useConfigStore();
  const { goldOverlay, toggleGoldOverlay, showDiff, toggleShowDiff } = useUiStore();
  const runNote = useRunNote();
  const rulesQuery = useRules();
  const recordsQuery = useRecords(split);
  const recordQuery = useRecord(split, sourceRowIndex);
  const familiesQuery = usePipelineFamilies();

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

  const pipelineOptions = familiesQuery.data?.families ?? [
    { value: "rules_only" as PipelineFamily, label: "Deterministic V1", executable: true, kind: "rules_only" as const },
    { value: "deterministic_v1" as PipelineFamily, label: "Deterministic V1 (alias)", executable: true, kind: "rules_only" as const },
  ];

  const selectedFamily = pipelineOptions.find((f) => f.value === pipeline);
  const isExecutable = selectedFamily?.executable ?? true;

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
          {pipelineOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
              {!opt.executable ? " (introspection only)" : ""}
            </option>
          ))}
        </select>
        {selectedFamily && !selectedFamily.executable && (
          <div className="flex items-center gap-1.5 rounded-md bg-llm-alt/10 px-2 py-1 text-[10px] text-llm border border-llm-alt/20">
            <AlertCircle className="h-3 w-3" />
            This pipeline is not yet executable via the Observatory API.
          </div>
        )}
      </div>

      {/* Diff mode toggle */}
      <div className="space-y-2 rounded-lg border border-border bg-surface-raised/50 p-3">
        <label className="flex cursor-pointer items-center gap-2.5">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-border text-hybrid focus:ring-hybrid"
            checked={showDiff}
            onChange={toggleShowDiff}
          />
          <span className="text-xs text-foreground flex items-center gap-1.5">
            <GitCompare className="h-3.5 w-3.5 text-hybrid" />
            Compare mode (A vs B)
          </span>
        </label>
        {showDiff && (
          <div className="space-y-1.5 pt-1 border-t border-border mt-2">
            <label className="text-[10px] font-semibold uppercase tracking-wide text-muted">
              Compare pipeline (B)
            </label>
            <select
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground shadow-sm outline-none transition-colors focus:border-hybrid focus:ring-1 focus:ring-hybrid/20"
              value={comparePipeline}
              onChange={(e) => setComparePipeline(e.target.value as PipelineFamily)}
            >
              {pipelineOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                  {!opt.executable ? " (introspection only)" : ""}
                </option>
              ))}
            </select>
          </div>
        )}
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
        disabled={runNote.isPending || !noteText.trim() || !isExecutable}
        className="flex w-full items-center justify-center gap-2 rounded-lg bg-deterministic px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-deterministic/90 hover:shadow disabled:opacity-50 disabled:cursor-not-allowed active:scale-[0.98]"
      >
        {runNote.isPending ? (
          <Loader2 className="h-4 w-4 shrink-0 animate-spin" />
        ) : !isExecutable ? (
          <Ban className="h-4 w-4 shrink-0" />
        ) : (
          <Play className="h-4 w-4 shrink-0" />
        )}
        <span className="truncate">
          {runNote.isPending
            ? "Running pipeline…"
            : !isExecutable
            ? "Pipeline not executable"
            : "Run Pipeline"}
        </span>
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

      {/* Rules inventory with toggles */}
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
              const enabled = ablationConfig.enabled_groups
                ? ablationConfig.enabled_groups.includes(group)
                : true; // default all enabled
              return (
                <button
                  key={group}
                  onClick={() => toggleRuleGroup(group)}
                  className={`rounded-md px-2 py-1.5 text-[10px] text-left transition-colors border ${
                    enabled
                      ? "bg-surface-raised text-foreground border-border"
                      : "bg-surface-raised/40 text-muted border-border/40 line-through"
                  }`}
                >
                  <span className="font-mono text-muted">{group}</span>
                  <span className="ml-1 font-medium">{count}</span>
                </button>
              );
            })}
          </div>
          <div className="max-h-40 overflow-y-auto space-y-1 rounded-md border border-border bg-surface-raised/40 p-2">
            {rulesQuery.data.rules.map((rule) => {
              const disabled = ablationConfig.disabled_rule_ids?.includes(
                rule.rule_id
              );
              return (
                <button
                  key={rule.rule_id}
                  onClick={() => toggleRuleId(rule.rule_id)}
                  className={`flex w-full items-center gap-2 rounded px-1.5 py-1 text-[10px] text-left transition-colors ${
                    disabled
                      ? "text-muted/60 line-through"
                      : "text-foreground hover:bg-surface-raised"
                  }`}
                  title={rule.description}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full shrink-0 ${
                      disabled ? "bg-muted/30" : "bg-deterministic"
                    }`}
                  />
                  <span className="font-mono truncate">{rule.rule_id}</span>
                  <span className="text-muted truncate ml-auto">
                    {rule.portability}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
