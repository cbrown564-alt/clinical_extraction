"use client";

import { getDataset } from "@/lib/datasets";
import type { DatasetId } from "@/lib/datasets/types";
import { SurfaceHeader, SurfaceLayout } from "@/components/surface";

export default function ComponentImpactUnavailable({
  datasetId,
}: {
  datasetId: DatasetId;
}) {
  const dataset = getDataset(datasetId);
  return (
    <SurfaceLayout
      variant="report"
      header={
        <SurfaceHeader
          surface="laboratory"
          dataset={dataset}
          description="Component-impact ladder is not available for this dataset on the supervisor path."
        />
      }
    >
      <section className="rounded-md border border-border bg-surface p-5">
        <h2 className="text-base font-semibold text-foreground">
          Component impact not available
        </h2>
        <p className="mt-2 max-w-[60ch] text-sm leading-relaxed text-muted">
          The ExECTv2 component-ablation ladder is retained in experiment reports only.
          A selected-method ladder will return here after the ExECT{" "}
          <span className="font-medium text-foreground">llm_with_rules</span> slice is
          ready for supervisor demonstration.
        </p>
      </section>
    </SurfaceLayout>
  );
}
