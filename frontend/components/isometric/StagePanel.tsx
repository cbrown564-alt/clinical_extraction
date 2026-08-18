"use client";

import type {
  StageObservationData,
  StationLayoutNode,
  TeachingCaseData,
  TeachingRunData,
} from "@/lib/isometricTypes";
import {
  ACCENT,
  catalogMatches,
  effectiveCatalog,
  lensThisCaseLine,
  usefulStageNote,
} from "@/lib/isometricLayout";

interface StagePanelProps {
  station: StationLayoutNode;
  observations: StageObservationData[];
  activeCase: TeachingCaseData | undefined;
  activeRun?: TeachingRunData;
  onClose: () => void;
}

function truncate(text: string, max = 420): string {
  const trimmed = text.trim();
  if (trimmed.length <= max) return trimmed;
  return `${trimmed.slice(0, max).trimEnd()}…`;
}

function formatPromptText(raw: string): string {
  const trimmed = raw.trim();
  if (!trimmed || trimmed.startsWith("prompt input of ")) {
    return "";
  }
  try {
    return JSON.stringify(JSON.parse(trimmed), null, 2);
  } catch {
    return trimmed;
  }
}

export default function StagePanel({
  station,
  observations,
  activeCase,
  activeRun,
  onClose,
}: StagePanelProps) {
  const fired = observations.filter((obs) => obs.changed);
  const catalog = effectiveCatalog(station, observations);

  const thisCaseLines =
    station.kind === "source"
      ? [activeCase ? `${activeCase.letter_id}. ${activeCase.story}` : "No letter loaded."]
      : station.kind === "score" && activeRun
        ? [
            ...activeRun.final_answer.split("\n"),
            activeRun.correctness_note,
          ].filter((line) => line.trim().length > 0)
        : station.kind === "lenses"
          ? catalog.map((item) =>
              lensThisCaseLine(
                item,
                observations.find((obs) => catalogMatches(item, obs))
              )
            )
        : catalog
            .filter((item) =>
              observations.some((obs) => catalogMatches(item, obs) && obs.changed)
            )
            .map((item) => {
              const obs = observations.find((o) => catalogMatches(item, o) && o.changed);
              const note = usefulStageNote(obs?.note ?? "");
              return note ? `${item.label}: ${note}` : item.label;
            });

  return (
    <aside className="flex h-full w-full flex-col border-l border-neutral-200 bg-white text-neutral-900">
      <div className="flex items-start justify-between gap-3 border-b border-neutral-200 px-5 py-4">
        <div>
          <h2 className="text-lg font-semibold">{station.name}</h2>
          <p className="mt-1 max-w-prose text-sm text-neutral-600">{station.alwaysDoes}</p>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-sm text-neutral-500 hover:text-neutral-900"
        >
          Close
        </button>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto px-5 py-4 text-sm">
        {catalog.length > 0 && (
          <section>
            <h3 className="mb-2 text-xs font-medium text-neutral-500">Catalog</h3>
            <ul className="space-y-1">
              {catalog.map((item) => {
                const itemObs = observations.filter((obs) => catalogMatches(item, obs));
                const isOn = itemObs.some((obs) => obs.changed);
                const inMethod = itemObs.length > 0;
                return (
                  <li
                    key={item.id}
                    className={isOn ? "font-medium text-neutral-900" : "text-neutral-500"}
                  >
                    {item.label}
                    <span
                      className="ml-2 font-normal"
                      style={isOn ? { color: ACCENT } : undefined}
                    >
                      {inMethod ? (isOn ? "on" : "idle") : "not in this method"}
                    </span>
                  </li>
                );
              })}
            </ul>
          </section>
        )}

        {station.kind === "source" && activeCase && (
          <section>
            <h3 className="mb-2 text-xs font-medium text-neutral-500">Letter</h3>
            <p className="note-text whitespace-pre-wrap">{activeCase.note_text}</p>
          </section>
        )}

        {station.kind === "prompt" && (
          <section>
            <h3 className="mb-2 text-xs font-medium text-neutral-500">Prompt</h3>
            {observations[0] && formatPromptText(observations[0].output) ? (
              <pre className="whitespace-pre-wrap break-words font-sans text-sm leading-snug">
                {formatPromptText(observations[0].output)}
              </pre>
            ) : (
              <p className="text-neutral-500">Not in this method.</p>
            )}
          </section>
        )}

        <section>
          <h3 className="mb-2 text-xs font-medium text-neutral-500">This case</h3>
          {thisCaseLines.length === 0 ? (
            <p className="text-neutral-500">Nothing at this stage on this case.</p>
          ) : (
            <ul className="space-y-1.5">
              {thisCaseLines.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          )}
        </section>

        {fired.length > 0 && station.kind !== "source" && station.kind !== "prompt" && (
          <section className="space-y-4">
            <h3 className="text-xs font-medium text-neutral-500">
              {fired.length === 1 ? "Change" : "Changes"}
            </h3>
            {fired.map((obs) => (
              <div key={obs.stage_id}>
                <p className="mb-2 font-medium">{obs.stage_name}</p>
                <p className="text-xs text-neutral-500">In</p>
                <p className="mb-3 whitespace-pre-wrap">{truncate(obs.input)}</p>
                <p className="text-xs text-neutral-500">Out</p>
                <p className="whitespace-pre-wrap">{truncate(obs.output)}</p>
              </div>
            ))}
          </section>
        )}
      </div>
    </aside>
  );
}
