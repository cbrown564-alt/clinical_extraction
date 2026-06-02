"use client";

import { X, Settings2, GitBranch, Layers, Wrench, Award } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import { useRules, usePipelineFamilies } from "@/lib/hooks";
import type { NodeFamily, PipelineFamily } from "@/lib/types";

const typeIcons: Record<string, React.ReactNode> = {
  extractor: <GitBranch className="h-4 w-4" />,
  normaliser: <Layers className="h-4 w-4" />,
  selector: <Settings2 className="h-4 w-4" />,
  repair: <Wrench className="h-4 w-4" />,
  scorer: <Award className="h-4 w-4" />,
};

const familyOptions: { value: NodeFamily; label: string }[] = [
  { value: "rules_only", label: "Deterministic" },
  { value: "llm_only", label: "LLM" },
  { value: "hybrid", label: "Hybrid" },
];

export default function NodeDrawer() {
  const selectedNodeId = useArchitectStore((s) => s.selectedNodeId);
  const nodes = useArchitectStore((s) => s.nodes);
  const updateNode = useArchitectStore((s) => s.updateNode);
  const setSelectedNodeId = useArchitectStore((s) => s.setSelectedNodeId);
  const rulesQuery = useRules();
  const familiesQuery = usePipelineFamilies();

  const node = nodes.find((n) => n.id === selectedNodeId);
  if (!node) return null;

  const pipelineOptions =
    familiesQuery.data?.families.filter((f) => {
      if (node.family === "rules_only") return f.kind === "rules_only";
      if (node.family === "llm_only") return f.kind === "llm_only";
      if (node.family === "hybrid") return f.kind === "hybrid";
      return true;
    }) ?? [];

  return (
    <div className="w-80 border-l border-border bg-surface flex flex-col h-full shadow-lg z-20">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <div className="text-muted">{typeIcons[node.type]}</div>
          <div>
            <h3 className="text-sm font-semibold text-foreground">{node.label}</h3>
            <p className="text-[10px] text-muted font-mono uppercase">{node.type}</p>
          </div>
        </div>
        <button
          onClick={() => setSelectedNodeId(null)}
          className="rounded-md p-1 text-muted hover:bg-surface-raised hover:text-foreground transition-colors"
        >
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Family selector */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Component Family
          </label>
          <div className="grid grid-cols-3 gap-2">
            {familyOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => updateNode(node.id, { family: opt.value })}
                className={`rounded-lg border px-2 py-2 text-[11px] font-medium transition-all
                  ${
                    node.family === opt.value
                      ? opt.value === "rules_only"
                        ? "border-deterministic bg-deterministic/10 text-deterministic"
                        : opt.value === "llm_only"
                        ? "border-llm bg-llm/10 text-llm"
                        : "border-hybrid bg-hybrid/10 text-hybrid"
                      : "border-border bg-surface-raised text-muted hover:text-foreground"
                  }
                `}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        {/* Pipeline family selector */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold uppercase tracking-wide text-muted">
            Pipeline Implementation
          </label>
          <select
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground shadow-sm outline-none transition-colors focus:border-deterministic focus:ring-1 focus:ring-deterministic/20"
            value={node.pipelineFamily ?? ""}
            onChange={(e) =>
              updateNode(node.id, { pipelineFamily: e.target.value as PipelineFamily })
            }
          >
            <option value="">Select implementation…</option>
            {pipelineOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
                {!opt.executable ? " (introspection only)" : ""}
              </option>
            ))}
          </select>
        </div>

        {/* Rules toggles (only for rules_only family) */}
        {node.family === "rules_only" && rulesQuery.data && (
          <div className="space-y-2">
            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted">
              Active Rule Groups
            </p>
            <div className="grid grid-cols-2 gap-1.5">
              {rulesQuery.data.groups.map((group) => {
                const count = rulesQuery.data.rules.filter((r) => r.group === group).length;
                const enabled = node.ablationConfig?.enabled_groups
                  ? node.ablationConfig.enabled_groups.includes(group)
                  : true;
                return (
                  <button
                    key={group}
                    onClick={() => {
                      const current = new Set(node.ablationConfig?.enabled_groups ?? []);
                      if (current.has(group)) current.delete(group);
                      else current.add(group);
                      updateNode(node.id, {
                        ablationConfig: {
                          ...node.ablationConfig,
                          enabled_groups: Array.from(current),
                        },
                      });
                    }}
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

            <p className="text-[11px] font-semibold uppercase tracking-wide text-muted pt-2">
              Disabled Rules
            </p>
            <div className="max-h-40 overflow-y-auto space-y-1 rounded-md border border-border bg-surface-raised/40 p-2">
              {rulesQuery.data.rules.map((rule) => {
                const disabled = node.ablationConfig?.disabled_rule_ids?.includes(rule.rule_id);
                return (
                  <button
                    key={rule.rule_id}
                    onClick={() => {
                      const current = new Set(node.ablationConfig?.disabled_rule_ids ?? []);
                      if (current.has(rule.rule_id)) current.delete(rule.rule_id);
                      else current.add(rule.rule_id);
                      updateNode(node.id, {
                        ablationConfig: {
                          ...node.ablationConfig,
                          disabled_rule_ids: Array.from(current),
                        },
                      });
                    }}
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
                    <span className="text-muted truncate ml-auto">{rule.portability}</span>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
