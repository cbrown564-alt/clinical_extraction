"use client";

import { Suspense, useState, useMemo, useCallback } from "react";
import { Search } from "lucide-react";
import { useRules, useRunAblation, useLaboratoryUrlSync } from "@/lib/hooks";
import { useLaboratoryStore } from "@/lib/stores";
import RuleInventory from "@/components/laboratory/RuleInventory";
import SimulationPanel from "@/components/laboratory/SimulationPanel";
import { useActiveDataset } from "@/lib/datasets";
import Exectv2ComponentImpact from "@/components/exectv2/Exectv2ComponentImpact";

function LaboratoryInner() {
  const [search, setSearch] = useState("");
  const [groupFilter, setGroupFilter] = useState<string>("all");
  const [portabilityFilter, setPortabilityFilter] = useState<string>("all");

  // Lifted from SimulationPanel so useRunAblation can cache deterministically
  const [simSplit, setSimSplit] = useState("validation");
  const [simLimit, setSimLimit] = useState<string>("");

  const { ablationConfig, toggleRuleGroup, toggleRuleId, setAblationConfig } = useLaboratoryStore();

  useLaboratoryUrlSync(
    search,
    setSearch,
    groupFilter,
    setGroupFilter,
    portabilityFilter,
    setPortabilityFilter,
    simSplit,
    setSimSplit,
    simLimit,
    setSimLimit,
    ablationConfig,
    setAblationConfig
  );
  const rulesQuery = useRules();

  const limitNum = useMemo(
    () => (simLimit.trim() ? parseInt(simLimit, 10) : undefined),
    [simLimit]
  );

  const runAblation = useRunAblation(simSplit, limitNum, ablationConfig);

  const rules = useMemo(() => rulesQuery.data?.rules ?? [], [rulesQuery.data?.rules]);
  const groups = useMemo(() => rulesQuery.data?.groups ?? [], [rulesQuery.data?.groups]);
  const portabilityLevels = useMemo(() => rulesQuery.data?.portability ?? [], [rulesQuery.data?.portability]);

  const filteredRules = useMemo(() => {
    return rules.filter((r) => {
      if (groupFilter !== "all" && r.group !== groupFilter) return false;
      if (portabilityFilter !== "all" && r.portability !== portabilityFilter) return false;
      if (!search.trim()) return true;
      const q = search.toLowerCase();
      return (
        r.rule_id.toLowerCase().includes(q) ||
        r.description.toLowerCase().includes(q) ||
        r.group.toLowerCase().includes(q)
      );
    });
  }, [rules, groupFilter, portabilityFilter, search]);

  const enabledCount = useMemo(() => {
    const enabledGroups = new Set(ablationConfig.enabled_groups ?? groups);
    const disabledIds = new Set(ablationConfig.disabled_rule_ids ?? []);
    return rules.filter(
      (r) => enabledGroups.has(r.group) && !disabledIds.has(r.rule_id)
    ).length;
  }, [rules, ablationConfig, groups]);

  const handleSimulate = useCallback(() => {
    runAblation.refetch();
  }, [runAblation]);

  const handleReset = useCallback(() => {
    setAblationConfig({});
  }, [setAblationConfig]);

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Header */}
      <div className="flex items-center justify-end border-b border-border bg-surface px-4 py-2 gap-3">
        <div className="flex items-center gap-1.5 rounded-md bg-surface-raised px-2 py-1 border border-border">
          <span className="text-[10px] text-muted">Active:</span>
          <span className="text-[11px] font-semibold text-deterministic">
            {enabledCount}
          </span>
          <span className="text-[10px] text-muted">/ {rules.length}</span>
        </div>
        <button
          onClick={handleReset}
          className="text-[11px] font-medium text-muted hover:text-foreground transition-colors"
        >
          Reset all
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <div className="flex h-full">
          {/* Left: Rule Inventory */}
          <div className="flex-1 overflow-y-auto p-5">
            <div className="mb-4 flex items-center gap-3">
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search rules by ID, description, or group…"
                  className="w-full rounded-lg border border-border bg-surface pl-8 pr-3 py-1.5 text-xs text-foreground placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-deterministic/30"
                />
              </div>
              <select
                value={groupFilter}
                onChange={(e) => setGroupFilter(e.target.value)}
                className="rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground focus:outline-none"
              >
                <option value="all">All groups</option>
                {groups.map((g) => (
                  <option key={g} value={g}>
                    {g.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
              <select
                value={portabilityFilter}
                onChange={(e) => setPortabilityFilter(e.target.value)}
                className="rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground focus:outline-none"
              >
                <option value="all">All portability</option>
                {portabilityLevels.map((p) => (
                  <option key={p} value={p}>
                    {p.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>

            <RuleInventory
              rules={filteredRules}
              ablationConfig={ablationConfig}
              onToggleGroup={toggleRuleGroup}
              onToggleRule={toggleRuleId}
            />
          </div>

          {/* Right: Simulation Panel */}
          <div className="w-[380px] border-l border-border bg-surface overflow-y-auto p-5">
            <SimulationPanel
              split={simSplit}
              limit={simLimit}
              onSplitChange={setSimSplit}
              onLimitChange={setSimLimit}
              onSimulate={handleSimulate}
              isSimulating={runAblation.isFetching}
              isCached={!runAblation.isFetching && runAblation.data !== undefined}
              result={runAblation.data ?? null}
              error={runAblation.error ? String(runAblation.error) : null}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function LaboratoryRoute() {
  const dataset = useActiveDataset();
  if (dataset === "exectv2") return <Exectv2ComponentImpact />;
  return <LaboratoryInner />;
}

export default function LaboratoryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading laboratory…</p>
          </div>
        </div>
      }
    >
      <LaboratoryRoute />
    </Suspense>
  );
}
