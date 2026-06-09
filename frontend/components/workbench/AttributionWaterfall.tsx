"use client";

interface Props {
  pipelineFamily: string;
  hasRepairChanges: boolean;
}

export default function AttributionWaterfall({ pipelineFamily, hasRepairChanges }: Props) {
  // Determine dynamic segments based on pipelineFamily and repair changes
  const segments = (() => {
    const isDeterministic = pipelineFamily === "rules_only" || pipelineFamily.includes("deterministic");
    const isHybrid = pipelineFamily.includes("hybrid");

    if (isDeterministic) {
      if (hasRepairChanges) {
        return [
          { label: "deterministic extraction", value: 90, color: "bg-deterministic" },
          { label: "format repair", value: 10, color: "bg-error" },
        ];
      }
      return [{ label: "deterministic extraction", value: 100, color: "bg-deterministic" }];
    }

    if (isHybrid) {
      if (hasRepairChanges) {
        return [
          { label: "deterministic extraction", value: 70, color: "bg-deterministic" },
          { label: "llm adjudication", value: 20, color: "bg-hybrid" },
          { label: "format repair", value: 10, color: "bg-error" },
        ];
      }
      return [
        { label: "deterministic extraction", value: 80, color: "bg-deterministic" },
        { label: "llm adjudication", value: 20, color: "bg-hybrid" },
      ];
    }

    // LLM-only pipelines
    if (hasRepairChanges) {
      return [
        { label: "llm extraction", value: 90, color: "bg-llm" },
        { label: "format repair", value: 10, color: "bg-error" },
      ];
    }
    return [{ label: "llm extraction", value: 100, color: "bg-llm" }];
  })();

  return (
    <div>
      <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-muted">
        Attribution Waterfall
      </p>
      <div className="flex h-4 w-full overflow-hidden rounded-full border border-border/30 bg-surface-raised">
        {segments.map((s) => (
          <div
            key={s.label}
            className={`${s.color} flex items-center justify-center text-[9px] font-bold text-white transition-all`}
            style={{ width: `${s.value}%` }}
            title={`${s.label}: ${s.value}%`}
          >
            {s.value >= 20 ? s.label : ""}
          </div>
        ))}
      </div>
      <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1">
        {segments.map((s) => (
          <div key={s.label} className="flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${s.color}`} />
            <span className="text-[10px] text-muted capitalize">
              {s.label} {s.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
