"use client";

import { Suspense } from "react";
import { useActiveDataset, getRuntimeAdapter } from "@/lib/datasets";

function ObservatoryRoute() {
  const dataset = useActiveDataset();
  const AggregatePerformance = getRuntimeAdapter(dataset).surfaces.AggregatePerformance;
  return <AggregatePerformance />;
}

export default function ObservatoryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading aggregate performance…</p>
          </div>
        </div>
      }
    >
      <ObservatoryRoute />
    </Suspense>
  );
}
