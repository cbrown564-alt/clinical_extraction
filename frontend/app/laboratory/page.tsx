"use client";

import { Suspense } from "react";
import { useActiveDataset } from "@/lib/datasets";
import GanComponentImpact from "@/components/laboratory/GanComponentImpact";
import Exectv2ComponentImpact from "@/components/exectv2/Exectv2ComponentImpact";

function LaboratoryRoute() {
  const dataset = useActiveDataset();
  if (dataset === "exectv2") return <Exectv2ComponentImpact />;
  return <GanComponentImpact />;
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

