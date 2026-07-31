"use client";

import { Suspense } from "react";
import SfInspectionPanel from "@/components/exectv2/SfInspectionPanel";

export default function Exectv2SfInspectionPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">
              Loading SeizureFrequency inspection…
            </p>
          </div>
        </div>
      }
    >
      <SfInspectionPanel />
    </Suspense>
  );
}
