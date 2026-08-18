"use client";

import { Suspense } from "react";
import AssemblyLineWorkspace from "@/components/assembly-line/AssemblyLineWorkspace";
import { SurfaceLoading } from "@/components/surface";

export default function SchematicPage() {
  return (
    <Suspense fallback={<SurfaceLoading message="Loading assembly line." />}>
      <div className="h-full">
        <AssemblyLineWorkspace />
      </div>
    </Suspense>
  );
}
