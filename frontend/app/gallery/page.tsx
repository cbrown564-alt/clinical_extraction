"use client";

import { Suspense } from "react";
import { useActiveDataset, getRuntimeAdapter } from "@/lib/datasets";

function GalleryRoute() {
  const dataset = useActiveDataset();
  const ErrorGallery = getRuntimeAdapter(dataset).surfaces.ErrorGallery;
  return <ErrorGallery />;
}

export default function GalleryPage() {
  return (
    <Suspense
      fallback={
        <div className="flex h-full items-center justify-center bg-background text-muted">
          <div className="text-center">
            <p className="text-lg font-medium">Loading gallery…</p>
          </div>
        </div>
      }
    >
      <GalleryRoute />
    </Suspense>
  );
}
