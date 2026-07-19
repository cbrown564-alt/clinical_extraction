"use client";

import { Suspense } from "react";
import QualifiedReviewWorkspace from "@/components/qualified-review/QualifiedReviewWorkspace";

export default function QualifiedReviewPage() {
  return (
    <div className="h-full">
      <Suspense
        fallback={
          <div className="flex h-full items-center justify-center bg-background text-muted">
            Loading qualified review…
          </div>
        }
      >
        <QualifiedReviewWorkspace />
      </Suspense>
    </div>
  );
}
