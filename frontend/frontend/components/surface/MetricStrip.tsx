"use client";

import { formatMetricValue, metricTone, type MetricFormat } from "./atoms";

export interface MetricTile {
  label: string;
  value: number | null | undefined;
  format: MetricFormat;
  /** Larger, leading tile (e.g. the headline metric). */
  emphasis?: boolean;
  /** Render rates as percentages. */
  asPercent?: boolean;
  /** Shade the value by magnitude (good for F1/rate). */
  shade?: boolean;
}

/**
 * A row of metric tiles, identical for both datasets. The caller maps whatever
 * its descriptor declares (headline / family / operational metrics) into tiles;
 * the strip just renders them, so Gan and ExECTv2 read as "the same strip with
 * different cells".
 */
export default function MetricStrip({ metrics }: { metrics: MetricTile[] }) {
  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 md:grid-cols-5">
      {metrics.map((m) => (
        <div key={m.label} className="rounded-md border border-border bg-surface px-3 py-2">
          <p className="truncate text-[11px] uppercase tracking-wider text-muted">
            {m.label}
          </p>
          <p
            className={`font-mono font-semibold ${m.emphasis ? "text-lg" : "text-base"} ${
              m.shade ? metricTone(m.value) : "text-foreground"
            }`}
          >
            {formatMetricValue(m.value, m.format, { asPercent: m.asPercent })}
          </p>
        </div>
      ))}
    </div>
  );
}
