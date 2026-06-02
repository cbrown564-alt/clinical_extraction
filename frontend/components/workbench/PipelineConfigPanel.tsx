"use client";

import { Play, Settings2 } from "lucide-react";
import { useConfigStore, useUiStore } from "@/lib/stores";
import { useRunNote, useRules } from "@/lib/hooks";
import type { PipelineFamily } from "@/lib/types";
import * as Tooltip from "@radix-ui/react-tooltip";

const PIPELINE_OPTIONS: { value: PipelineFamily; label: string }[] = [
  { value: "rules_only", label: "Deterministic V1" },
  { value: "deterministic_v1", label: "Deterministic V1 (alias)" },
];

export default function PipelineConfigPanel() {
  const { noteText, pipeline, setNoteText, setPipeline, ablationConfig } =
    useConfigStore();
  const { goldOverlay, toggleGoldOverlay } = useUiStore();
  const runNote = useRunNote();
  const rulesQuery = useRules();

  const handleRun = () => {
    if (!noteText.trim()) return;
    runNote.mutate({
      note_text: noteText,
      pipeline,
      ablation_config: ablationConfig,
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Settings2 className="h-4 w-4 text-muted" />
        <h2 className="text-sm font-semibold uppercase tracking-wide text-foreground">
          Configuration
        </h2>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium text-muted">Pipeline</label>
        <select
          className="w-full rounded-md border border-border bg-surface px-2 py-1.5 text-sm text-foreground outline-none focus:border-deterministic"
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

      <div className="space-y-2">
        <label className="text-xs font-medium text-muted">Clinical Note</label>
        <textarea
          className="h-32 w-full resize-y rounded-md border border-border bg-surface p-2 text-sm text-foreground outline-none focus:border-deterministic font-sans"
          placeholder="Paste a clinical note here..."
          value={noteText}
          onChange={(e) => setNoteText(e.target.value)}
        />
      </div>

      <button
        onClick={handleRun}
        disabled={runNote.isPending || !noteText.trim()}
        className="flex w-full items-center justify-center gap-2 rounded-md bg-deterministic px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-deterministic/90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Play className="h-4 w-4" />
        {runNote.isPending ? "Running…" : "Run Pipeline"}
      </button>

      {runNote.isError && (
        <div className="rounded-md bg-error/10 p-2 text-xs text-error">
          {runNote.error instanceof Error ? runNote.error.message : "Run failed"}
        </div>
      )}

      <div className="border-t border-border pt-3">
        <label className="flex cursor-pointer items-center gap-2">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-border text-deterministic focus:ring-deterministic"
            checked={goldOverlay}
            onChange={toggleGoldOverlay}
          />
          <span className="text-xs text-foreground">Show gold label overlay</span>
        </label>
      </div>

      {rulesQuery.data && (
        <div className="border-t border-border pt-3">
          <p className="mb-2 text-xs font-medium text-muted">
            Rules ({rulesQuery.data.rules.length} total)
          </p>
          <div className="max-h-40 overflow-y-auto space-y-1">
            {rulesQuery.data.groups.map((group) => (
              <div key={group} className="text-xs">
                <span className="rounded bg-surface-raised px-1.5 py-0.5 font-mono text-muted">
                  {group}
                </span>
                <span className="ml-1 text-muted">
                  {rulesQuery.data.rules.filter((r) => r.group === group).length}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
