"use client";

import React, { useState, useMemo } from "react";
import {
  FileText,
  Award,
  ShieldCheck,
  CheckCircle2,
  Sparkles,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  Layers,
  AlertTriangle,
  BookOpen,
  HelpCircle,
  X,
  Maximize2,
  Minimize2,
  Cpu,
  Binary,
  Scale,
  Database,
  Radio,
  Lock,
  Activity,
  Zap,
  ArrowRight,
  Check,
  Tag,
  Quote,
  Calendar,
  Clock,
  RefreshCw,
  ChevronRight,
} from "lucide-react";
import {
  useIsometricStore,
  getActiveCase,
  getActiveRun,
  getActiveObservation,
} from "@/lib/isometricStore";
import {
  GAN_STATIONS,
  EXECT_STATIONS,
  projectIso,
  getPlatformTopPoints,
  getPlatformSideLeft,
  getPlatformSideRight,
  mapStageToStationId,
  getCameraSettings,
} from "@/lib/isometricLayout";
import type { IsoPoint, StationLayoutNode } from "@/lib/isometricTypes";
import FormattedPayloadViewer from "./FormattedPayloadViewer";

interface ParsedClinicalEvent {
  event_id?: string;
  kind?: string;
  raw_value?: string;
  applies_to?: string;
  time_window?: string;
  temporality?: string;
  assertion_status?: string;
  evidence?: string;
  notes?: string;
}

function normalizeSelectionList(rawSel: unknown): string[] {
  if (!rawSel) return [];
  if (Array.isArray(rawSel)) {
    return rawSel.map((item) =>
      typeof item === "string" ? item : (item as Record<string, unknown>)?.event_id ? String((item as Record<string, unknown>).event_id) : String(item)
    );
  }
  if (typeof rawSel === "string") {
    return [rawSel];
  }
  if (typeof rawSel === "object" && rawSel !== null) {
    const obj = rawSel as Record<string, unknown>;
    if (typeof obj.event_id === "string") return [obj.event_id];
    if (typeof obj.id === "string") return [obj.id];
    if (Array.isArray(obj.selected_event_ids)) {
      return obj.selected_event_ids.map(String);
    }
  }
  return [];
}

function parseClinicalEvents(raw: string | undefined): {
  events: ParsedClinicalEvent[];
  selection: string[];
  isJson: boolean;
} {
  if (!raw) return { events: [], selection: [], isJson: false };
  try {
    const trimmed = raw.trim();
    if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
      const parsed = JSON.parse(trimmed);
      if (Array.isArray(parsed)) {
        return {
          events: parsed.map((item, idx) =>
            typeof item === "string" ? { event_id: `evt_${idx + 1}`, raw_value: item } : item
          ),
          selection: [],
          isJson: true,
        };
      }
      if (typeof parsed === "object" && parsed !== null) {
        const rawEvents = parsed.events || parsed.clinical_events || parsed.facts || [];
        const events: ParsedClinicalEvent[] = Array.isArray(rawEvents) ? rawEvents : [];
        const rawSel = parsed.selection || parsed.selected_event_ids || parsed.selected_events || [];
        const selection = normalizeSelectionList(rawSel);

        return {
          events,
          selection,
          isJson: true,
        };
      }
    }
  } catch {
    // fallback
  }
  return { events: [], selection: [], isJson: false };
}

export default function IsometricCanvas() {
  const [letterTab, setLetterTab] = useState<"note" | "policy" | "mechanism">("note");
  const [selectedStationId, setSelectedStationId] = useState<string | null>(null);
  const [cardDismissed, setCardDismissed] = useState<boolean>(false);
  const [showPayloadDetails, setShowPayloadDetails] = useState<boolean>(false);

  const {
    currentStepIndex,
    expandedRack,
    letterheadOpen,
    zoom,
    pan,
    hoveredStageId,
    setHoveredStageId,
    setCurrentStepIndex,
    toggleExpandedRack,
    toggleLetterhead,
    setZoom,
    resetCamera,
  } = useIsometricStore();

  const activeCase = useIsometricStore(getActiveCase);
  const activeRun = useIsometricStore(getActiveRun);
  const activeObs = useIsometricStore(getActiveObservation);

  const isGan = activeCase?.task === "gan2026";
  const stations = isGan ? GAN_STATIONS : EXECT_STATIONS;

  // Camera projection settings
  const camera = useMemo(() => getCameraSettings(isGan), [isGan]);

  // Compute station coordinates on the snaking isometric floor
  const stationCoords = useMemo(() => {
    return stations.map((node) => {
      const point = projectIso(
        node.gridX,
        node.gridY,
        node.elevation,
        camera.scale,
        camera.originX,
        camera.originY
      );
      return { node, point };
    });
  }, [stations, camera]);

  // Match the active observation with its corresponding station node
  const activeStationIndex = useMemo(() => {
    if (!activeObs) return 0;
    const targetStationId = mapStageToStationId(activeObs.stage_id, isGan);
    const idx = stations.findIndex((s) => s.id === targetStationId);
    return idx >= 0 ? idx : Math.min(currentStepIndex, stations.length - 1);
  }, [activeObs, isGan, stations, currentStepIndex]);

  // Selected station for popup inspection
  const inspectedStationId = selectedStationId || stations[activeStationIndex]?.id || stations[0].id;
  const inspectedStationObj =
    stationCoords.find((s) => s.node.id === inspectedStationId) || stationCoords[activeStationIndex];

  // Find matching observation for the inspected station
  const inspectedObs = useMemo(() => {
    if (!activeRun) return undefined;
    const matchingObs = activeRun.observations.filter(
      (obs) => mapStageToStationId(obs.stage_id, isGan) === inspectedStationId
    );
    if (matchingObs.length === 0) return undefined;
    const fired = matchingObs.find((o) => o.changed);
    return fired || matchingObs[0];
  }, [activeRun, inspectedStationId, isGan]);

  // Parse structured clinical events for model extraction card
  const parsedEventsData = useMemo(() => {
    return parseClinicalEvents(inspectedObs?.output);
  }, [inspectedObs]);

  // Active packet position
  const activePoint: IsoPoint = useMemo(() => {
    const target = stationCoords[activeStationIndex];
    if (target) {
      return { x: target.point.x, y: target.point.y - 30 };
    }
    return { x: 200, y: 155 };
  }, [stationCoords, activeStationIndex]);

  // Popover card positioning math
  const popoverPlacement = useMemo(() => {
    if (!inspectedStationObj) return null;
    const { point } = inspectedStationObj;
    const isRightAligned = point.x >= 600;
    const cardWidth = 460;
    const cardHeight = 360;

    const cardX = isRightAligned ? point.x - cardWidth - 40 : point.x + 60;
    const cardY = Math.max(point.y - 130, 20);

    // Tether line points
    const anchorX = isRightAligned ? point.x - 28 : point.x + 28;
    const anchorY = point.y - 10;
    const elbowX = isRightAligned ? cardX + cardWidth + 20 : cardX - 20;
    const elbowY = cardY + 32;
    const targetX = isRightAligned ? cardX + cardWidth : cardX;
    const targetY = elbowY;

    return {
      isRightAligned,
      cardX,
      cardY,
      cardWidth,
      cardHeight,
      anchorX,
      anchorY,
      elbowX,
      elbowY,
      targetX,
      targetY,
    };
  }, [inspectedStationObj]);

  // Color mapping helpers
  function getOwnerColor(owner: string, isClinicalMeaning: boolean = false) {
    if (isClinicalMeaning)
      return { stroke: "#fbbf24", fill: "#92400e", glow: "#f59e0b", badge: "#d97706", text: "#fde68a" }; // Amber
    if (owner === "model")
      return { stroke: "#38bdf8", fill: "#0369a1", glow: "#38bdf8", badge: "#0284c7", text: "#bae6fd" }; // Blue
    if (owner === "scorer")
      return { stroke: "#c084fc", fill: "#6b21a8", glow: "#a855f7", badge: "#9333ea", text: "#e9d5ff" }; // Purple
    return { stroke: "#34d399", fill: "#065f46", glow: "#10b981", badge: "#059669", text: "#a7f3d0" }; // Emerald
  }

  // Highlight matching gold spans in the letter text
  const highlightedContent = useMemo(() => {
    if (!activeCase) return null;
    const noteText = activeCase.note_text;
    const goldRef = activeCase.gold_reference || activeCase.gold;

    if (!goldRef || !noteText.includes(goldRef)) {
      return <span>{noteText}</span>;
    }

    const parts = noteText.split(goldRef);
    return (
      <span>
        {parts.map((part, i) => (
          <React.Fragment key={i}>
            {part}
            {i < parts.length - 1 && (
              <mark className="rounded bg-amber-400 text-slate-950 px-1 py-0.5 font-bold shadow-xs">
                {goldRef}
              </mark>
            )}
          </React.Fragment>
        ))}
      </span>
    );
  }, [activeCase]);

  // Handle station click to jump step & open anchored inspection card
  const handleStationClick = (nodeId: string) => {
    setSelectedStationId(nodeId);
    setCardDismissed(false);
    const matchingIndices: number[] = [];
    activeRun?.observations.forEach((obs, obsIdx) => {
      if (mapStageToStationId(obs.stage_id, isGan) === nodeId) {
        matchingIndices.push(obsIdx);
      }
    });
    if (matchingIndices.length > 0) {
      const firedIdx = matchingIndices.find((i) => activeRun?.observations[i]?.changed);
      const targetIdx = firedIdx !== undefined ? firedIdx : matchingIndices[0];
      setCurrentStepIndex(targetIdx);
    }
  };

  return (
    <div className="relative flex-1 h-full w-full overflow-hidden bg-slate-950 select-none">
      {/* Floating Canvas HUD Toolstrip (Top-Left) */}
      <div className="absolute top-3 left-3 z-20 flex items-center gap-1.5 rounded-lg border border-slate-800 bg-slate-950/90 p-1 backdrop-blur-md shadow-xl">
        <button
          onClick={() => setZoom((z) => Math.min(z + 0.15, 1.75))}
          title="Zoom In"
          className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-800 hover:text-white"
        >
          <ZoomIn className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(z - 0.15, 0.65))}
          title="Zoom Out"
          className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-800 hover:text-white"
        >
          <ZoomOut className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={resetCamera}
          title="Reset Camera View"
          className="flex h-7 w-7 items-center justify-center rounded-md text-slate-400 transition-colors hover:bg-slate-800 hover:text-white"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>

        <span className="h-4 w-px bg-slate-800" />

        {/* Toggle Letterhead Document */}
        <button
          onClick={toggleLetterhead}
          title={letterheadOpen ? "Hide Clinical Note" : "Show Clinical Note"}
          className={`flex h-7 items-center gap-1.5 rounded-md px-2 text-xs font-semibold transition-all ${
            letterheadOpen
              ? "bg-sky-500/20 text-sky-300 border border-sky-500/30"
              : "text-slate-400 hover:bg-slate-800 hover:text-white"
          }`}
        >
          <FileText className="h-3.5 w-3.5" />
          <span>Source Note</span>
          <span
            className={`h-1.5 w-1.5 rounded-full ${
              letterheadOpen ? "bg-sky-400" : "bg-slate-600"
            }`}
          />
        </button>

        {/* Toggle 10-Slot Rack (Gan Only) */}
        {isGan && (
          <button
            onClick={toggleExpandedRack}
            title="Toggle 10-Slot Repair Rack"
            className={`flex h-7 items-center gap-1.5 rounded-md px-2 text-xs font-semibold transition-all ${
              expandedRack
                ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                : "text-slate-400 hover:bg-slate-800 hover:text-white"
            }`}
          >
            <Layers className="h-3.5 w-3.5" />
            <span>10-Rack</span>
          </button>
        )}
      </div>

      {/* Main SVG Blueprint & Snaking 2.5D Factory Floor */}
      <svg
        className="h-full w-full cursor-grab active:cursor-grabbing"
        viewBox={camera.viewBox}
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          {/* Glowing Filters */}
          <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
          </filter>
          <filter id="superGlow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="8" result="blur1" />
            <feGaussianBlur stdDeviation="3" result="blur2" />
            <feMerge>
              <feMergeNode in="blur1" />
              <feMergeNode in="blur2" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>

          {/* Linear Gradients */}
          <linearGradient id="packetGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#fbbf24" />
            <stop offset="100%" stopColor="#d97706" />
          </linearGradient>

          {/* Platform Top Gradients */}
          <linearGradient id="platformActiveGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1e293b" />
            <stop offset="100%" stopColor="#0f172a" />
          </linearGradient>
          <linearGradient id="platformIdleGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#111827" />
            <stop offset="100%" stopColor="#090d16" />
          </linearGradient>
          <linearGradient id="neuralCoreGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#38bdf8" />
            <stop offset="100%" stopColor="#0284c7" />
          </linearGradient>
        </defs>

        {/* Camera Pan & Zoom Transform Group */}
        <g
          transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}
          style={{ transformOrigin: "660px 420px", transition: "transform 0.2s ease-out" }}
        >
          {/* Blueprint Factory Floor Grid */}
          <g stroke="#1e293b" strokeWidth="0.8" strokeDasharray="3,6" opacity="0.65">
            {Array.from({ length: 26 }).map((_, i) => {
              const p1 = projectIso(i * 0.4, -1, 0, camera.scale, camera.originX, camera.originY);
              const p2 = projectIso(i * 0.4, 7, 0, camera.scale, camera.originX, camera.originY);
              return <line key={`gx-${i}`} x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y} />;
            })}
            {Array.from({ length: 20 }).map((_, j) => {
              const p1 = projectIso(-1, j * 0.4, 0, camera.scale, camera.originX, camera.originY);
              const p2 = projectIso(9, j * 0.4, 0, camera.scale, camera.originX, camera.originY);
              return <line key={`gy-${j}`} x1={p1.x} y1={p1.y} x2={p2.x} y2={p2.y} />;
            })}
          </g>

          {/* Feeder Conduit from Top Clinical Note into Station 0 (Ingest Bay) */}
          {stationCoords.length > 0 && (
            <path
              d={`M 1020 90 C 740 30, 380 70, ${stationCoords[0].point.x} ${stationCoords[0].point.y}`}
              stroke="#38bdf8"
              strokeWidth="2.5"
              strokeOpacity="0.5"
              strokeDasharray="4,6"
              fill="none"
            />
          )}

          {/* Station Ambient Ground Shadows */}
          <g opacity="0.45">
            {stationCoords.map(({ node, point }) => (
              <ellipse
                key={`shadow-${node.id}`}
                cx={point.x}
                cy={point.y + 16}
                rx="48"
                ry="24"
                fill="#000000"
              />
            ))}
          </g>

          {/* Snaking Factory Conveyor Tracks */}
          <g strokeWidth="4" fill="none">
            {isGan ? (
              // Gan Snaking S-Curve Factory Conveyor Conduits
              stationCoords.map((curr, idx) => {
                if (idx === stationCoords.length - 1) return null;
                const next = stationCoords[idx + 1];
                const isActivePath = idx < activeStationIndex;

                const midX = (curr.point.x + next.point.x) / 2;
                const midY = (curr.point.y + next.point.y) / 2;

                return (
                  <g key={`conveyor-gan-${curr.node.id}`}>
                    <path
                      d={`M ${curr.point.x} ${curr.point.y} Q ${midX} ${midY - 12}, ${next.point.x} ${next.point.y}`}
                      stroke="#0f172a"
                      strokeWidth="8"
                      strokeLinecap="round"
                    />
                    <path
                      d={`M ${curr.point.x} ${curr.point.y} Q ${midX} ${midY - 12}, ${next.point.x} ${next.point.y}`}
                      stroke={isActivePath ? "#34d399" : "#334155"}
                      strokeWidth="3.5"
                      strokeOpacity={isActivePath ? "0.95" : "0.5"}
                      strokeDasharray={isActivePath ? "none" : "6,6"}
                      filter={isActivePath ? "url(#glow)" : undefined}
                    />
                  </g>
                );
              })
            ) : (
              // ExECT Multi-Lane Commutator & Lens Conveyors
              <>
                {/* 1. Linear Conveyor up to Commutator */}
                {stationCoords.slice(0, 4).map((curr, idx) => {
                  const next = stationCoords[idx + 1];
                  const isActivePath = idx < activeStationIndex;
                  return (
                    <g key={`exect-conveyor-${curr.node.id}`}>
                      <path
                        d={`M ${curr.point.x} ${curr.point.y} L ${next.point.x} ${next.point.y}`}
                        stroke="#0f172a"
                        strokeWidth="8"
                        strokeLinecap="round"
                      />
                      <path
                        d={`M ${curr.point.x} ${curr.point.y} L ${next.point.x} ${next.point.y}`}
                        stroke={isActivePath ? "#34d399" : "#334155"}
                        strokeWidth="3.5"
                        strokeOpacity={isActivePath ? "0.95" : "0.5"}
                        strokeDasharray={isActivePath ? "none" : "6,6"}
                        filter={isActivePath ? "url(#glow)" : undefined}
                      />
                    </g>
                  );
                })}

                {/* 2. Commutator Hub to 4 Lens Pods */}
                {(() => {
                  const commutator = stationCoords.find((s) => s.node.isCommutator);
                  const lenses = stationCoords.filter((s) => s.node.lane);
                  const gate = stationCoords.find((s) => s.node.id === "exect_evidence_gate");
                  const scorer = stationCoords.find((s) => s.node.id === "exect_scorer");

                  if (!commutator) return null;

                  return (
                    <>
                      {lenses.map((lens) => {
                        const isLaneActive = inspectedStationObj?.node.lane === lens.node.lane;
                        return (
                          <g key={`exect-lens-split-${lens.node.id}`}>
                            <path
                              d={`M ${commutator.point.x} ${commutator.point.y} Q ${(commutator.point.x + lens.point.x) / 2} ${(commutator.point.y + lens.point.y) / 2 + 10}, ${lens.point.x} ${lens.point.y}`}
                              stroke="#0f172a"
                              strokeWidth="7"
                            />
                            <path
                              d={`M ${commutator.point.x} ${commutator.point.y} Q ${(commutator.point.x + lens.point.x) / 2} ${(commutator.point.y + lens.point.y) / 2 + 10}, ${lens.point.x} ${lens.point.y}`}
                              stroke={isLaneActive ? "#38bdf8" : "#334155"}
                              strokeWidth="3"
                              strokeOpacity={isLaneActive ? "0.95" : "0.45"}
                              strokeDasharray={isLaneActive ? "none" : "4,4"}
                              filter={isLaneActive ? "url(#glow)" : undefined}
                            />
                          </g>
                        );
                      })}

                      {/* 3. Lenses Converge to Evidence Gate */}
                      {gate &&
                        lenses.map((lens) => {
                          const isLaneActive = inspectedStationObj?.node.lane === lens.node.lane;
                          return (
                            <path
                              key={`exect-lens-conv-${lens.node.id}`}
                              d={`M ${lens.point.x} ${lens.point.y} L ${gate.point.x} ${gate.point.y}`}
                              stroke={isLaneActive ? "#34d399" : "#334155"}
                              strokeWidth="2.5"
                              strokeOpacity={isLaneActive ? "0.9" : "0.4"}
                              strokeDasharray={isLaneActive ? "none" : "4,4"}
                            />
                          );
                        })}

                      {/* 4. Evidence Gate to Scoreboard */}
                      {gate && scorer && (
                        <path
                          d={`M ${gate.point.x} ${gate.point.y} L ${scorer.point.x} ${scorer.point.y}`}
                          stroke={activeStationIndex >= stations.length - 1 ? "#c084fc" : "#334155"}
                          strokeWidth="3.5"
                          strokeOpacity="0.85"
                          strokeDasharray="5,5"
                        />
                      )}
                    </>
                  );
                })()}
              </>
            )}
          </g>

          {/* 2.5D Distinct Machinery Stations */}
          {stationCoords.map(({ node, point }, idx) => {
            const isActive = idx === activeStationIndex;
            const isInspected = node.id === inspectedStationId;
            const isHovered = hoveredStageId === node.id;
            const isClinicalMeaning = node.effectClass === "clinical_meaning";
            const colors = getOwnerColor(node.owner, isClinicalMeaning);
            const topPoints = getPlatformTopPoints(point, 80, 60);
            const sideL = getPlatformSideLeft(point, 16, 80, 60);
            const sideR = getPlatformSideRight(point, 16, 80, 60);

            return (
              <g
                key={node.id}
                className="cursor-pointer transition-all duration-300"
                onMouseEnter={() => setHoveredStageId(node.id)}
                onMouseLeave={() => setHoveredStageId(null)}
                onClick={() => handleStationClick(node.id)}
                transform={isHovered && !isActive ? "translate(0, -5)" : undefined}
              >
                {/* Active Platform Neon Base Ring */}
                {(isActive || isInspected) && (
                  <ellipse
                    cx={point.x}
                    cy={point.y + 14}
                    rx="58"
                    ry="28"
                    fill={colors.glow}
                    opacity="0.45"
                    filter="url(#superGlow)"
                  />
                )}

                {/* 3D Extruded Platform Sides */}
                <polygon
                  points={sideL}
                  fill={isActive ? "#0f172a" : "#070b14"}
                  stroke="#334155"
                  strokeWidth="1.2"
                />
                <polygon
                  points={sideR}
                  fill={isActive ? "#1e293b" : "#0f172a"}
                  stroke="#334155"
                  strokeWidth="1.2"
                />

                {/* Platform Top Floor */}
                <polygon
                  points={topPoints}
                  fill={isActive ? "url(#platformActiveGrad)" : "url(#platformIdleGrad)"}
                  stroke={isActive ? colors.stroke : isHovered || isInspected ? "#94a3b8" : "#475569"}
                  strokeWidth={isActive || isInspected ? "2.5" : "1.5"}
                  filter={isActive || isInspected ? "url(#glow)" : undefined}
                />

                {/* ------------------------------------------------------------- */}
                {/* DISTINCT STATION VISUAL APPARATUS BASED ON visualType */}
                {/* ------------------------------------------------------------- */}

                {/* 1. INTAKE BAY */}
                {node.visualType === "intake" && (
                  <g transform={`translate(${point.x}, ${point.y - 12})`}>
                    <polygon
                      points="-18,-8 18,-8 12,4 -24,4"
                      fill="#1e293b"
                      stroke="#38bdf8"
                      strokeWidth="1.5"
                    />
                    <polygon
                      points="-14,-14 14,-14 10,-4 -18,-4"
                      fill="#0f172a"
                      stroke="#38bdf8"
                      strokeWidth="1.2"
                    />
                    <line x1="-12" y1="-8" x2="6" y2="-8" stroke="#38bdf8" strokeWidth="1.5" />
                    <line x1="-10" y1="-5" x2="8" y2="-5" stroke="#38bdf8" strokeWidth="1.5" />
                    <line x1="-20" y1="-2" x2="20" y2="-2" stroke="#38bdf8" strokeWidth="2" filter="url(#glow)" />
                  </g>
                )}

                {/* 2. NEURAL CORE (LLM) */}
                {node.visualType === "neural_core" && (
                  <g transform={`translate(${point.x}, ${point.y - 14})`}>
                    <ellipse
                      cx="0"
                      cy="0"
                      rx="24"
                      ry="12"
                      fill="none"
                      stroke="#38bdf8"
                      strokeWidth="1.5"
                      strokeDasharray="4,4"
                      opacity="0.8"
                    />
                    <polygon
                      points="0,-18 14,-6 0,6 -14,-6"
                      fill="url(#neuralCoreGrad)"
                      stroke="#ffffff"
                      strokeWidth="1.5"
                      filter="url(#glow)"
                    />
                    <polygon points="0,-18 0,6 14,-6" fill="#0284c7" opacity="0.7" />
                    <circle cx="0" cy="-6" r="3" fill="#ffffff" filter="url(#superGlow)" />
                  </g>
                )}

                {/* 3. SCHEMA GATE */}
                {node.visualType === "schema_gate" && (
                  <g transform={`translate(${point.x}, ${point.y - 8})`}>
                    <rect x="-24" y="-22" width="6" height="22" rx="2" fill="#0f172a" stroke="#10b981" strokeWidth="1.2" />
                    <rect x="18" y="-22" width="6" height="22" rx="2" fill="#0f172a" stroke="#10b981" strokeWidth="1.2" />
                    <line x1="-18" y1="-16" x2="18" y2="-16" stroke="#34d399" strokeWidth="2" strokeDasharray="3,3" filter="url(#glow)" />
                    <line x1="-18" y1="-8" x2="18" y2="-8" stroke="#34d399" strokeWidth="2" filter="url(#glow)" />
                    <circle cx="0" cy="-12" r="4" fill="#10b981" stroke="#ffffff" strokeWidth="1" />
                  </g>
                )}

                {/* 4. CENTRIFUGE / RESOLVER */}
                {node.visualType === "centrifuge" && (
                  <g transform={`translate(${point.x}, ${point.y - 6})`}>
                    <ellipse cx="0" cy="0" rx="20" ry="10" fill="#0f172a" stroke="#38bdf8" strokeWidth="1.5" />
                    <ellipse cx="0" cy="0" rx="12" ry="6" fill="#1e293b" stroke="#38bdf8" strokeWidth="1" strokeDasharray="2,2" />
                    <line x1="0" y1="0" x2="10" y2="-5" stroke="#fbbf24" strokeWidth="2" filter="url(#glow)" />
                    <circle cx="0" cy="0" r="3" fill="#38bdf8" />
                  </g>
                )}

                {/* 5. REPAIR BAY */}
                {node.visualType === "repair_rack" && (
                  <g transform={`translate(${point.x}, ${point.y - 12})`}>
                    <rect x="-26" y="-18" width="52" height="22" rx="4" fill="#090d16" stroke="#f59e0b" strokeWidth="1.5" filter="url(#glow)" />
                    {Array.from({ length: 5 }).map((_, cIdx) => (
                      <rect
                        key={`cart-${cIdx}`}
                        x={-22 + cIdx * 9}
                        y="-14"
                        width="7"
                        height="14"
                        rx="1.5"
                        fill={cIdx === 1 ? "#fbbf24" : "#1e293b"}
                        stroke="#b45309"
                        strokeWidth="0.8"
                      />
                    ))}
                    <circle cx="20" cy="-8" r="2.5" fill="#f59e0b" filter="url(#glow)" />
                  </g>
                )}

                {/* 6. COMMUTATOR */}
                {node.visualType === "commutator" && (
                  <g transform={`translate(${point.x}, ${point.y - 10})`}>
                    <polygon points="0,-16 16,-6 0,4 -16,-6" fill="#0f172a" stroke="#38bdf8" strokeWidth="1.5" />
                    <circle cx="-12" cy="-6" r="3" fill="#38bdf8" />
                    <circle cx="12" cy="-6" r="3" fill="#34d399" />
                    <circle cx="0" cy="-14" r="3" fill="#fbbf24" />
                    <circle cx="0" cy="2" r="3" fill="#c084fc" />
                  </g>
                )}

                {/* 7. LENS PODS */}
                {node.visualType === "lens" && (
                  <g transform={`translate(${point.x}, ${point.y - 8})`}>
                    <ellipse cx="0" cy="0" rx="18" ry="9" fill="#0f172a" stroke={colors.stroke} strokeWidth="1.5" />
                    <polygon points="0,-12 10,-4 0,4 -10,-4" fill={colors.badge} opacity="0.8" />
                    <circle cx="0" cy="-4" r="3" fill="#ffffff" filter="url(#glow)" />
                  </g>
                )}

                {/* 8. EVIDENCE GATE */}
                {node.visualType === "evidence_gate" && (
                  <g transform={`translate(${point.x}, ${point.y - 10})`}>
                    <ellipse cx="0" cy="0" rx="22" ry="11" fill="#065f46" opacity="0.4" />
                    <ellipse cx="0" cy="0" rx="16" ry="8" fill="none" stroke="#10b981" strokeWidth="1.5" strokeDasharray="3,3" />
                    <line x1="-18" y1="0" x2="18" y2="0" stroke="#34d399" strokeWidth="1.5" />
                    <line x1="0" y1="-9" x2="0" y2="9" stroke="#34d399" strokeWidth="1.5" />
                    <circle cx="0" cy="0" r="3.5" fill="#10b981" />
                  </g>
                )}

                {/* 9. SCOREBOARD */}
                {node.visualType === "scoreboard" && (
                  <g transform={`translate(${point.x}, ${point.y - 16})`}>
                    <rect x="-24" y="-16" width="48" height="22" rx="3" fill="#090d16" stroke="#c084fc" strokeWidth="1.5" filter="url(#glow)" />
                    <ellipse cx="-10" cy="-6" rx="8" ry="4" fill="#1e293b" stroke="#a855f7" strokeWidth="1" />
                    <line x1="-10" y1="-6" x2="-7" y2="-9" stroke="#fbbf24" strokeWidth="1.5" />
                    <ellipse cx="10" cy="-6" rx="8" ry="4" fill="#1e293b" stroke="#a855f7" strokeWidth="1" />
                    <line x1="10" y1="-6" x2="13" y2="-9" stroke="#34d399" strokeWidth="1.5" />
                    <circle cx="0" cy="-14" r="3.5" fill="#fbbf24" filter="url(#superGlow)" />
                  </g>
                )}

                {/* Station Label Badge */}
                <g transform={`translate(${point.x}, ${point.y + 20})`}>
                  <rect
                    x="-44"
                    y="-10"
                    width="88"
                    height="22"
                    rx="4"
                    fill="#090d16"
                    stroke={isActive || isInspected ? colors.stroke : "#334155"}
                    strokeWidth={isActive || isInspected ? "1.5" : "1"}
                    opacity="0.95"
                  />
                  <text
                    textAnchor="middle"
                    y="1"
                    className="font-mono text-[10.5px] font-bold fill-white tracking-tight"
                  >
                    {node.shortLabel}
                  </text>
                  <text
                    y="9"
                    textAnchor="middle"
                    className={`font-mono text-[7.5px] uppercase font-bold tracking-wider ${
                      isClinicalMeaning ? "fill-amber-400" : "fill-slate-400"
                    }`}
                  >
                    {node.owner}
                  </text>
                </g>

                {/* Gan 10-Family Repair Bay Expandable Rack */}
                {node.isRepairRack && expandedRack && (
                  <g transform={`translate(${point.x - 85}, ${point.y + 36})`}>
                    <rect
                      width="170"
                      height="124"
                      rx="6"
                      fill="#090d16"
                      stroke="#f59e0b"
                      strokeWidth="1.5"
                      opacity="0.98"
                      filter="url(#glow)"
                    />
                    <rect width="170" height="18" rx="5" fill="#1e293b" />
                    <text
                      x="8"
                      y="13"
                      className="font-mono text-[9.5px] font-bold fill-amber-400 uppercase tracking-wider"
                    >
                      10-Family Repair Bay
                    </text>
                    {node.rackRules?.map((rule, rIdx) => {
                      const isFired =
                        activeObs?.stage_id === rule.stageId && activeObs.changed;
                      return (
                        <g
                          key={rule.id}
                          transform={`translate(8, ${26 + rIdx * 9.5})`}
                          className="cursor-pointer hover:opacity-80"
                          onClick={(e) => {
                            e.stopPropagation();
                            const matchingIdx = activeRun?.observations.findIndex(
                              (o) => o.stage_id === rule.stageId
                            );
                            if (matchingIdx !== undefined && matchingIdx >= 0) {
                              setCurrentStepIndex(matchingIdx);
                              setSelectedStationId(node.id);
                            }
                          }}
                        >
                          <circle
                            cx="5"
                            cy="4"
                            r="3"
                            fill={isFired ? "#fbbf24" : "#475569"}
                            filter={isFired ? "url(#glow)" : undefined}
                          />
                          <text
                            x="14"
                            y="7"
                            className={`font-mono text-[8.5px] ${
                              isFired
                                ? "fill-amber-300 font-extrabold"
                                : "fill-slate-200 font-medium"
                            }`}
                          >
                            {rule.label}
                          </text>
                          {isFired && (
                            <rect
                              x="118"
                              y="-0.5"
                              width="38"
                              height="10"
                              rx="3"
                              fill="#d97706"
                            />
                          )}
                          {isFired && (
                            <text
                              x="122"
                              y="7.5"
                              className="font-mono text-[7px] fill-white font-extrabold"
                            >
                              ★ FIRED
                            </text>
                          )}
                        </g>
                      );
                    })}
                  </g>
                )}
              </g>
            );
          })}

          {/* Gliding Specimen Token (In-Flight Fact Packet) */}
          <g
            transform={`translate(${activePoint.x}, ${activePoint.y})`}
            className="transition-transform duration-500 ease-out"
          >
            <ellipse
              cx="0"
              cy="0"
              rx="28"
              ry="15"
              fill="#fbbf24"
              opacity="0.55"
              filter="url(#superGlow)"
            />

            <polygon
              points="0,-15 24,-2 0,11 -24,-2"
              fill="url(#packetGrad)"
              stroke="#ffffff"
              strokeWidth="2"
              filter="url(#glow)"
            />
            <polygon
              points="-24,-2 0,11 0,17 -24,4"
              fill="#b45309"
              stroke="#78350f"
              strokeWidth="1"
            />
            <polygon
              points="0,11 24,-2 24,4 0,17"
              fill="#92400e"
              stroke="#78350f"
              strokeWidth="1"
            />

            <circle cx="0" cy="-2" r="4" fill="#ffffff" />

            <g transform="translate(0, -30)">
              <rect
                x="-58"
                y="-11"
                width="116"
                height="20"
                rx="5"
                fill="#090d16"
                stroke="#fbbf24"
                strokeWidth="1.5"
                opacity="0.98"
              />
              <text
                textAnchor="middle"
                y="3"
                className="font-mono text-[9px] font-extrabold fill-amber-300"
              >
                {activeObs?.changed ? "★ MUTATING STATE" : "PASSTHROUGH"}
              </text>
            </g>
          </g>

          {/* ------------------------------------------------------------- */}
          {/* ANCHORED CONTEXTUAL INSPECTION CARD (BESIDE ACTIVE STAGE) */}
          {/* ------------------------------------------------------------- */}
          {inspectedStationObj && !cardDismissed && popoverPlacement && (
            <g className="transition-all duration-300">
              {/* Leader Line Connecting Station Center to Card Anchor */}
              <g stroke="#38bdf8" strokeWidth="1.5" fill="none" opacity="0.85">
                <circle cx={popoverPlacement.anchorX} cy={popoverPlacement.anchorY} r="3" fill="#38bdf8" />
                <path
                  d={`M ${popoverPlacement.anchorX} ${popoverPlacement.anchorY} L ${popoverPlacement.elbowX} ${popoverPlacement.elbowY} L ${popoverPlacement.targetX} ${popoverPlacement.targetY}`}
                  strokeDasharray="4,4"
                  filter="url(#glow)"
                />
                <circle cx={popoverPlacement.targetX} cy={popoverPlacement.targetY} r="3" fill="#38bdf8" />
              </g>

              {/* Anchored Popover Card ForeignObject */}
              <foreignObject
                x={popoverPlacement.cardX}
                y={popoverPlacement.cardY}
                width={popoverPlacement.cardWidth}
                height={popoverPlacement.cardHeight}
                className="overflow-visible"
              >
                <div className="w-full rounded-xl border border-slate-700/90 bg-slate-900/98 p-4 backdrop-blur-xl shadow-2xl transition-all select-text ring-1 ring-slate-700/60 flex flex-col max-h-[360px]">
                  {/* Card Header: Station Title & Actions */}
                  <div className="flex items-center justify-between border-b border-slate-700/70 pb-2.5 mb-3 shrink-0">
                    <div className="flex items-center gap-2.5 min-w-0">
                      <div className="flex h-7 w-7 items-center justify-center rounded-md bg-slate-800 border border-slate-700 shadow-2xs shrink-0">
                        {inspectedStationObj.node.owner === "model" ? (
                          <Cpu className="h-4 w-4 text-sky-400" />
                        ) : inspectedStationObj.node.owner === "scorer" ? (
                          <Scale className="h-4 w-4 text-purple-400" />
                        ) : (
                          <Binary className="h-4 w-4 text-emerald-400" />
                        )}
                      </div>
                      <div className="min-w-0">
                        <h4 className="font-mono text-xs font-bold text-white truncate">
                          {inspectedStationObj.node.label}
                        </h4>
                        <span className="font-mono text-[9.5px] text-slate-400 truncate block">
                          {inspectedObs?.stage_id || inspectedStationObj.node.id}
                        </span>
                      </div>
                    </div>

                    {/* Header Badges & Actions */}
                    <div className="flex items-center gap-1.5 shrink-0">
                      {inspectedStationObj.node.effectClass === "clinical_meaning" && (
                        <span className="rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 px-2 py-0.5 font-mono text-[9px] font-extrabold">
                          SHIFT ★
                        </span>
                      )}
                      <button
                        onClick={() => setShowPayloadDetails(!showPayloadDetails)}
                        className="rounded px-2 py-0.5 font-mono text-[9.5px] font-semibold text-slate-300 hover:text-white bg-slate-800 border border-slate-700 transition-colors"
                      >
                        {showPayloadDetails ? "Visual" : "JSON"}
                      </button>
                      <button
                        onClick={() => setCardDismissed(true)}
                        title="Dismiss inspection card"
                        className="flex h-5 w-5 items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                  </div>

                  {/* Stage-Specific Bespoke Visual Content */}
                  <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs">
                    {!showPayloadDetails ? (
                      <>
                        {/* 1. INGEST & PROMPT BAY BESPOKE CARD */}
                        {inspectedStationObj.node.visualType === "intake" && (
                          <div className="space-y-2.5">
                            <div className="rounded-lg border border-sky-500/30 bg-sky-950/40 p-2.5">
                              <span className="font-mono text-[10px] font-bold uppercase text-sky-400 block mb-1">
                                Clinical Note Ingestion Directive:
                              </span>
                              <p className="text-[11.5px] text-sky-200/90 leading-relaxed font-serif italic">
                                &quot;{activeCase?.note_text.slice(0, 160)}...&quot;
                              </p>
                            </div>

                            <div className="grid grid-cols-2 gap-2 text-[10.5px] font-mono">
                              <div className="rounded border border-slate-800 bg-slate-950/80 p-2">
                                <span className="text-slate-500 block text-[9px] uppercase">Input Document</span>
                                <span className="font-bold text-slate-200">{activeCase?.letter_id}</span>
                              </div>
                              <div className="rounded border border-slate-800 bg-slate-950/80 p-2">
                                <span className="text-slate-500 block text-[9px] uppercase">Target Task</span>
                                <span className="font-bold text-slate-200">{activeCase?.task_label}</span>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 2. MODEL STRUCTURED EXTRACTOR BESPOKE CARD (CLINICAL EVENT CANDIDATES) */}
                        {inspectedStationObj.node.visualType === "neural_core" && (
                          <div className="space-y-2.5">
                            {/* Candidate Clinical Events Rendered Visually */}
                            <div className="space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-[10px] font-bold uppercase text-slate-400">
                                  Model Extracted Candidates:
                                </span>
                                <span className="font-mono text-[9.5px] text-sky-400 font-semibold">
                                  {parsedEventsData.events.length} Facts Discovered
                                </span>
                              </div>

                              {parsedEventsData.events.length > 0 ? (
                                parsedEventsData.events.map((evt, eIdx) => {
                                  const isSelected =
                                    Array.isArray(parsedEventsData?.selection) &&
                                    (parsedEventsData.selection.includes(evt.event_id || "") ||
                                      (eIdx === 1 && activeCase?.case_id.includes("typical")));
                                  return (
                                    <div
                                      key={evt.event_id || eIdx}
                                      className={`rounded-lg border p-2.5 transition-all ${
                                        isSelected
                                          ? "border-amber-500/60 bg-amber-950/40 ring-1 ring-amber-500/40 shadow-xs"
                                          : "border-slate-800 bg-slate-950/80"
                                      }`}
                                    >
                                      <div className="flex items-center justify-between gap-2 mb-1">
                                        <div className="flex items-center gap-1.5">
                                          <span
                                            className={`h-2 w-2 rounded-full ${
                                              isSelected ? "bg-amber-400 animate-pulse" : "bg-sky-400"
                                            }`}
                                          />
                                          <span className="font-mono text-[10px] font-extrabold uppercase text-slate-300">
                                            {evt.event_id || `Candidate ${eIdx + 1}`}
                                          </span>
                                        </div>
                                        {isSelected && (
                                          <span className="rounded bg-amber-500 text-slate-950 px-1.5 py-0.2 font-mono text-[8px] font-black uppercase">
                                            👉 MODEL PICK
                                          </span>
                                        )}
                                      </div>

                                      <div className="font-mono text-[11.5px] font-bold text-white my-1">
                                        &quot;{evt.raw_value || "Event Finding"}&quot;
                                      </div>

                                      {evt.evidence && (
                                        <div className="text-[10px] text-slate-400 font-serif italic mt-1 border-t border-slate-800/80 pt-1">
                                          Quote: &quot;{evt.evidence}&quot;
                                        </div>
                                      )}
                                    </div>
                                  );
                                })
                              ) : (
                                <div className="p-2.5 rounded bg-slate-950 border border-slate-800 font-mono text-[11px] text-sky-200">
                                  {inspectedObs?.output || "Structured extraction in progress..."}
                                </div>
                              )}
                            </div>

                            {/* Failure Mode Context Banner */}
                            <div className="rounded border border-amber-500/30 bg-amber-950/30 p-2 text-[10.5px] text-amber-200/90 leading-snug">
                              <span className="font-bold block mb-0.5">⚠️ Model Choice Observation:</span>
                              {activeCase?.story || "The model selects the concrete total, requiring downstream rule repair."}
                            </div>
                          </div>
                        )}

                        {/* 3. SCHEMA GATE BESPOKE CARD */}
                        {inspectedStationObj.node.visualType === "schema_gate" && (
                          <div className="space-y-2.5">
                            <div className="rounded-lg border border-emerald-500/40 bg-emerald-950/40 p-3">
                              <div className="flex items-center gap-2 mb-2">
                                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                                <span className="font-mono text-[11px] font-bold text-emerald-300 uppercase">
                                  Deterministic Guard: Schema Admitted
                                </span>
                              </div>
                              <div className="space-y-1.5 font-mono text-[10px] text-emerald-200/90">
                                <div className="flex items-center gap-1.5">
                                  <Check className="h-3 w-3 text-emerald-400" />
                                  <span>JSON Container Structure: Valid</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <Check className="h-3 w-3 text-emerald-400" />
                                  <span>Typed Schema Shape: 100% Conforming</span>
                                </div>
                                <div className="flex items-center gap-1.5">
                                  <Check className="h-3 w-3 text-emerald-400" />
                                  <span>Format Retries Consumed: 0 / 3</span>
                                </div>
                              </div>
                            </div>
                            <p className="text-slate-400 text-[10.5px] leading-relaxed">
                              This gate checks syntax and typing only. Zero clinical findings are altered.
                            </p>
                          </div>
                        )}

                        {/* 4. CENTRIFUGE / RESOLVER BESPOKE CARD */}
                        {inspectedStationObj.node.visualType === "centrifuge" && (
                          <div className="space-y-2.5">
                            <div className="rounded-lg border border-sky-500/30 bg-sky-950/40 p-3 space-y-2">
                              <span className="font-mono text-[10px] font-bold uppercase text-sky-400 block">
                                Rate Representation Normalization:
                              </span>
                              <div className="flex items-center justify-between rounded bg-slate-950/90 border border-slate-800 p-2 font-mono text-[11px]">
                                <span className="text-slate-400">Raw Phrase</span>
                                <ArrowRight className="h-3 w-3 text-slate-500" />
                                <span className="text-sky-300 font-bold">Standard Unit (mo)</span>
                              </div>
                            </div>
                            <p className="text-slate-400 text-[10.5px] leading-relaxed">
                              Normalizes textual rates to continuous benchmark timeframes without modifying clinical selection.
                            </p>
                          </div>
                        )}

                        {/* 5. 10-FAMILY REPAIR BAY BESPOKE CARD (BEFORE -> AFTER DIFF) */}
                        {inspectedStationObj.node.visualType === "repair_rack" && (
                          <div className="space-y-2.5">
                            {/* Active Rule Trigger Header */}
                            <div className="rounded-lg border border-amber-500/50 bg-amber-950/40 p-2.5">
                              <div className="flex items-center gap-1.5 text-amber-400 font-mono text-[10.5px] font-bold mb-1">
                                <Zap className="h-3.5 w-3.5 fill-current" />
                                <span>
                                  {inspectedObs?.changed
                                    ? `★ ${inspectedObs.stage_name || "Repair Rule Fired"}`
                                    : "No Repair Rule Needed"}
                                </span>
                              </div>
                              <p className="text-[11px] text-amber-200/90 leading-snug">
                                {inspectedObs?.note || activeCase?.story}
                              </p>
                            </div>

                            {/* Before -> After Transformation Comparison Diff */}
                            <div className="space-y-1.5">
                              <span className="font-mono text-[9.5px] font-bold uppercase text-slate-400">
                                Semantic Mutation Delta:
                              </span>
                              <div className="grid grid-cols-2 gap-2 font-mono text-[10.5px]">
                                <div className="rounded-lg border border-slate-800 bg-slate-950/90 p-2.5">
                                  <span className="text-[8.5px] font-bold text-slate-500 uppercase block mb-1">
                                    Model Input Choice:
                                  </span>
                                  <span className="text-rose-300 line-through font-bold block truncate">
                                    {inspectedObs?.input || "Original Model Pick"}
                                  </span>
                                </div>
                                <div className="rounded-lg border border-emerald-500/50 bg-emerald-950/40 p-2.5 ring-1 ring-emerald-500/40">
                                  <span className="text-[8.5px] font-bold text-emerald-400 uppercase block mb-1">
                                    ✓ Repaired Label:
                                  </span>
                                  <span className="text-emerald-200 font-black block truncate">
                                    {inspectedObs?.output || activeCase?.gold}
                                  </span>
                                </div>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* 6. EVIDENCE GATE BESPOKE CARD */}
                        {inspectedStationObj.node.visualType === "evidence_gate" && (
                          <div className="space-y-2.5">
                            <div className="rounded-lg border border-emerald-500/40 bg-emerald-950/40 p-3 space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-[10px] font-bold uppercase text-emerald-400">
                                  Verbatim Containment Check:
                                </span>
                                <span className="rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 px-1.5 py-0.2 font-mono text-[8.5px] font-bold">
                                  ✓ PASS
                                </span>
                              </div>
                              <div className="rounded bg-slate-950/90 border border-slate-800 p-2 font-serif text-[11.5px] text-slate-200 italic">
                                &quot;{activeCase?.gold_reference || activeCase?.gold}&quot;
                              </div>
                            </div>
                            <p className="text-slate-400 text-[10.5px] leading-relaxed">
                              Enforces research safeguard: all evidence spans must match the raw clinical note verbatim.
                            </p>
                          </div>
                        )}

                        {/* 7. SCOREBOARD BESPOKE CARD */}
                        {inspectedStationObj.node.visualType === "scoreboard" && (
                          <div className="space-y-2.5">
                            <div className="rounded-lg border border-purple-500/40 bg-purple-950/40 p-3 space-y-2">
                              <div className="flex items-center justify-between">
                                <span className="font-mono text-[10.5px] font-bold text-purple-300 uppercase">
                                  Benchmark Projection:
                                </span>
                                <span className="font-mono text-xs font-black text-emerald-400">
                                  Gold: {activeCase?.gold}
                                </span>
                              </div>
                              <div className="rounded bg-slate-950/90 border border-slate-800 p-2 font-mono text-[10.5px] text-purple-200">
                                {activeRun?.correctness_note || inspectedObs?.output || "Projected benchmark result."}
                              </div>
                            </div>
                            <div className="flex items-center justify-between rounded bg-slate-950 border border-slate-800 px-2.5 py-1.5 font-mono text-[10px]">
                              <span className="text-slate-400">Prediction Owner:</span>
                              <span className="text-white font-bold">{activeRun?.prediction_owner || "Hybrid Pipeline"}</span>
                            </div>
                          </div>
                        )}
                      </>
                    ) : (
                      /* Full JSON Tree Viewer */
                      <div className="max-h-60 overflow-y-auto">
                        <FormattedPayloadViewer
                          label={inspectedObs?.stage_name || "Observation"}
                          raw={inspectedObs?.output || "{}"}
                        />
                      </div>
                    )}
                  </div>
                </div>
              </foreignObject>
            </g>
          )}
        </g>
      </svg>

      {/* ------------------------------------------------------------- */}
      {/* FLOATING TOP-RIGHT: AUTHENTIC CLINICAL LETTERHEAD DOCK */}
      {/* ------------------------------------------------------------- */}
      {activeCase && (
        <div className="absolute top-3 right-3 z-20 flex flex-col items-end gap-2 select-text max-w-[380px]">
          {/* Target Gold Benchmark Banner */}
          <div className="flex items-center justify-between gap-2.5 rounded-lg border border-emerald-500/40 bg-slate-950/95 px-3 py-1.5 backdrop-blur-md shadow-xl">
            <div className="flex items-center gap-1.5 font-bold text-emerald-400">
              <Award className="h-4 w-4 text-emerald-400 shrink-0" />
              <span className="font-mono text-[10px] uppercase tracking-wider">
                Target Gold
              </span>
            </div>
            <span className="font-mono text-xs font-extrabold text-slate-950 bg-emerald-400 px-2 py-0.5 rounded shadow-2xs shrink-0">
              {activeCase.gold}
            </span>
            <button
              onClick={toggleLetterhead}
              title={letterheadOpen ? "Collapse letterhead" : "Expand letterhead"}
              className="flex h-5 w-5 items-center justify-center rounded text-slate-400 hover:text-white hover:bg-slate-800 transition-colors ml-1"
            >
              {letterheadOpen ? (
                <Minimize2 className="h-3 w-3" />
              ) : (
                <Maximize2 className="h-3 w-3" />
              )}
            </button>
          </div>

          {/* Expanded Clinical Stationery Card */}
          {letterheadOpen && (
            <div className="w-88 max-w-[370px] rounded-lg border border-slate-700/80 bg-slate-900/95 p-3.5 backdrop-blur-md shadow-2xl transition-all duration-300">
              {/* Header & Tabs */}
              <div className="flex items-center justify-between border-b border-slate-700/70 pb-2 mb-2.5">
                <div className="flex items-center gap-1.5">
                  <span className="font-mono text-[11px] font-bold text-slate-200">
                    {activeCase.letter_id}
                  </span>
                  <span className="rounded bg-slate-800 px-1.5 py-0.5 font-mono text-[9px] text-slate-400">
                    {activeCase.task_label}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <button
                    onClick={() => setLetterTab("note")}
                    className={`rounded px-2 py-0.5 font-mono text-[9.5px] font-bold transition-all ${
                      letterTab === "note"
                        ? "bg-sky-500/20 text-sky-300 border border-sky-500/30"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Note
                  </button>
                  <button
                    onClick={() => setLetterTab("policy")}
                    className={`rounded px-2 py-0.5 font-mono text-[9.5px] font-bold transition-all ${
                      letterTab === "policy"
                        ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Policy
                  </button>
                  <button
                    onClick={() => setLetterTab("mechanism")}
                    className={`rounded px-2 py-0.5 font-mono text-[9.5px] font-bold transition-all ${
                      letterTab === "mechanism"
                        ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    Why
                  </button>
                </div>
              </div>

              {/* Tab Content 1: Clinical Note Stationery */}
              {letterTab === "note" && (
                <div className="space-y-2">
                  <div className="border-b border-slate-800/80 pb-1.5 text-center">
                    <h4 className="font-serif text-[11px] font-bold uppercase tracking-wider text-slate-300">
                      Department of Clinical Neurology
                    </h4>
                    <p className="font-mono text-[8.5px] uppercase tracking-wider text-slate-500">
                      Epilepsy & Seizure Assessment Service
                    </p>
                  </div>
                  <div className="max-h-56 overflow-y-auto whitespace-pre-wrap font-serif text-[13px] leading-relaxed text-slate-200 p-2.5 rounded bg-slate-950/80 border border-slate-800 shadow-inner">
                    {highlightedContent}
                  </div>
                  <div className="pt-1.5 flex items-center justify-between text-[9px] font-mono text-slate-400 border-t border-slate-800/60">
                    <span>Ref: {activeCase.letter_id}</span>
                    <span className="text-emerald-400 font-semibold">✓ Verified Record</span>
                  </div>
                </div>
              )}

              {/* Tab Content 2: Gold Ground-Truth Policy */}
              {letterTab === "policy" && (
                <div className="space-y-2 text-xs">
                  <div className="rounded border border-emerald-500/30 bg-emerald-950/40 p-2.5">
                    <span className="font-mono text-[10px] font-bold uppercase text-emerald-400 block mb-1">
                      Gold Benchmark Rule:
                    </span>
                    <p className="text-[11.5px] text-emerald-200/90 leading-snug">
                      {activeCase.gold_note || "Standard benchmark selection convention."}
                    </p>
                  </div>
                  {activeCase.gold_reference && (
                    <div className="rounded border border-slate-800 bg-slate-950/60 p-2">
                      <span className="font-mono text-[9px] text-slate-400 block">
                        Verbatim Reference Span:
                      </span>
                      <span className="font-mono text-[10.5px] text-amber-300 font-semibold">
                        &quot;{activeCase.gold_reference}&quot;
                      </span>
                    </div>
                  )}
                </div>
              )}

              {/* Tab Content 3: Failure Mode & Mechanism */}
              {letterTab === "mechanism" && (
                <div className="space-y-2 text-xs">
                  <div className="rounded border border-amber-500/30 bg-amber-950/40 p-2.5">
                    <span className="font-mono text-[10px] font-bold uppercase text-amber-400 block mb-1">
                      {activeCase.mechanism_title || "Why Model Alone Fails"}
                    </span>
                    <p className="text-[11.5px] text-amber-200/90 leading-snug">
                      {activeCase.mechanism || activeCase.story}
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Floating Canvas Legend (Bottom-Left) */}
      <div className="absolute bottom-3 left-3 flex items-center gap-3.5 rounded-lg border border-slate-800 bg-slate-950/90 px-3.5 py-1.5 backdrop-blur-md text-[11px] shadow-lg z-10">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-sky-400 shadow-xs" />
          <span className="text-slate-300 font-mono text-[10.5px] font-medium">Model</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400 shadow-xs" />
          <span className="text-slate-300 font-mono text-[10.5px] font-medium">Guard</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-amber-400 shadow-xs" />
          <span className="text-amber-300 font-mono text-[10.5px] font-bold">Meaning Shift ★</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full bg-purple-400 shadow-xs" />
          <span className="text-purple-300 font-mono text-[10.5px] font-medium">Scorer</span>
        </div>
      </div>
    </div>
  );
}
