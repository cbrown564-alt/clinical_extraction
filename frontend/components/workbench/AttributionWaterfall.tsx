"use client";

import type { PipelineDiagnostics } from "@/lib/types";

interface Props {
  diagnostics?: PipelineDiagnostics;
}

export default function AttributionWaterfall({ diagnostics }: Props) {
  // For Phase 1 with deterministic V1, attribution is 100% deterministic_extraction.
  // As hybrid/LLM pipelines are added, this should be driven by diagnostics.
  const segments = [
    { label: "deterministic_extraction", value: 100, color: "bg-deterministic" },
  ];

  if (!diagnostics) {
    return (
      <div className="text-xs text-muted">Run a pipeline to see attribution.</div>
    );
  }

  return (
    <div>
      <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-muted">
        Attribution
      </p>
      <div className="flex h-4 w-full overflow-hidden rounded-full">
        {segments.map((s) => (
          <div
            key={s.label}
            className={`${s.color} flex items-center justify-center text-[9px] font-bold text-white`}
            style={{ width: `${s.value}%` }}
            title={`${s.label}: ${s.value}%`}
          >
            {s.value >= 20 ? s.label.replace(/_/g, " ") : ""}
          </div>
        ))}
      </div>
      <div className="mt-1 flex flex-wrap gap-2">
        {segments.map((s) => (
          <div key={s.label} className="flex items-center gap-1">
            <span className={`h-2 w-2 rounded-full ${s.color}`} />
            <span className="text-[10px] text-muted">
              {s.label.replace(/_/g, " ")} {s.value}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
