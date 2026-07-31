"use client";

import { Suspense } from "react";
import GoldAuditPanel from "@/components/observatory/GoldAuditPanel";

export default function GoldAuditPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading gold audit queue…</p>
          </div>
        </div>
      }
    >
      <GoldAuditPanel />
    </Suspense>
  );
}
