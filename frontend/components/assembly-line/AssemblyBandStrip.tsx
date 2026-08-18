"use client";

import { ASSEMBLY_BANDS, type AssemblyBand } from "@/lib/assemblyLineTypes";
import { bandHasSteps } from "@/lib/assemblyLine";
import type { PredictedFactData } from "@/lib/assemblyLineTypes";

export default function AssemblyBandStrip({
  fact,
}: {
  fact: PredictedFactData | undefined;
}) {
  function jump(band: AssemblyBand) {
    const node = document.getElementById(`assembly-band-${band}`);
    node?.scrollIntoView({ block: "start", behavior: "smooth" });
  }

  return (
    <div
      className="flex items-center gap-1 px-5 pb-4"
      role="navigation"
      aria-label="Pipeline bands"
    >
      {ASSEMBLY_BANDS.map((band, index) => {
        const touched = bandHasSteps(fact, band.id);
        return (
          <div key={band.id} className="flex min-w-0 flex-1 items-center">
            {index > 0 ? <span className="h-px flex-1 bg-border" aria-hidden /> : null}
            <button
              type="button"
              disabled={!touched}
              onClick={() => jump(band.id)}
              className={`shrink-0 rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.12em] ${
                touched
                  ? "bg-surface-raised text-foreground hover:bg-deterministic/10 hover:text-deterministic"
                  : "text-muted/40"
              }`}
            >
              {band.label}
            </button>
          </div>
        );
      })}
    </div>
  );
}
