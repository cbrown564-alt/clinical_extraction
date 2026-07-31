"use client";

import { Suspense } from "react";
import { useActiveDataset, getRuntimeAdapter } from "@/lib/datasets";

function WorkbenchRoute() {
  const dataset = useActiveDataset();
  const ExampleExplorer = getRuntimeAdapter(dataset).surfaces.ExampleExplorer;
  return <ExampleExplorer />;
}

export default function WorkbenchPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading example explorer…</p>
          </div>
        </div>
      }
    >
      <WorkbenchRoute />
    </Suspense>
  );
}
