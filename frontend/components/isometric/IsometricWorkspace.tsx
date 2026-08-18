"use client";

import React, { useEffect } from "react";
import { useIsometricStore } from "@/lib/isometricStore";
import IsometricControls from "./IsometricControls";
import IsometricCanvas from "./IsometricCanvas";
import IsometricInspector from "./IsometricInspector";

export default function IsometricWorkspace() {
  const { loadData, isLoading, error } = useIsometricStore();

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (isLoading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-background text-muted">
        <div className="flex flex-col items-center gap-2">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-emerald-500 border-t-transparent" />
          <p className="text-xs font-medium">Loading assembly line architecture...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-background text-rose-400">
        <p className="text-xs font-semibold">Failed to load teaching cases: {error}</p>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col overflow-hidden bg-background">
      {/* Top Playback & Configuration Controls */}
      <IsometricControls />

      {/* Main Workspace Layout: Full Canvas with Contextual Popovers & Letterhead */}
      <div className="flex flex-1 min-h-0 w-full overflow-hidden">
        <IsometricCanvas />
      </div>
    </div>
  );
}
