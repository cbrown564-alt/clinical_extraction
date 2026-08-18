"use client";

import { useEffect } from "react";
import { useIsometricStore } from "@/lib/isometricStore";
import IsometricControls from "./IsometricControls";
import IsometricCanvas from "./IsometricCanvas";

export default function IsometricWorkspace() {
  const { loadData, isLoading, error } = useIsometricStore();

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (isLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-white text-neutral-600">
        <p className="text-sm">Loading teaching cases.</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-white text-neutral-900">
        <p className="text-sm">Failed to load teaching cases: {error}</p>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col overflow-hidden bg-white">
      <IsometricControls />
      <div className="flex min-h-0 flex-1 overflow-hidden">
        <IsometricCanvas />
      </div>
    </div>
  );
}
