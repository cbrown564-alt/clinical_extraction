"use client";

import { useMemo } from "react";
import { Play, Loader2, AlertCircle, CheckCircle, XCircle, Zap, BarChart3, Layers, RotateCcw } from "lucide-react";
import type { RunAblationResponse } from "@/lib/types";
import { useLaboratoryStore } from "@/lib/stores";

interface SimulationPanelProps {
  split: string;
  limit: string;
  onSplitChange: (split: string) => void;
  onLimitChange: (limit: string) => void;
  onSimulate: () => void;
  isSimulating: boolean;
  isCached: boolean;
  result: RunAblationResponse | null;
  error: string | null;
}

export default function SimulationPanel({
  split,
  limit,
  onSplitChange,
  onLimitChange,
  onSimulate,
  isSimulating,
  isCached,
  result,
  error,
}: SimulationPanelProps) {
  const { ablationConfig } = useLaboratoryStore();

  const configSummary = useMemo(() => {
    const enabledGroups = ablationConfig.enabled_groups;
    const disabledRules = ablationConfig.disabled_rule_ids;
    return {
      hasCustomConfig: !!enabledGroups || !!disabledRules,
      groupCount: enabledGroups?.length,
      disabledCount: disabledRules?.length,
    };
  }, [ablationConfig]);

  return (
    <div className="space-y-6">
      {/* Configuration Preview */}
      <div className="rounded-xl border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-3">
          <Layers className="h-3.5 w-3.5 text-deterministic-alt" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">
            Current Configuration
          </h3>
        </div>
        <div className="space-y-2">
          {!configSummary.hasCustomConfig ? (
            <div className="flex items-center gap-2 text-xs text-muted">
              <CheckCircle className="h-3.5 w-3.5 text-success shrink-0" />
              All rules active (default configuration)
            </div>
          ) : (
            <>
              {configSummary.groupCount !== undefined && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-deterministic shrink-0" />
                  <span className="text-muted">Active groups:</span>
                  <span className="font-mono text-foreground">{configSummary.groupCount}</span>
                </div>
              )}
              {configSummary.disabledCount !== undefined && configSummary.disabledCount > 0 && (
                <div className="flex items-center gap-2 text-xs">
                  <span className="w-1.5 h-1.5 rounded-full bg-error shrink-0" />
                  <span className="text-muted">Disabled rules:</span>
                  <span className="font-mono text-error">{configSummary.disabledCount}</span>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Run Controls */}
      <div className="rounded-xl border border-border bg-surface p-4">
        <div className="flex items-center gap-2 mb-4">
          <Zap className="h-3.5 w-3.5 text-llm" />
          <h3 className="text-xs font-semibold uppercase tracking-wide text-muted">
            Run Simulation
          </h3>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-[11px] font-semibold text-foreground mb-1.5">
              Dataset split
            </label>
            <select
              value={split}
              onChange={(e) => onSplitChange(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-deterministic/30"
            >
              <option value="validation">validation</option>
              <option value="validation25">validation25</option>
              <option value="validation50">validation50</option>
              <option value="validation250">validation250</option>
              <option value="test">test (locked)</option>
            </select>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-foreground mb-1.5">
              Row limit <span className="text-muted font-normal">(optional)</span>
            </label>
            <input
              type="number"
              value={limit}
              onChange={(e) => onLimitChange(e.target.value)}
              placeholder="All rows"
              min={1}
              className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-deterministic/30"
            />
          </div>

          <button
            onClick={onSimulate}
            disabled={isSimulating}
            className="mt-2 flex w-full items-center justify-center gap-2 rounded-lg bg-deterministic px-4 py-2.5 text-sm font-semibold text-surface shadow-sm transition-colors hover:bg-deterministic/90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isSimulating ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Running against {split}…
              </>
            ) : isCached ? (
              <>
                <RotateCcw className="h-4 w-4" />
                Re-run simulation
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run simulation
              </>
            )}
          </button>

          {isCached && !isSimulating && (
            <div className="flex items-center gap-1.5 text-[11px] text-success">
              <CheckCircle className="h-3 w-3" />
              Result cached – same config will load instantly
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-error/20 bg-error/5 px-4 py-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-error shrink-0 mt-0.5" />
            <div className="text-xs text-error leading-relaxed">{error}</div>
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-3.5 w-3.5 text-success" />
            <span className="text-xs font-semibold uppercase tracking-wide text-muted">
              Results
            </span>
            <span className="ml-auto text-[11px] text-muted">
              {result.row_count} rows · {result.split}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <ScoreCard
              label="Strict"
              accuracy={result.summary.purist.accuracy}
              f1={result.summary.purist.f1}
              color="deterministic"
            />
            <ScoreCard
              label="Lenient"
              accuracy={result.summary.pragmatic.accuracy}
              f1={result.summary.pragmatic.f1}
              color="success"
            />
          </div>

          <div className="rounded-xl border border-border bg-surface p-4">
            <h4 className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-3">
              Per-label F1
            </h4>
            <div className="space-y-1.5 max-h-[220px] overflow-y-auto">
              {Object.entries(result.summary.purist.per_label)
                .filter(([, m]) => m.support > 0)
                .sort((a, b) => b[1].support - a[1].support)
                .map(([label, metrics]) => (
                  <div key={label} className="flex items-center gap-2">
                    <div className="w-16 text-[11px] font-mono text-foreground truncate">
                      {label.replace("seizure_freq_", "")}
                    </div>
                    <div className="flex-1 h-1.5 rounded-full bg-surface-raised overflow-hidden">
                      <div
                        className="h-full rounded-full bg-deterministic/60"
                        style={{ width: `${Math.max(metrics.f1 * 100, 2)}%` }}
                      />
                    </div>
                    <span className="text-[11px] text-muted w-8 text-right">
                      n={metrics.support}
                    </span>
                    <span
                      className={`text-[11px] font-mono font-medium w-8 text-right ${
                        metrics.f1 >= 0.8
                          ? "text-success"
                          : metrics.f1 >= 0.5
                          ? "text-llm"
                          : "text-error"
                      }`}
                    >
                      {metrics.f1.toFixed(2)}
                    </span>
                  </div>
                ))}
            </div>
          </div>

          <ErrorFamilyShifts rows={result.rows} />
        </div>
      )}
    </div>
  );
}

function ScoreCard({
  label,
  accuracy,
  f1,
  color,
}: {
  label: string;
  accuracy: number;
  f1: number;
  color: "deterministic" | "success";
}) {
  const colorClass =
    color === "deterministic" ? "text-deterministic" : "text-success";
  const barColor =
    color === "deterministic" ? "bg-deterministic/20" : "bg-success/20";

  return (
    <div className="rounded-xl border border-border bg-surface p-3">
      <div className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-1">
        {label}
      </div>
      <div className={`text-xl font-bold ${colorClass}`}>
        {(accuracy * 100).toFixed(1)}%
      </div>
      <div className="mt-1.5 flex items-center gap-2">
        <div className={`flex-1 h-1 rounded-full ${barColor}`}>
          <div
            className={`h-full rounded-full ${colorClass.replace("text-", "bg-")}`}
            style={{ width: `${Math.max(f1 * 100, 2)}%` }}
          />
        </div>
        <span className="text-[11px] text-muted">F1 {(f1 * 100).toFixed(0)}%</span>
      </div>
    </div>
  );
}

function ErrorFamilyShifts({
  rows,
}: {
  rows: Array<{
    purist_predicted_category: string;
    purist_gold_category: string;
    pragmatic_predicted_category: string;
    pragmatic_gold_category: string;
  }>;
}) {
  const errors = rows.filter(
    (r) => r.purist_predicted_category !== r.purist_gold_category
  );

  if (errors.length === 0) {
    return (
      <div className="rounded-xl border border-success/20 bg-success/5 px-4 py-3">
        <div className="flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-success" />
          <span className="text-xs text-success font-medium">Zero errors – all rows correct</span>
        </div>
      </div>
    );
  }

  const transitions = new Map<string, number>();
  for (const row of errors) {
    const key = `${row.purist_gold_category} → ${row.purist_predicted_category}`;
    transitions.set(key, (transitions.get(key) ?? 0) + 1);
  }

  const sortedTransitions = Array.from(transitions.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  const maxCount = sortedTransitions[0]?.[1] ?? 1;

  return (
    <div className="rounded-xl border border-border bg-surface p-4">
      <h4 className="text-[11px] font-semibold uppercase tracking-wide text-muted mb-3">
        Top Error Transitions ({errors.length} errors)
      </h4>
      <div className="space-y-2">
        {sortedTransitions.map(([transition, count]) => {
          const [from, to] = transition.split(" → ");
          return (
            <div key={transition} className="flex items-center gap-2">
              <XCircle className="h-3.5 w-3.5 text-error shrink-0" />
              <span className="text-[11px] font-mono text-muted w-24 truncate">{from.replace("seizure_freq_", "")}</span>
              <span className="text-[11px] text-border">→</span>
              <span className="text-[11px] font-mono text-foreground w-24 truncate">{to.replace("seizure_freq_", "")}</span>
              <div className="flex-1 h-1.5 rounded-full bg-surface-raised overflow-hidden">
                <div
                  className="h-full rounded-full bg-error/60"
                  style={{ width: `${Math.max((count / maxCount) * 100, 3)}%` }}
                />
              </div>
              <span className="text-[11px] font-mono text-muted w-5 text-right">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
