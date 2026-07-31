"use client";

import { Suspense } from "react";
import { useActiveDataset, getRuntimeAdapter } from "@/lib/datasets";

function LaboratoryRoute() {
  const dataset = useActiveDataset();
  const ComponentImpact = getRuntimeAdapter(dataset).surfaces.ComponentImpact;
  return <ComponentImpact />;
}

export default function LaboratoryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading component impact...</p>
          </div>
        </div>
      }
    >
      <LaboratoryRoute />
    </Suspense>
  );
}

