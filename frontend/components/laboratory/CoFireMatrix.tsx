"use client";

import { useMemo } from "react";
import { useRules } from "@/lib/hooks";
import { Info } from "lucide-react";

const GROUP_COLORS: Record<string, string> = {
  rate: "#4a6fa5",
  temporal: "#81b29a",
  diary: "#7c3aed",
  cluster: "#d97706",
  seizure_free: "#2a6f6f",
  benchmark_repair: "#9ca3af",
};

function getGroupColor(group: string): string {
  for (const [key, color] of Object.entries(GROUP_COLORS)) {
    if (group.includes(key)) return color;
  }
  return "#6b7280";
}

function shortenGroupName(group: string): string {
  return group
    .replace(/_/g, " ")
    .replace(/benchmark /i, "")
    .replace(/selection /i, "sel. ")
    .replace(/seizure[-_ ]?free/i, "sz-free")
    .replace(/portable /i, "")
    .replace(/rules?/i, "")
    .trim();
}

export default function CoFireMatrix() {
  const rulesQuery = useRules();
  const rules = useMemo(() => rulesQuery.data?.rules ?? [], [rulesQuery.data?.rules]);
  const groups = useMemo(() => rulesQuery.data?.groups ?? [], [rulesQuery.data?.groups]);

  const matrix = useMemo(() => {
    const groupRules = new Map<string, typeof rules>();
    for (const rule of rules) {
      const list = groupRules.get(rule.group) ?? [];
      list.push(rule);
      groupRules.set(rule.group, list);
    }

    const result: {
      groupA: string;
      groupB: string;
      sharedPortability: number;
      totalRulesA: number;
      totalRulesB: number;
      colorA: string;
      colorB: string;
    }[] = [];

    for (let i = 0; i < groups.length; i++) {
      for (let j = 0; j < groups.length; j++) {
        const a = groups[i];
        const b = groups[j];
        const rulesA = groupRules.get(a) ?? [];
        const rulesB = groupRules.get(b) ?? [];

        const portabilityA = new Set(rulesA.map((r) => r.portability));
        const portabilityB = new Set(rulesB.map((r) => r.portability));
        let shared = 0;
        for (const p of portabilityA) {
          if (portabilityB.has(p)) shared++;
        }

        result.push({
          groupA: a,
          groupB: b,
          sharedPortability: shared,
          totalRulesA: rulesA.length,
          totalRulesB: rulesB.length,
          colorA: getGroupColor(a),
          colorB: getGroupColor(b),
        });
      }
    }

    return result;
  }, [rules, groups]);

  if (rulesQuery.isLoading) {
    return (
      <div className="flex h-full items-center justify-center text-muted">
        <p className="text-sm font-medium">Loading rule metadata…</p>
      </div>
    );
  }

  const cellSize = 72;
  const labelPad = 180;
  const topPad = 140;
  const size = groups.length * cellSize + labelPad;
  const svgHeight = groups.length * cellSize + topPad;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Info className="h-3.5 w-3.5 text-muted shrink-0" />
        <p className="text-xs text-muted">
          This matrix shows rule-group relationships by shared portability levels.
          Darker cells indicate more shared portability classes between groups.
          Diagonal shows rule count per group.
        </p>
      </div>

      <div className="overflow-auto rounded-xl border border-border bg-surface">
        <svg width={size} height={svgHeight} className="block">
          {/* Row labels */}
          {groups.map((g, i) => (
            <g key={`row-${g}`}>
              <text
                x={labelPad - 12}
                y={topPad + i * cellSize + cellSize / 2 + 4}
                textAnchor="end"
                className="text-xs font-semibold"
                fill={getGroupColor(g)}
              >
                {shortenGroupName(g)}
              </text>
              {/* Color dot */}
              <circle
                cx={labelPad - 6}
                cy={topPad + i * cellSize + cellSize / 2}
                r={3}
                fill={getGroupColor(g)}
              />
            </g>
          ))}

          {/* Column labels – rotated -45° */}
          {groups.map((g, i) => (
            <g
              key={`col-${g}`}
              transform={`translate(${labelPad + i * cellSize + cellSize / 2}, ${topPad - 16}) rotate(-45)`}
            >
              <text
                x={0}
                y={0}
                textAnchor="start"
                className="text-xs font-semibold"
                fill={getGroupColor(g)}
              >
                {shortenGroupName(g)}
              </text>
            </g>
          ))}

          {/* Cells */}
          {matrix.map((cell, idx) => {
            const i = groups.indexOf(cell.groupA);
            const j = groups.indexOf(cell.groupB);
            const maxShared = 4;
            const intensity = Math.min(cell.sharedPortability / maxShared, 1);
            const fillColor =
              i === j
                ? cell.colorA
                : `rgba(42, 111, 111, ${0.04 + intensity * 0.28})`;

            return (
              <g key={idx}>
                <rect
                  x={labelPad + j * cellSize + 1}
                  y={topPad + i * cellSize + 1}
                  width={cellSize - 2}
                  height={cellSize - 2}
                  rx={6}
                  fill={fillColor}
                  stroke="rgba(0,0,0,0.04)"
                />
                {i === j && (
                  <text
                    x={labelPad + j * cellSize + cellSize / 2}
                    y={topPad + i * cellSize + cellSize / 2 + 5}
                    textAnchor="middle"
                    className="text-xs font-bold"
                    fill="white"
                  >
                    {cell.totalRulesA}
                  </text>
                )}
                {i !== j && cell.sharedPortability > 0 && (
                  <text
                    x={labelPad + j * cellSize + cellSize / 2}
                    y={topPad + i * cellSize + cellSize / 2 + 4}
                    textAnchor="middle"
                    className="text-xs font-semibold"
                    fill={`rgba(42, 111, 111, ${0.5 + intensity * 0.5})`}
                  >
                    {cell.sharedPortability}
                  </text>
                )}
              </g>
            );
          })}
        </svg>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-6 text-[11px] text-muted">
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 rounded bg-deterministic/20" />
          <span>Shared portability levels</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 rounded bg-deterministic" />
          <span>Diagonal = rule count</span>
        </div>
      </div>
    </div>
  );
}
