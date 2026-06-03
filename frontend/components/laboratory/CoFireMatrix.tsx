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

  const cellSize = 48;
  const padding = 120;
  const size = groups.length * cellSize + padding;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <Info className="h-3.5 w-3.5 text-muted" />
        <p className="text-[11px] text-muted">
          This matrix shows rule-group relationships by shared portability levels.
          Darker cells indicate more shared portability classes between groups.
        </p>
      </div>

      <div className="overflow-auto">
        <svg width={size} height={size} className="block">
          {/* Row labels */}
          {groups.map((g, i) => (
            <text
              key={`row-${g}`}
              x={padding - 8}
              y={padding + i * cellSize + cellSize / 2 + 4}
              textAnchor="end"
              className="text-[10px] font-medium"
              fill={getGroupColor(g)}
            >
              {g.replace(/_/g, " ")}
            </text>
          ))}

          {/* Column labels */}
          {groups.map((g, i) => (
            <text
              key={`col-${g}`}
              x={padding + i * cellSize + cellSize / 2}
              y={padding - 8}
              textAnchor="middle"
              className="text-[10px] font-medium"
              fill={getGroupColor(g)}
            >
              {g.replace(/_/g, " ")}
            </text>
          ))}

          {/* Cells */}
          {matrix.map((cell, idx) => {
            const i = groups.indexOf(cell.groupA);
            const j = groups.indexOf(cell.groupB);
            const maxShared = 4; // approximate max portability levels
            const intensity = Math.min(cell.sharedPortability / maxShared, 1);
            const fillColor =
              i === j
                ? cell.colorA
                : `rgba(42, 111, 111, ${0.05 + intensity * 0.35})`;

            return (
              <g key={idx}>
                <rect
                  x={padding + j * cellSize + 1}
                  y={padding + i * cellSize + 1}
                  width={cellSize - 2}
                  height={cellSize - 2}
                  rx={4}
                  fill={fillColor}
                  stroke="rgba(0,0,0,0.04)"
                />
                {i === j && (
                  <text
                    x={padding + j * cellSize + cellSize / 2}
                    y={padding + i * cellSize + cellSize / 2 + 4}
                    textAnchor="middle"
                    className="text-[9px] font-semibold"
                    fill="white"
                  >
                    {cell.totalRulesA}
                  </text>
                )}
                {i !== j && cell.sharedPortability > 0 && (
                  <text
                    x={padding + j * cellSize + cellSize / 2}
                    y={padding + i * cellSize + cellSize / 2 + 3}
                    textAnchor="middle"
                    className="text-[9px] font-medium"
                    fill={`rgba(42, 111, 111, ${0.4 + intensity * 0.6})`}
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
      <div className="flex items-center gap-4 text-[10px] text-muted">
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 rounded bg-deterministic/20" />
          <span>Shared portability</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 rounded bg-deterministic" />
          <span>Diagonal = rule count</span>
        </div>
      </div>
    </div>
  );
}
