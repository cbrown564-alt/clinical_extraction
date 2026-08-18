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
} from "@/lib/isometricLayout";
import type { StationActivation } from "@/lib/isometricTypes";
import StagePanel from "./StagePanel";

function statusClass(activation: StationActivation, selected: boolean): string {
  if (selected) return "font-semibold text-neutral-900";
  if (activation === "on") return "font-semibold text-neutral-900";
  return "font-normal text-neutral-500";
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
                stroke="#d4d4d4"
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
              className={`absolute w-36 -translate-x-1/2 -translate-y-1/2 bg-white px-2 py-2 text-left ${
                selectedHere ? "border border-neutral-900" : "border border-transparent"
              }`}
              style={{ left, top }}
            >
              <div className={`text-sm ${statusClass(activation, selectedHere)}`}>
                {station.name}
              </div>
              <div className={`text-xs ${activation === "on" ? "text-neutral-700" : "text-neutral-500"}`}>
                {activationLabel(activation, onCount, catalogSize)}
              </div>
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
            onClose={() => setSelectedStageId(null)}
          />
        </div>
      )}
    </div>
  );
}
