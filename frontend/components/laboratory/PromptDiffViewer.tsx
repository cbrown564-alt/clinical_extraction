"use client";

import { useState, useMemo } from "react";
import { usePrompts } from "@/lib/hooks";
import { FileCode, Check, X, ArrowRight } from "lucide-react";

export default function PromptDiffViewer() {
  const promptsQuery = usePrompts();
  const prompts = promptsQuery.data?.prompts ?? [];
  const [leftIdx, setLeftIdx] = useState(0);
  const [rightIdx, setRightIdx] = useState(1);

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
        <p className="text-[11px] text-muted mt-1 max-w-md">
          Only {prompts.length} prompt module{prompts.length === 1 ? "" : "s"} registered in the backend.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-w-[900px]">
      <div className="flex items-center gap-3">
        <div className="flex-1">
          <label className="block text-[10px] font-medium text-muted mb-1">Baseline</label>
          <select
            value={leftIdx}
            onChange={(e) => setLeftIdx(Number(e.target.value))}
            className="w-full rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground focus:outline-none"
          >
            {prompts.map((p, i) => (
              <option key={i} value={i}>
                {p.prompt_version}
              </option>
            ))}
          </select>
        </div>
        <ArrowRight className="h-4 w-4 text-muted mt-5" />
        <div className="flex-1">
          <label className="block text-[10px] font-medium text-muted mb-1">Compare</label>
          <select
            value={rightIdx}
            onChange={(e) => setRightIdx(Number(e.target.value))}
            className="w-full rounded-lg border border-border bg-surface px-2.5 py-1.5 text-xs text-foreground focus:outline-none"
          >
            {prompts.map((p, i) => (
              <option key={i} value={i}>
                {p.prompt_version}
              </option>
            ))}
          </select>
        </div>
      </div>

      {diff && (
        <div className="rounded-xl border border-border bg-surface overflow-hidden">
          <div className="grid grid-cols-[1fr_auto_1fr] gap-0 border-b border-border bg-surface-raised/50">
            <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wide text-muted">
              {left.prompt_version}
            </div>
            <div className="px-2 py-2 text-center" />
            <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wide text-muted">
              {right.prompt_version}
            </div>
          </div>

          <div className="divide-y divide-border">
            {diff.map((row) => (
              <div
                key={row.policy_id}
                className={`grid grid-cols-[1fr_auto_1fr] gap-0 ${
                  row.status === "same"
                    ? ""
                    : row.status === "added"
                    ? "bg-success/5"
                    : row.status === "removed"
                    ? "bg-error/5"
                    : "bg-llm-alt/5"
                }`}
              >
                <div className="px-3 py-2.5">
                  {row.left ? (
                    <PolicyCell policy={row.left} />
                  ) : (
                    <span className="text-[11px] text-muted italic">Not present</span>
                  )}
                </div>
                <div className="flex items-center justify-center px-2">
                  {row.status === "same" && (
                    <Check className="h-3 w-3 text-success" />
                  )}
                  {row.status === "removed" && (
                    <X className="h-3 w-3 text-error" />
                  )}
                  {row.status === "added" && (
                    <span className="rounded bg-success/10 px-1 py-0 text-[9px] font-medium text-success">
                      NEW
                    </span>
                  )}
                  {row.status === "changed" && (
                    <span className="rounded bg-llm-alt/10 px-1 py-0 text-[9px] font-medium text-llm">
                      CHG
                    </span>
                  )}
                </div>
                <div className="px-3 py-2.5">
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
      <div className="flex items-center gap-1.5">
        <span className="text-[10px] font-mono font-medium text-foreground">
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
