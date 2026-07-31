"use client";

import { Suspense } from "react";
import GoldNoisePanel from "@/components/observatory/GoldNoisePanel";

export default function GoldNoisePage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading gold noise evidence…</p>
          </div>
        </div>
      }
    >
      <GoldNoisePanel />
    </Suspense>
  );
}
