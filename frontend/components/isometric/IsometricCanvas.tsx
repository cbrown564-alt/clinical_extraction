"use client";

import { useMemo } from "react";
import {
  useIsometricStore,
  getActiveCase,
  getActiveRun,
} from "@/lib/isometricStore";
import {
  GAN_STATIONS,
  EXECT_STATIONS,
  CANVAS_WIDTH,
  CANVAS_HEIGHT,
  layoutStationPoints,
  observationsForStation,
  stationActivation,
  activationLabel,
  ACCENT,
  sourceLetterLine,
  clipLine,
} from "@/lib/isometricLayout";
import type { StationActivation } from "@/lib/isometricTypes";
import StagePanel from "./StagePanel";

function nameClass(activation: StationActivation): string {
  if (activation === "skipped") return "text-sm font-normal text-neutral-400";
  if (activation === "idle") return "text-sm font-normal text-neutral-700";
  return "text-base font-semibold text-neutral-900";
}

function statusClass(activation: StationActivation): string {
  if (activation === "on") return "text-xs font-medium";
  return "text-xs font-normal text-neutral-500";
}

export default function IsometricCanvas() {
  const { selectedStageId, setSelectedStageId } = useIsometricStore();
  const activeCase = useIsometricStore(getActiveCase);
  const activeRun = useIsometricStore(getActiveRun);

  const isGan = activeCase?.task === "gan2026";
  const stations = isGan ? GAN_STATIONS : EXECT_STATIONS;
  const observations = activeRun?.observations ?? [];

  const placed = useMemo(() => {
    const points = layoutStationPoints(stations.length);
    return stations.map((station, index) => {
      const mapped = observationsForStation(observations, station.id, isGan);
      return {
        station,
        point: points[index],
        mapped,
        ...stationActivation(station, mapped),
      };
    });
  }, [stations, observations, isGan]);

  const selected = placed.find((item) => item.station.id === selectedStageId) ?? null;

  return (
    <div className="flex h-full min-h-0 w-full bg-white text-neutral-900">
      <div className="relative min-w-0 flex-1">
        <svg
          className="h-full w-full"
          viewBox={`0 0 ${CANVAS_WIDTH} ${CANVAS_HEIGHT}`}
          role="img"
          aria-label="Pipeline stages"
        >
          <rect width={CANVAS_WIDTH} height={CANVAS_HEIGHT} fill="#ffffff" />
          {placed.map((curr, index) => {
            const next = placed[index + 1];
            if (!next) return null;
            const midY = (curr.point.y + next.point.y) / 2;
            const path =
              curr.point.y === next.point.y
                ? `M ${curr.point.x} ${curr.point.y} L ${next.point.x} ${next.point.y}`
                : `M ${curr.point.x} ${curr.point.y} C ${curr.point.x} ${midY}, ${next.point.x} ${midY}, ${next.point.x} ${next.point.y}`;
            return (
              <path
                key={`${curr.station.id}-path`}
                d={path}
                fill="none"
                stroke={
                  curr.activation === "skipped" && next.activation === "skipped"
                    ? "#e5e5e5"
                    : "#a3a3a3"
                }
                strokeWidth="1"
              />
            );
          })}
        </svg>

        {placed.map(({ station, point, activation, onCount, catalogSize }) => {
          const selectedHere = selectedStageId === station.id;
          const left = `${(point.x / CANVAS_WIDTH) * 100}%`;
          const top = `${(point.y / CANVAS_HEIGHT) * 100}%`;
          return (
            <button
              key={station.id}
              type="button"
              onClick={() => setSelectedStageId(selectedHere ? null : station.id)}
              className={`absolute -translate-x-1/2 bg-white px-2 py-1.5 text-left ${
                station.kind === "source" || station.kind === "score" ? "w-52" : "w-32"
              }`}
              style={{
                left,
                top,
                boxShadow: selectedHere ? `inset 0 0 0 1px ${ACCENT}` : undefined,
              }}
            >
              <div className={nameClass(activation)}>{station.name}</div>
              <div
                className={statusClass(activation)}
                style={activation === "on" ? { color: ACCENT } : undefined}
              >
                {activationLabel(activation, onCount, catalogSize)}
              </div>
              {station.kind === "source" && activeCase && (
                <p className="mt-1 text-xs leading-snug text-neutral-600">
                  {sourceLetterLine(activeCase.note_text, activeCase.gold_reference)}
                </p>
              )}
              {station.kind === "score" && activation !== "skipped" && activeRun?.final_answer && (
                <p className="mt-1 text-xs leading-snug text-neutral-600">
                  {clipLine(activeRun.final_answer, 40)}
                  {activeRun.correct === true
                    ? " · matches gold"
                    : activeRun.correct === false
                      ? " · misses gold"
                      : ""}
                </p>
              )}
            </button>
          );
        })}
      </div>

      {selected && (
        <div className="hidden w-[380px] shrink-0 md:block">
          <StagePanel
            station={selected.station}
            observations={selected.mapped}
            activeCase={activeCase}
            activeRun={activeRun}
            onClose={() => setSelectedStageId(null)}
          />
        </div>
      )}

      {selected && (
        <div className="absolute inset-x-0 bottom-0 top-1/2 border-t border-neutral-200 md:hidden">
          <StagePanel
            station={selected.station}
            observations={selected.mapped}
            activeCase={activeCase}
            activeRun={activeRun}
            onClose={() => setSelectedStageId(null)}
          />
        </div>
      )}
    </div>
  );
}
