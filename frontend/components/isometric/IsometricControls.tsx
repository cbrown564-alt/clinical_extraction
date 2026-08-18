"use client";

import React, { useEffect } from "react";
import {
  Play,
  Pause,
  RotateCcw,
  SkipForward,
  SkipBack,
  Sparkles,
  Layers,
  Cpu,
  Binary,
} from "lucide-react";
import {
  useIsometricStore,
  getActiveCase,
  getActiveRun,
  getActiveObservation,
  type MethodType,
} from "@/lib/isometricStore";

export default function IsometricControls() {
  const {
    cases,
    selectedCaseId,
    selectedMethod,
    currentStepIndex,
    isPlaying,
    playbackSpeed,
    expandedRack,
    setSelectedCaseId,
    setSelectedMethod,
    setCurrentStepIndex,
    togglePlay,
    setPlaybackSpeed,
    stepForward,
    stepBackward,
    resetPlayback,
    toggleExpandedRack,
  } = useIsometricStore();

  const activeCase = useIsometricStore(getActiveCase);
  const activeRun = useIsometricStore(getActiveRun);
  const activeObs = useIsometricStore(getActiveObservation);

  const totalSteps = activeRun?.observations.length ?? 1;

  // Free-running playback timer
  useEffect(() => {
    if (!isPlaying) return;
    const intervalMs = Math.max(800 / playbackSpeed, 250);
    const timer = setInterval(() => {
      stepForward();
    }, intervalMs);
    return () => clearInterval(timer);
  }, [isPlaying, playbackSpeed, stepForward]);

  // Keyboard navigation shortcuts
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.code === "Space") {
        e.preventDefault();
        togglePlay();
      } else if (e.code === "ArrowRight") {
        e.preventDefault();
        stepForward();
      } else if (e.code === "ArrowLeft") {
        e.preventDefault();
        stepBackward();
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [togglePlay, stepForward, stepBackward]);

  const methods: { id: MethodType; label: string; icon: React.ReactNode }[] = [
    { id: "rules", label: "Rules Only", icon: <Binary className="h-3.5 w-3.5" /> },
    { id: "llm", label: "LLM Only", icon: <Cpu className="h-3.5 w-3.5" /> },
    {
      id: "llm_with_rules",
      label: "LLM with Rules (Hybrid)",
      icon: <Sparkles className="h-3.5 w-3.5 text-amber-500" />,
    },
  ];

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-surface px-4 py-2 shadow-2xs">
      {/* Left: Case & Task Selector */}
      <div className="flex items-center gap-2.5 min-w-0">
        <span className="text-[11px] font-bold uppercase tracking-wider text-muted shrink-0">
          Letter Case:
        </span>
        <select
          value={selectedCaseId}
          onChange={(e) => setSelectedCaseId(e.target.value)}
          className="h-8 max-w-[320px] truncate rounded-md border border-border bg-surface-raised px-2.5 text-xs font-semibold text-foreground focus:outline-none focus:ring-1 focus:ring-primary shadow-2xs"
        >
          {cases.map((c) => (
            <option key={c.case_id} value={c.case_id}>
              [{c.task === "gan2026" ? "Gan 2026" : "ExECTv2"}] {c.letter_id}: {c.story.slice(0, 45)}...
            </option>
          ))}
        </select>

        <span className="hidden h-5 w-px bg-border sm:block" />

        {/* Method Toggle Buttons */}
        <div className="flex items-center rounded-lg border border-border bg-surface-raised p-0.5">
          {methods.map((m) => {
            const active = selectedMethod === m.id;
            return (
              <button
                key={m.id}
                onClick={() => setSelectedMethod(m.id)}
                className={`flex items-center gap-1.5 rounded-md px-2.5 py-1 text-xs font-semibold transition-all ${
                  active
                    ? "bg-surface text-foreground shadow-2xs ring-1 ring-border"
                    : "text-muted hover:text-foreground"
                }`}
              >
                {m.icon}
                <span>{m.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Center / Right: Interactive Playback Scrubber & Controls */}
      <div className="flex items-center gap-3">
        {/* Play / Step Buttons */}
        <div className="flex items-center gap-1">
          <button
            onClick={resetPlayback}
            title="Reset to start"
            className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface-raised text-muted transition-colors hover:text-foreground hover:bg-surface shadow-2xs"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
          <button
            onClick={stepBackward}
            disabled={currentStepIndex === 0}
            title="Step backward (Left Arrow)"
            className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface-raised text-muted transition-colors hover:text-foreground hover:bg-surface disabled:opacity-35 shadow-2xs"
          >
            <SkipBack className="h-4 w-4" />
          </button>
          <button
            onClick={togglePlay}
            title="Play / Pause (Spacebar)"
            className={`flex h-8 items-center gap-1.5 rounded-md px-3.5 text-xs font-bold text-white transition-all shadow-xs ${
              isPlaying
                ? "bg-amber-600 hover:bg-amber-500"
                : "bg-emerald-600 hover:bg-emerald-500"
            }`}
          >
            {isPlaying ? (
              <>
                <Pause className="h-3.5 w-3.5" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Play Flow</span>
              </>
            )}
          </button>
          <button
            onClick={stepForward}
            disabled={currentStepIndex >= totalSteps - 1}
            title="Step forward (Right Arrow)"
            className="flex h-8 w-8 items-center justify-center rounded-md border border-border bg-surface-raised text-muted transition-colors hover:text-foreground hover:bg-surface disabled:opacity-35 shadow-2xs"
          >
            <SkipForward className="h-4 w-4" />
          </button>
        </div>

        {/* Speed Controls */}
        <div className="flex items-center rounded-md border border-border bg-surface-raised p-0.5 text-[11px]">
          {[0.5, 1, 2].map((speed) => (
            <button
              key={speed}
              onClick={() => setPlaybackSpeed(speed)}
              className={`rounded px-2 py-0.5 font-mono ${
                playbackSpeed === speed
                  ? "bg-surface font-bold text-foreground shadow-2xs ring-1 ring-border/50"
                  : "text-muted hover:text-foreground"
              }`}
            >
              {speed}x
            </button>
          ))}
        </div>

        {/* Step Indicator & Scrubber */}
        <div className="flex items-center gap-2 rounded-md border border-border bg-surface-raised px-2.5 py-1">
          <input
            type="range"
            min={0}
            max={Math.max(totalSteps - 1, 0)}
            value={currentStepIndex}
            onChange={(e) => setCurrentStepIndex(Number(e.target.value))}
            className="h-1.5 w-24 cursor-pointer accent-emerald-600"
          />
          <span className="font-mono text-xs font-bold text-foreground">
            {currentStepIndex + 1}/{totalSteps}
          </span>
        </div>

        {/* Gan 10-Family Expand Rack Toggle */}
        {activeCase?.task === "gan2026" && (
          <button
            onClick={toggleExpandedRack}
            title="Toggle 10-Family Repair Bay Expansion"
            className={`flex h-8 items-center gap-1.5 rounded-md border px-2.5 text-xs font-bold transition-all shadow-2xs ${
              expandedRack
                ? "bg-amber-500/15 border-amber-500/40 text-amber-500 ring-1 ring-amber-500/30"
                : "border-border bg-surface-raised text-muted hover:text-foreground"
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">10-Slot Rack</span>
          </button>
        )}
      </div>
    </div>
  );
}
