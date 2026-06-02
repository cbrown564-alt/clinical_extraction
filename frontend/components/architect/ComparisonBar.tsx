"use client";

import { GitCompare, Save, RotateCcw } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import { useConfigStore } from "@/lib/stores";

export default function ComparisonBar() {
  const compareMode = useArchitectStore((s) => s.compareMode);
  const toggleCompareMode = useArchitectStore((s) => s.toggleCompareMode);
  const configA = useArchitectStore((s) => s.configA);
  const configB = useArchitectStore((s) => s.configB);
  const activeConfigLabel = useArchitectStore((s) => s.activeConfigLabel);
  const saveConfig = useArchitectStore((s) => s.saveConfig);
  const loadConfig = useArchitectStore((s) => s.loadConfig);
  const setActiveConfigLabel = useArchitectStore((s) => s.setActiveConfigLabel);
  const nodes = useArchitectStore((s) => s.nodes);
  const ablationConfig = useConfigStore((s) => s.ablationConfig);
  const pipeline = useConfigStore((s) => s.pipeline);

  return (
    <div className="border-b border-border bg-surface px-4 py-2.5 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <label className="flex cursor-pointer items-center gap-2 rounded-lg border border-border bg-surface-raised/50 px-3 py-1.5">
          <input
            type="checkbox"
            className="h-4 w-4 rounded border-border text-hybrid focus:ring-hybrid"
            checked={compareMode}
            onChange={toggleCompareMode}
          />
          <span className="text-xs text-foreground flex items-center gap-1.5 font-medium">
            <GitCompare className="h-3.5 w-3.5 text-hybrid" />
            Compare mode
          </span>
        </label>

        {compareMode && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setActiveConfigLabel("a");
                loadConfig("a");
              }}
              className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[11px] font-medium border transition-colors ${
                activeConfigLabel === "a"
                  ? "bg-deterministic/10 text-deterministic border-deterministic/30"
                  : "bg-surface-raised text-muted border-border hover:text-foreground"
              }`}
            >
              <span className="font-mono">A</span>
              <span className="truncate max-w-[80px]">{configA?.name ?? "Unsaved"}</span>
            </button>
            <span className="text-muted text-xs">vs</span>
            <button
              onClick={() => {
                setActiveConfigLabel("b");
                loadConfig("b");
              }}
              className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-[11px] font-medium border transition-colors ${
                activeConfigLabel === "b"
                  ? "bg-llm/10 text-llm border-llm/30"
                  : "bg-surface-raised text-muted border-border hover:text-foreground"
              }`}
            >
              <span className="font-mono">B</span>
              <span className="truncate max-w-[80px]">{configB?.name ?? "Unsaved"}</span>
            </button>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        {compareMode && (
          <>
            <button
              onClick={() => saveConfig(activeConfigLabel, `Config ${activeConfigLabel.toUpperCase()}`, pipeline, ablationConfig)}
              className="flex items-center gap-1.5 rounded-md bg-surface-raised border border-border px-2.5 py-1 text-[11px] font-medium text-foreground hover:bg-surface-raised/80 transition-colors"
            >
              <Save className="h-3 w-3" />
              Save {activeConfigLabel.toUpperCase()}
            </button>
            <button
              onClick={() => loadConfig(activeConfigLabel === "a" ? "b" : "a")}
              className="flex items-center gap-1.5 rounded-md bg-surface-raised border border-border px-2.5 py-1 text-[11px] font-medium text-foreground hover:bg-surface-raised/80 transition-colors"
            >
              <RotateCcw className="h-3 w-3" />
              Load {activeConfigLabel === "a" ? "B" : "A"}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
