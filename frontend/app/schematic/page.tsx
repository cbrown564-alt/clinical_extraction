"use client";

import { Suspense } from "react";
import IsometricWorkspace from "@/components/isometric/IsometricWorkspace";

export default function SchematicPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full w-full items-center justify-center bg-white text-neutral-600">
          <p className="text-sm">Loading pipeline map.</p>
        </div>
      }
    >
      <div className="h-full">
        <IsometricWorkspace />
      </div>
    </Suspense>
  );
}
