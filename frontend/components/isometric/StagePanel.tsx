"use client";

import type {
  StageObservationData,
  StationLayoutNode,
  TeachingCaseData,
} from "@/lib/isometricTypes";
import { ACCENT, catalogMatches } from "@/lib/isometricLayout";

interface StagePanelProps {
  station: StationLayoutNode;
  observations: StageObservationData[];
  activeCase: TeachingCaseData | undefined;
  onClose: () => void;
}

function truncate(text: string, max = 420): string {
  const trimmed = text.trim();
  if (trimmed.length <= max) return trimmed;
  return `${trimmed.slice(0, max).trimEnd()}…`;
}

export default function StagePanel({
  station,
  observations,
  activeCase,
  onClose,
}: StagePanelProps) {
  const fired = observations.filter((obs) => obs.changed);
  const changeObs = fired[0] ?? observations.find((obs) => obs.input !== obs.output);
  const catalog = station.catalog ?? [];

  const thisCaseLines =
    station.kind === "source"
      ? [activeCase ? `${activeCase.letter_id}. ${activeCase.story}` : "No letter loaded."]
      : catalog.length > 0
        ? catalog
            .filter((item) =>
              observations.some((obs) => catalogMatches(item, obs) && obs.changed)
            )
            .map((item) => {
              const obs = observations.find((o) => catalogMatches(item, o) && o.changed);
              return obs?.note ? `${item.label}: ${obs.note}` : item.label;
            })
        : observations.map((obs) => obs.note || obs.stage_name);

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

        {changeObs && changeObs.changed && (
          <section>
            <h3 className="mb-2 text-xs font-medium text-neutral-500">Change</h3>
            <p className="mb-2 font-medium">{changeObs.stage_name}</p>
            <p className="text-xs text-neutral-500">In</p>
            <p className="mb-3 whitespace-pre-wrap">{truncate(changeObs.input)}</p>
            <p className="text-xs text-neutral-500">Out</p>
            <p className="whitespace-pre-wrap">{truncate(changeObs.output)}</p>
          </section>
        )}
      </div>
    </aside>
  );
}
