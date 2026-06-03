"use client";

import { useState, useMemo } from "react";
import { usePrompts } from "@/lib/hooks";
import { FileCode, Check, X, ArrowRight, AlertTriangle, BookOpen } from "lucide-react";

export default function PromptDiffViewer() {
  const promptsQuery = usePrompts();
  const prompts = useMemo(() => promptsQuery.data?.prompts ?? [], [promptsQuery.data?.prompts]);

  // Only modules with policies are meaningful for diff; but show all with indicators
  const enrichedPrompts = useMemo(() => {
    return prompts.map((p, i) => ({
      ...p,
      index: i,
      hasPolicies: p.policy_taxonomy.length > 0,
      policyCount: p.policy_taxonomy.length,
    }));
  }, [prompts]);

  const promptsWithPolicies = enrichedPrompts.filter((p) => p.hasPolicies);

  // Default to first two modules with policies
  const [leftIdx, setLeftIdx] = useState(() =>
    promptsWithPolicies.length > 0 ? promptsWithPolicies[0].index : 0
  );
  const [rightIdx, setRightIdx] = useState(() =>
    promptsWithPolicies.length > 1 ? promptsWithPolicies[1].index : 0
  );

  const left = prompts[leftIdx];
  const right = prompts[rightIdx];

  const diff = useMemo(() => {
    if (!left || !right) return null;

    const leftPolicies = new Map(left.policy_taxonomy.map((p) => [p.policy_id, p]));
    const rightPolicies = new Map(right.policy_taxonomy.map((p) => [p.policy_id, p]));
    const allIds = new Set([...leftPolicies.keys(), ...rightPolicies.keys()]);

    const rows: Array<{
      policy_id: string;
      left: (typeof left.policy_taxonomy)[0] | null;
      right: (typeof right.policy_taxonomy)[0] | null;
      status: "same" | "added" | "removed" | "changed";
    }> = [];

    for (const id of allIds) {
      const l = leftPolicies.get(id) ?? null;
      const r = rightPolicies.get(id) ?? null;
      let status: "same" | "added" | "removed" | "changed" = "same";
      if (!l) status = "added";
      else if (!r) status = "removed";
      else if (
        l.status !== r.status ||
        l.description !== r.description ||
        l.portability !== r.portability
      ) {
        status = "changed";
      }
      rows.push({ policy_id: id, left: l, right: r, status });
    }

    return rows.sort((a, b) => {
      const order = { removed: 0, changed: 1, added: 2, same: 3 };
      return order[a.status] - order[b.status];
    });
  }, [left, right]);

  if (promptsQuery.isLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading prompt registry…</p>
      </div>
    );
  }

  if (prompts.length < 2) {
    return (
      <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
        <FileCode className="h-8 w-8 text-muted/40 mb-3" />
        <p className="text-sm font-medium text-muted">Need at least 2 prompt variants</p>
      </div>
    );
  }

  const leftHasPolicies = left?.policy_taxonomy.length ?? 0 > 0;
  const rightHasPolicies = right?.policy_taxonomy.length ?? 0 > 0;
  const canDiff = leftHasPolicies && rightHasPolicies;

  return (
    <div className="space-y-5 max-w-[1000px]">
      {/* Module selector */}
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <label className="block text-[10px] font-semibold text-muted mb-1.5">
            Baseline module
          </label>
          <select
            value={leftIdx}
            onChange={(e) => setLeftIdx(Number(e.target.value))}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-deterministic/30"
          >
            {enrichedPrompts.map((p) => (
              <option key={p.index} value={p.index}>
                {p.prompt_version} {p.hasPolicies ? `(${p.policyCount} policies)` : "(no policies)"}
              </option>
            ))}
          </select>
        </div>
        <ArrowRight className="h-4 w-4 text-muted mt-5" />
        <div className="flex-1">
          <label className="block text-[10px] font-semibold text-muted mb-1.5">
            Compare module
          </label>
          <select
            value={rightIdx}
            onChange={(e) => setRightIdx(Number(e.target.value))}
            className="w-full rounded-lg border border-border bg-surface px-3 py-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-deterministic/30"
          >
            {enrichedPrompts.map((p) => (
              <option key={p.index} value={p.index}>
                {p.prompt_version} {p.hasPolicies ? `(${p.policyCount} policies)` : "(no policies)"}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Warnings for modules without policies */}
      {!canDiff && (
        <div className="rounded-xl border border-llm/20 bg-llm/5 px-4 py-3">
          <div className="flex items-start gap-2">
            <AlertTriangle className="h-4 w-4 text-llm shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="text-[11px] font-medium text-llm">Module lacks structured policy taxonomy</p>
              {!leftHasPolicies && (
                <p className="text-[11px] text-muted">
                  <span className="font-mono text-foreground">{left?.prompt_version}</span> does not define <code className="text-[10px] bg-surface-raised px-1 rounded">PROMPT_POLICY_TAXONOMY</code>. Only modules with explicit policy taxonomies can be compared.
                </p>
              )}
              {!rightHasPolicies && (
                <p className="text-[11px] text-muted">
                  <span className="font-mono text-foreground">{right?.prompt_version}</span> does not define <code className="text-[10px] bg-surface-raised px-1 rounded">PROMPT_POLICY_TAXONOMY</code>.
                </p>
              )}
              {promptsWithPolicies.length >= 2 && (
                <p className="text-[11px] text-muted">
                  Modules with policy data: {promptsWithPolicies.map((p) => p.prompt_version).join(", ")}.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Diff table */}
      {canDiff && diff && (
        <div className="rounded-xl border border-border bg-surface overflow-hidden">
          <div className="grid grid-cols-[1fr_auto_1fr] gap-0 border-b border-border bg-surface-raised/50 px-4 py-2.5">
            <div className="text-[10px] font-semibold uppercase tracking-wide text-muted">
              {left.prompt_version}
            </div>
            <div className="px-2" />
            <div className="text-[10px] font-semibold uppercase tracking-wide text-muted">
              {right.prompt_version}
            </div>
          </div>

          <div className="divide-y divide-border">
            {diff.map((row) => (
              <div
                key={row.policy_id}
                className={`grid grid-cols-[1fr_auto_1fr] gap-0 px-4 py-3 ${
                  row.status === "same"
                    ? ""
                    : row.status === "added"
                    ? "bg-success/5"
                    : row.status === "removed"
                    ? "bg-error/5"
                    : "bg-llm-alt/5"
                }`}
              >
                <div>
                  {row.left ? (
                    <PolicyCell policy={row.left} />
                  ) : (
                    <span className="text-[11px] text-muted italic">Not present</span>
                  )}
                </div>
                <div className="flex items-center justify-center px-3">
                  {row.status === "same" && (
                    <Check className="h-3.5 w-3.5 text-success" />
                  )}
                  {row.status === "removed" && (
                    <X className="h-3.5 w-3.5 text-error" />
                  )}
                  {row.status === "added" && (
                    <span className="rounded bg-success/10 px-1.5 py-0 text-[9px] font-semibold text-success">
                      NEW
                    </span>
                  )}
                  {row.status === "changed" && (
                    <span className="rounded bg-llm-alt/10 px-1.5 py-0 text-[9px] font-semibold text-llm">
                      CHG
                    </span>
                  )}
                </div>
                <div>
                  {row.right ? (
                    <PolicyCell policy={row.right} />
                  ) : (
                    <span className="text-[11px] text-muted italic">Not present</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state when modules have no policies */}
      {canDiff && diff && diff.length === 0 && (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-border bg-surface py-12 text-center">
          <BookOpen className="h-8 w-8 text-muted/40 mb-3" />
          <p className="text-sm font-medium text-muted">No policies to compare</p>
          <p className="text-[11px] text-muted mt-1">
            Both modules have empty policy taxonomies.
          </p>
        </div>
      )}
    </div>
  );
}

function PolicyCell({
  policy,
}: {
  policy: {
    policy_id: string;
    controlled_variable: string;
    portability: string;
    status: string;
    description: string;
  };
}) {
  return (
    <div className="space-y-1">
      <div className="flex items-center gap-1.5 flex-wrap">
        <span className="text-[10px] font-mono font-semibold text-foreground">
          {policy.policy_id}
        </span>
        <span
          className={`rounded px-1 py-0 text-[9px] font-medium uppercase ${
            policy.portability === "general"
              ? "bg-success/10 text-success"
              : policy.portability === "seizure_frequency"
              ? "bg-deterministic-alt/10 text-deterministic-alt"
              : "bg-llm/10 text-llm"
          }`}
        >
          {policy.portability}
        </span>
      </div>
      <p className="text-[11px] text-foreground leading-snug">{policy.description}</p>
      <span className="text-[9px] font-mono text-muted">{policy.controlled_variable}</span>
    </div>
  );
}
