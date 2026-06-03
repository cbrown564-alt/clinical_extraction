"use client";

import { useState } from "react";
import { Play, Loader2, AlertCircle, CheckCircle, XCircle } from "lucide-react";
import type { RunAblationResponse } from "@/lib/types";

interface SimulationPanelProps {
  onSimulate: (split: string, limit?: number) => void;
  isSimulating: boolean;
  result: RunAblationResponse | null;
  error: string | null;
}

export default function SimulationPanel({
  onSimulate,
  isSimulating,
  result,
  error,
}: SimulationPanelProps) {
  const [split, setSplit] = useState("validation");
  const [limit, setLimit] = useState<string>("");

  const handleRun = () => {
    const n = limit.trim() ? parseInt(limit, 10) : undefined;
    onSimulate(split, n);
  };

  return (
    <div className="space-y-5">
      <div>
        <h3 className="text-xs font-semibold uppercase tracking-wide text-muted mb-3">
          Live Ablation Simulation
        </h3>
        <div className="space-y-3">
          <div>
            <label className="block text-[10px] font-medium text-muted mb-1">Split</label>
            <select
              value={split}
              onChange={(e) => setSplit(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground focus:outline-none"
            >
              <option value="validation">validation</option>
              <option value="validation25">validation25</option>
              <option value="validation50">validation50</option>
              <option value="validation250">validation250</option>
              <option value="test">test (locked)</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] font-medium text-muted mb-1">
              Limit (optional)
            </label>
            <input
              type="number"
              value={limit}
              onChange={(e) => setLimit(e.target.value)}
              placeholder="e.g. 50"
              min={1}
              className="w-full rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground placeholder:text-muted focus:outline-none focus:ring-1 focus:ring-deterministic/30"
            />
          </div>

          <button
            onClick={handleRun}
            disabled={isSimulating}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-deterministic px-3 py-2 text-xs font-semibold text-white shadow-sm hover:bg-deterministic/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isSimulating ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Running…
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5" />
                Simulate against {split}
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-error/20 bg-error/5 px-3 py-2.5">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-3.5 w-3.5 text-error shrink-0 mt-0.5" />
            <div className="text-[11px] text-error">{error}</div>
          </div>
        </div>
      )}

      {result && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <CheckCircle className="h-3.5 w-3.5 text-success" />
            <span className="text-[11px] font-semibold text-foreground">
              Simulation complete
            </span>
            <span className="text-[10px] text-muted ml-auto">
              {result.row_count} rows
            </span>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <ScoreCard
              label="Purist Accuracy"
              value={result.summary.purist.accuracy}
              f1={result.summary.purist.f1}
            />
            <ScoreCard
              label="Pragmatic Accuracy"
              value={result.summary.pragmatic.accuracy}
              f1={result.summary.pragmatic.f1}
            />
          </div>

          <div className="rounded-lg border border-border bg-surface p-3">
            <h4 className="text-[10px] font-semibold uppercase tracking-wide text-muted mb-2">
              Per-label F1
            </h4>
            <div className="space-y-1 max-h-[200px] overflow-y-auto">
              {Object.entries(result.summary.purist.per_label)
                .sort((a, b) => b[1].support - a[1].support)
                .map(([label, metrics]) => (
                  <div key={label} className="flex items-center gap-2">
                    <span className="w-1 h-1 rounded-full bg-muted shrink-0" />
                    <span className="flex-1 text-[10px] font-mono text-foreground truncate">
                      {label}
                    </span>
                    <span className="text-[10px] text-muted">n={metrics.support}</span>
                    <span
                      className={`text-[10px] font-mono font-medium ${
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

          {/* Error family shifts (approximated from row transitions) */}
          <ErrorFamilyShifts rows={result.rows} />
        </div>
      )}
    </div>
  );
}

function ScoreCard({
  label,
  value,
  f1,
}: {
  label: string;
  value: number;
  f1: number;
}) {
  return (
    <div className="rounded-lg border border-border bg-surface p-2.5">
      <div className="text-[9px] font-medium uppercase tracking-wide text-muted">{label}</div>
      <div className="mt-1 text-lg font-semibold text-foreground">{(value * 100).toFixed(1)}%</div>
      <div className="text-[10px] text-muted">F1 {(f1 * 100).toFixed(1)}%</div>
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
      <div className="rounded-lg border border-success/20 bg-success/5 px-3 py-2.5">
        <div className="flex items-center gap-2">
          <CheckCircle className="h-3.5 w-3.5 text-success" />
          <span className="text-[11px] text-success font-medium">Zero errors — all rows correct</span>
        </div>
      </div>
    );
  }

  // Categorise transitions
  const transitions = new Map<string, number>();
  for (const row of errors) {
    const key = `${row.purist_gold_category} → ${row.purist_predicted_category}`;
    transitions.set(key, (transitions.get(key) ?? 0) + 1);
  }

  const sortedTransitions = Array.from(transitions.entries()).sort((a, b) => b[1] - a[1]).slice(0, 8);

  return (
    <div className="rounded-lg border border-border bg-surface p-3">
      <h4 className="text-[10px] font-semibold uppercase tracking-wide text-muted mb-2">
        Top Error Transitions ({errors.length} errors)
      </h4>
      <div className="space-y-1">
        {sortedTransitions.map(([transition, count]) => {
          const [from, to] = transition.split(" → ");
          return (
            <div key={transition} className="flex items-center gap-2 text-[10px]">
              <XCircle className="h-3 w-3 text-error shrink-0" />
              <span className="text-muted truncate">{from}</span>
              <span className="text-border">→</span>
              <span className="text-foreground truncate">{to}</span>
              <span className="ml-auto font-mono text-muted">{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
