"use client";

import { useMemo, useState } from "react";
import { Info, AlertTriangle, ChevronDown, ChevronRight } from "lucide-react";
import * as Switch from "@radix-ui/react-switch";
import * as Collapsible from "@radix-ui/react-collapsible";
import * as Tooltip from "@radix-ui/react-tooltip";
import type { RulePayload, AblationConfigPayload } from "@/lib/types";
import RegexHighlighter from "./RegexHighlighter";

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

function groupColor(group: string): string {
  if (group.includes("rate")) return "#4a6fa5";
  if (group.includes("temporal")) return "#81b29a";
  if (group.includes("diary")) return "#7c3aed";
  if (group.includes("cluster")) return "#d97706";
  if (group.includes("seizure_free")) return "#2a6f6f";
  if (group.includes("repair")) return "#9ca3af";
  return "#6b7280";
}

function groupIcon(group: string): string {
  if (group.includes("rate")) return "⚡";
  if (group.includes("temporal")) return "🕐";
  if (group.includes("diary")) return "📓";
  if (group.includes("cluster")) return "🔀";
  if (group.includes("seizure_free")) return "✓";
  if (group.includes("repair")) return "🔧";
  if (group.includes("shorthand")) return "⌨";
  return "◆";
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

  const enabledGroups = new Set(ablationConfig.enabled_groups ?? groups);
  const disabledIds = new Set(ablationConfig.disabled_rule_ids ?? []);

  // Track which groups are expanded; default all open
  const [openGroups, setOpenGroups] = useState<Set<string>>(new Set(groups));

  const toggleGroupOpen = (group: string) => {
    setOpenGroups((prev) => {
      const next = new Set(prev);
      if (next.has(group)) next.delete(group);
      else next.add(group);
      return next;
    });
  };

  if (rules.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
        <p className="text-sm font-medium text-muted">No rules match your filters</p>
      </div>
    );
  }

  return (
    <Tooltip.Provider delayDuration={150}>
      <div className="columns-1 xl:columns-2 gap-4">
        {groups.map((group) => {
          const groupRulesList = grouped.get(group) ?? [];
          const groupEnabled = enabledGroups.has(group);
          const groupColorValue = groupColor(group);
          const activeInGroup = groupRulesList.filter(
            (r) => !disabledIds.has(r.rule_id)
          ).length;
          const isOpen = openGroups.has(group);

          return (
            <div key={group} className="break-inside-avoid mb-4">
            <Collapsible.Root
              open={isOpen}
              onOpenChange={() => toggleGroupOpen(group)}
              className={`overflow-hidden transition-[background-color,border-color,opacity,box-shadow] ${
                isOpen
                  ? `rounded-xl border bg-surface ${
                      groupEnabled
                        ? "border-border shadow-sm"
                        : "border-border/40 opacity-70"
                    }`
                  : `rounded-lg border bg-surface/60 ${
                      groupEnabled
                        ? "border-border/40"
                        : "border-border/30 opacity-60"
                    }`
              }`}
            >
              {/* Group header – always visible */}
              <div
                className={`relative flex items-center gap-3 cursor-pointer select-none ${
                  isOpen ? "px-4 py-3" : "px-3 py-2"
                }`}
                style={{
                  backgroundColor: groupEnabled && isOpen ? `${groupColorValue}06` : undefined,
                }}
              >
                {/* Color accent bar */}
                <div
                  className="absolute left-0 top-0 bottom-0 w-1"
                  style={{ backgroundColor: groupEnabled ? groupColorValue : "#d1d5db" }}
                />

                {/* Expand/collapse chevron */}
                <Collapsible.Trigger asChild>
                  <button className="flex items-center justify-center h-6 w-6 rounded-md hover:bg-black/5 transition-colors shrink-0">
                    {isOpen ? (
                      <ChevronDown className="h-4 w-4 text-muted" />
                    ) : (
                      <ChevronRight className="h-4 w-4 text-muted" />
                    )}
                  </button>
                </Collapsible.Trigger>

                {/* Icon */}
                <span className="text-base shrink-0">{groupIcon(group)}</span>

                {/* Group info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <h3
                      className={`text-sm font-bold truncate ${
                        groupEnabled ? "text-foreground" : "text-muted line-through"
                      }`}
                    >
                      {group.replace(/_/g, " ")}
                    </h3>
                    {!groupEnabled && (
                      <span className="rounded bg-muted/10 px-1.5 py-0 text-[11px] font-medium text-muted uppercase tracking-wide shrink-0">
                        Off
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-[11px] text-muted">
                      {groupRulesList.length} rules
                    </span>
                    <span className="text-[11px] text-border">·</span>
                    <span
                      className={`text-[11px] font-medium ${
                        groupEnabled && activeInGroup === groupRulesList.length
                          ? "text-success"
                          : groupEnabled && activeInGroup > 0
                          ? "text-llm"
                          : "text-muted"
                      }`}
                    >
                      {groupEnabled ? activeInGroup : 0} / {groupRulesList.length} active
                    </span>
                  </div>
                </div>

                {/* Group toggle switch */}
                <Switch.Root
                  checked={groupEnabled}
                  onCheckedChange={() => onToggleGroup(group)}
                  className="relative h-5 w-9 rounded-full bg-muted/30 data-[state=checked]:bg-success transition-colors outline-none focus:ring-2 focus:ring-success/30 shrink-0"
                >
                  <Switch.Thumb className="block h-4 w-4 translate-x-0.5 rounded-full bg-surface shadow-sm transition-transform data-[state=checked]:translate-x-4" />
                </Switch.Root>
              </div>

              {/* Collapsible rule list */}
              <Collapsible.Content>
                <div className="border-t border-border/50">
                  {groupRulesList.map((rule, idx) => {
                    const ruleDisabled = disabledIds.has(rule.rule_id);
                    const ruleActive = groupEnabled && !ruleDisabled;

                    return (
                      <Tooltip.Root key={rule.rule_id}>
                        <Tooltip.Trigger asChild>
                          <div
                            className={`flex items-start gap-3 px-4 py-2.5 transition-colors ${
                              idx !== groupRulesList.length - 1
                                ? "border-b border-border/30"
                                : ""
                            } ${
                              ruleActive
                                ? "bg-surface hover:bg-surface-raised/40"
                                : "bg-surface-raised/20 opacity-50"
                            }`}
                          >
                            {/* Rule toggle */}
                            <Switch.Root
                              checked={ruleActive}
                              onCheckedChange={() => onToggleRule(rule.rule_id)}
                              disabled={!groupEnabled}
                              className="relative h-4 w-7 rounded-full bg-muted/30 data-[state=checked]:bg-deterministic disabled:opacity-30 transition-colors outline-none focus:ring-2 focus:ring-deterministic/30 shrink-0 mt-0.5"
                            >
                              <Switch.Thumb className="block h-3 w-3 translate-x-0.5 rounded-full bg-surface shadow-sm transition-transform data-[state=checked]:translate-x-3" />
                            </Switch.Root>

                            {/* Rule content */}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <span className="text-xs font-mono font-semibold text-deterministic">
                                  {rule.rule_id}
                                </span>
                                <span
                                  className={`rounded px-1 py-0 text-[11px] font-medium uppercase tracking-wide ${portabilityBadgeColor(rule.portability)}`}
                                >
                                  {rule.portability?.replace(/_/g, " ") ?? "unknown"}
                                </span>
                                {rule.has_exclusions && (
                                  <AlertTriangle className="h-3 w-3 text-error shrink-0" />
                                )}
                              </div>
                              <p
                                className={`text-xs leading-snug mt-0.5 ${
                                  ruleActive ? "text-foreground" : "text-muted"
                                }`}
                              >
                                {rule.description}
                              </p>
                              {rule.regex_preview && (
                                <div className="mt-1.5">
                                  <RegexHighlighter pattern={rule.regex_preview} />
                                </div>
                              )}
                            </div>
                          </div>
                        </Tooltip.Trigger>
                        <Tooltip.Portal>
                          <Tooltip.Content
                            side="top"
                            sideOffset={6}
                            className="z-50 max-w-md rounded-lg border border-border bg-surface px-3 py-2 shadow-lg"
                          >
                            <div className="space-y-1.5">
                              <div className="flex items-center gap-2">
                                <span className="text-[11px] font-mono font-semibold text-deterministic">
                                  {rule.rule_id}
                                </span>
                                <span
                                  className={`rounded px-1 py-0 text-[11px] font-medium uppercase tracking-wide ${portabilityBadgeColor(rule.portability)}`}
                                >
                                  {rule.portability?.replace(/_/g, " ") ?? "unknown"}
                                </span>
                              </div>
                              <p className="text-xs text-foreground">{rule.description}</p>
                              {rule.regex_preview && (
                                <div className="mt-1">
                                  <RegexHighlighter pattern={rule.regex_preview} />
                                </div>
                              )}
                              {rule.has_exclusions && (
                                <div className="flex items-center gap-1 text-[11px] text-error">
                                  <Info className="h-3 w-3" />
                                  Has exclusion patterns
                                </div>
                              )}
                              {rule.examples && rule.examples.length > 0 && (
                                <div className="border-t border-border pt-1.5 mt-1">
                                  <p className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-1">
                                    Examples
                                  </p>
                                  <div className="space-y-1">
                                    {rule.examples.slice(0, 2).map((ex, i) => (
                                      <div key={i} className="text-[11px] text-foreground">
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
              </Collapsible.Content>
            </Collapsible.Root>
            </div>
          );
        })}
      </div>
    </Tooltip.Provider>
  );
}
