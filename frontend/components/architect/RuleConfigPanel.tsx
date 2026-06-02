"use client";

import * as Collapsible from "@radix-ui/react-collapsible";
import { useState } from "react";
import { SlidersHorizontal, ChevronDown, Check, X } from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import { useRules } from "@/lib/hooks";
import type { RulesResponse, RulePayload } from "@/lib/types";

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

export default function RuleConfigPanel() {
  const [open, setOpen] = useState(false);
  const { ablationConfig, toggleRuleGroup, toggleRuleId } = useArchitectStore();
  const rulesQuery = useRules();

  if (!rulesQuery.data) return null;

  const data = rulesQuery.data as RulesResponse;
  const grouped = groupRules(data.rules);
  const groups = Array.from(grouped.keys()).sort();

  return (
    <Collapsible.Root open={open} onOpenChange={setOpen}>
      <Collapsible.Trigger asChild>
        <button
          className={`flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-medium transition-all ${
            open
              ? "border-deterministic bg-deterministic/5 text-deterministic"
              : "border-border bg-surface text-foreground hover:bg-surface-raised"
          }`}
        >
          <SlidersHorizontal className="h-3.5 w-3.5" />
          <span>Rules</span>
          <ChevronDown
            className={`h-3 w-3 transition-transform ${open ? "rotate-180" : ""}`}
          />
        </button>
      </Collapsible.Trigger>

      <Collapsible.Content>
        <div className="mt-2 rounded-xl border border-border bg-surface p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-[11px] font-semibold uppercase tracking-wide text-muted">
              Rule Configuration
            </span>
            <span className="text-[10px] text-muted">
              {data.rules.length} rules across {groups.length} groups
            </span>
          </div>

          <div className="space-y-4">
            {groups.map((group) => {
              const groupRules = grouped.get(group) ?? [];
              const groupEnabled = ablationConfig.enabled_groups
                ? ablationConfig.enabled_groups.includes(group)
                : true;

              return (
                <div key={group} className="rounded-lg border border-border bg-surface-raised/40 p-3">
                  <div className="flex items-center justify-between mb-2">
                    <button
                      onClick={() => toggleRuleGroup(group)}
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
                        <button
                          key={rule.rule_id}
                          onClick={() => toggleRuleId(rule.rule_id)}
                          disabled={globallyOff}
                          className={`flex flex-col gap-1 rounded-md border px-2.5 py-2 text-left transition-all ${
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
                              {rule.regex_preview.slice(0, 40)}
                              {rule.regex_preview.length > 40 ? "…" : ""}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </Collapsible.Content>
    </Collapsible.Root>
  );
}
