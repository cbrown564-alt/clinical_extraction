"use client";

import { Telescope } from "lucide-react";
import type { RegistryEntry } from "@/lib/types";

interface RunSelectorProps {
  runs: RegistryEntry[];
  selectedIds: Set<string>;
  loadingIds: Set<string>;
  errors: Map<string, string>;
  onToggle: (runId: string) => void;
}

function familyColor(family: string): string {
  if (family.includes("rules_only") || family.includes("deterministic")) {
    return "bg-deterministic/10 text-deterministic border-deterministic/20";
  }
  if (family.includes("hybrid")) {
    return "bg-hybrid/10 text-hybrid border-hybrid/20";
  }
  return "bg-llm/10 text-llm border-llm/20";
}

function decisionBadge(decision: string): string {
  switch (decision) {
    case "accept":
      return "bg-success/15 text-success";
    case "reject":
      return "bg-error/15 text-error";
    case "revise":
      return "bg-llm-alt/15 text-llm";
    default:
      return "bg-muted/10 text-muted";
  }
}

export default function RunSelector({ runs, selectedIds, loadingIds, errors, onToggle }: RunSelectorProps) {
  // Group by pipeline family
  const grouped = new Map<string, RegistryEntry[]>();
  for (const run of runs) {
    const list = grouped.get(run.pipeline_family) ?? [];
    list.push(run);
    grouped.set(run.pipeline_family, list);
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <Telescope className="h-4 w-4 text-muted" />
        <h3 className="text-xs font-semibold uppercase tracking-widest text-muted">
          Select Runs
        </h3>
        <span className="text-[10px] text-muted">
          {selectedIds.size} selected
        </span>
      </div>

      <div className="space-y-4">
        {Array.from(grouped.entries()).map(([family, familyRuns]) => (
          <div key={family} className="space-y-1.5">
            <div className="text-[10px] font-semibold uppercase tracking-wider text-muted">
              {family.replace(/_/g, " ")}
            </div>
            <div className="flex flex-wrap gap-2">
              {familyRuns.map((run) => {
                const selected = selectedIds.has(run.run_id);
                const loading = loadingIds.has(run.run_id);
                const error = errors.get(run.run_id);
                const hasJsonl = run.artifact_paths.some((p) => p.endsWith(".jsonl"));

                return (
                  <button
                    key={run.run_id}
                    onClick={() => onToggle(run.run_id)}
                    disabled={loading || !hasJsonl}
                    className={`group relative flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-left transition-all ${
                      selected
                        ? familyColor(family)
                        : "border-border bg-surface text-foreground hover:bg-surface-raised"
                    } ${!hasJsonl ? "opacity-40 cursor-not-allowed" : ""} ${loading ? "animate-pulse" : ""}`}
                    title={error ?? run.run_id}
                  >
                    <span className="text-[11px] font-medium leading-none">
                      {run.run_id.length > 40 ? run.run_id.slice(0, 40) + "…" : run.run_id}
                    </span>
                    <span
                      className={`rounded px-1 py-0 text-[9px] font-medium leading-none ${decisionBadge(
                        run.decision ?? ""
                      )}`}
                    >
                      {run.decision}
                    </span>
                    <span className="text-[9px] text-muted">
                      {run.row_count} rows
                    </span>
                    {selected && (
                      <span className="absolute -top-1 -right-1 flex h-3 w-3 items-center justify-center rounded-full bg-deterministic text-white text-[7px]">
                        ✓
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
