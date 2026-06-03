"use client";

import { useMemo } from "react";
import { Check, X, Info } from "lucide-react";
import * as Tooltip from "@radix-ui/react-tooltip";
import type { RulePayload, AblationConfigPayload } from "@/lib/types";

function groupRules(rules: RulePayload[]) {
  const map = new Map<string, RulePayload[]>();
  for (const rule of rules) {
    const list = map.get(rule.group) ?? [];
    list.push(rule);
    map.set(rule.group, list);
  }
  return map;
}

function portabilityBadgeColor(p: string | null): string {
  if (!p) return "bg-muted/10 text-muted";
  if (p === "general") return "bg-success/10 text-success";
  if (p === "task_specific") return "bg-deterministic-alt/10 text-deterministic-alt";
  if (p === "dataset_specific") return "bg-llm/10 text-llm";
  return "bg-muted/10 text-muted";
}

function groupBorderColor(group: string): string {
  if (group.includes("rate")) return "border-deterministic-alt/30";
  if (group.includes("temporal")) return "border-success/30";
  if (group.includes("diary")) return "border-hybrid/30";
  if (group.includes("repair")) return "border-muted/30";
  return "border-border";
}

interface RuleInventoryProps {
  rules: RulePayload[];
  ablationConfig: AblationConfigPayload;
  onToggleGroup: (group: string) => void;
  onToggleRule: (ruleId: string) => void;
}

export default function RuleInventory({
  rules,
  ablationConfig,
  onToggleGroup,
  onToggleRule,
}: RuleInventoryProps) {
  const grouped = useMemo(() => groupRules(rules), [rules]);
  const groups = Array.from(grouped.keys()).sort();

  if (rules.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
        <p className="text-sm font-medium text-muted">No rules match your filters</p>
      </div>
    );
  }

  return (
    <Tooltip.Provider delayDuration={200}>
      <div className="space-y-4">
        {groups.map((group) => {
          const groupRules = grouped.get(group) ?? [];
          const groupEnabled = ablationConfig.enabled_groups
            ? ablationConfig.enabled_groups.includes(group)
            : true;

          return (
            <div
              key={group}
              className={`rounded-xl border ${groupBorderColor(group)} bg-surface p-4`}
            >
              <div className="flex items-center justify-between mb-3">
                <button
                  onClick={() => onToggleGroup(group)}
                  className="flex items-center gap-2 text-sm font-semibold text-foreground hover:text-deterministic transition-colors"
                >
                  {groupEnabled ? (
                    <Check className="h-3.5 w-3.5 text-success" />
                  ) : (
                    <X className="h-3.5 w-3.5 text-error" />
                  )}
                  <span className={groupEnabled ? "" : "line-through text-muted"}>
                    {group.replace(/_/g, " ")}
                  </span>
                </button>
                <span className="text-[10px] text-muted">
                  {groupRules.length} rule{groupRules.length !== 1 ? "s" : ""}
                </span>
              </div>

              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {groupRules.map((rule) => {
                  const disabled = ablationConfig.disabled_rule_ids?.includes(rule.rule_id) ?? false;
                  const globallyOff = !groupEnabled;
                  const inactive = globallyOff || disabled;

                  return (
                    <Tooltip.Root key={rule.rule_id}>
                      <Tooltip.Trigger asChild>
                        <button
                          onClick={() => onToggleRule(rule.rule_id)}
                          disabled={globallyOff}
                          className={`flex flex-col gap-1 rounded-lg border px-3 py-2.5 text-left transition-all ${
                            inactive
                              ? "border-border/40 bg-surface-raised/30 opacity-60"
                              : "border-border bg-surface hover:border-deterministic/40 hover:shadow-sm"
                          }`}
                        >
                          <div className="flex items-center gap-1.5">
                            <span
                              className={`rounded px-1 py-0 text-[10px] font-mono font-medium ${
                                inactive
                                  ? "bg-muted/10 text-muted"
                                  : "bg-deterministic/10 text-deterministic"
                              }`}
                            >
                              {rule.rule_id}
                            </span>
                            <span
                              className={`rounded px-1 py-0 text-[9px] font-medium uppercase tracking-wide ${portabilityBadgeColor(rule.portability)}`}
                            >
                              {rule.portability?.replace(/_/g, " ") ?? "unknown"}
                            </span>
                          </div>
                          <span
                            className={`text-[11px] leading-snug ${
                              inactive ? "text-muted" : "text-foreground"
                            }`}
                          >
                            {rule.description}
                          </span>
                          {rule.regex_preview && (
                            <span className="text-[10px] font-mono text-muted truncate">
                              {rule.regex_preview.slice(0, 50)}
                              {rule.regex_preview.length > 50 ? "…" : ""}
                            </span>
                          )}
                        </button>
                      </Tooltip.Trigger>
                      <Tooltip.Portal>
                        <Tooltip.Content
                          side="top"
                          sideOffset={6}
                          className="z-50 max-w-sm rounded-lg border border-border bg-surface px-3 py-2 shadow-lg"
                        >
                          <div className="space-y-1.5">
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-mono font-semibold text-deterministic">
                                {rule.rule_id}
                              </span>
                              <span
                                className={`rounded px-1 py-0 text-[9px] font-medium uppercase tracking-wide ${portabilityBadgeColor(rule.portability)}`}
                              >
                                {rule.portability?.replace(/_/g, " ") ?? "unknown"}
                              </span>
                            </div>
                            <p className="text-[11px] text-foreground">{rule.description}</p>
                            {rule.regex_preview && (
                              <code className="block rounded bg-surface-raised px-1.5 py-0.5 text-[10px] font-mono text-muted">
                                {rule.regex_preview}
                              </code>
                            )}
                            {rule.has_exclusions && (
                              <div className="flex items-center gap-1 text-[10px] text-error">
                                <Info className="h-3 w-3" />
                                Has exclusion patterns
                              </div>
                            )}
                            {rule.examples && rule.examples.length > 0 && (
                              <div className="border-t border-border pt-1.5 mt-1">
                                <p className="text-[9px] font-semibold uppercase tracking-wide text-muted mb-1">
                                  Examples
                                </p>
                                <div className="space-y-1">
                                  {rule.examples.slice(0, 2).map((ex, i) => (
                                    <div key={i} className="text-[10px] text-foreground">
                                      <span className="text-muted">“{ex.text}”</span>
                                      {ex.expected_label && (
                                        <span className="text-success"> → {ex.expected_label}</span>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                          <Tooltip.Arrow className="fill-surface" />
                        </Tooltip.Content>
                      </Tooltip.Portal>
                    </Tooltip.Root>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </Tooltip.Provider>
  );
}
