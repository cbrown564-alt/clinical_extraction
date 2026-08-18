"use client";

import { Suspense } from "react";
import IsometricWorkspace from "@/components/isometric/IsometricWorkspace";

export default function SchematicPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full w-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-sm font-medium">Loading 2.5D Isometric Assembly Line...</p>
          </div>
        </div>
      }
    >
      <IsometricWorkspace />
    </Suspense>
  );
}
