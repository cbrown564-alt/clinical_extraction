"use client";

import { Suspense } from "react";
import ReliabilityScorecardSurface from "@/components/reliability/ReliabilityScorecardSurface";

export default function ReliabilityScorecardPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading reliability scorecard...</p>
          </div>
        </div>
      }
    >
      <ReliabilityScorecardSurface />
    </Suspense>
  );
}

