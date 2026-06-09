"use client";

import { Suspense } from "react";
import ReportBuilder from "@/components/review/ReportBuilder";

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
      <ReportBuilder />
    </Suspense>
  );
}

