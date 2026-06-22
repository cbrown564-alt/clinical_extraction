"use client";

import { formatMetricValue, metricTone, type MetricFormat } from "./atoms";

export interface MetricChip {
  label: string;
  value: number | null | undefined;
  format: MetricFormat;
  /** Shade the value by magnitude (good for F1/rate). */
  shade?: boolean;
  asPercent?: boolean;
}

/**
 * Headline metrics as compact chips for the header right slot.
 *
 * The denser, in-header counterpart to {@link MetricStrip}: where a surface
 * wants its overall/per-family numbers visible without spending a band of
 * vertical space in the body, it drops them here. ExECTv2's explorer carries
 * its run's Overall + family F1 this way, leaving the body for the specimen.
 */
export default function MetricChips({ chips }: { chips: MetricChip[] }) {
  return (
    <div className="flex flex-wrap items-center gap-1.5">
      {chips.map((chip) => (
        <div
          key={chip.label}
          className="flex items-center gap-1 rounded border border-border bg-surface-raised px-2 py-1"
        >
          <span className="text-[9px] uppercase tracking-wider text-muted">{chip.label}</span>
          <span
            className={`font-mono text-[11px] font-semibold ${
              chip.shade ? metricTone(chip.value) : "text-foreground"
            }`}
          >
            {formatMetricValue(chip.value, chip.format, { asPercent: chip.asPercent })}
          </span>
        </div>
      ))}
    </div>
  );
}
