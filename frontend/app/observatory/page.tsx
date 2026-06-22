"use client";

import { Suspense } from "react";
import ReportBuilder from "@/components/review/ReportBuilder";
import { useActiveDataset } from "@/lib/datasets";
import Exectv2AggregatePerformance from "@/components/exectv2/Exectv2AggregatePerformance";

function ObservatoryRoute() {
  const dataset = useActiveDataset();
  if (dataset === "exectv2") return <Exectv2AggregatePerformance />;
  return <ReportBuilder />;
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
