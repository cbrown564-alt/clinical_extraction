"use client";

import {
  useIsometricStore,
  getActiveCase,
  getActiveRun,
  type MethodType,
} from "@/lib/isometricStore";
import { ACCENT } from "@/lib/isometricLayout";
import { PAPER_CELLS, teachingStandInCaption } from "@/lib/paperCells";

export default function IsometricControls() {
  const { cases, selectedCaseId, selectedMethod, setSelectedCaseId, setSelectedMethod } =
    useIsometricStore();
  const activeCase = useIsometricStore(getActiveCase);
  const activeRun = useIsometricStore(getActiveRun);
  const standIn = activeCase
    ? teachingStandInCaption(activeCase.task, selectedMethod)
    : null;

  return (
    <div className="border-b border-neutral-200 bg-white px-4 py-2 text-neutral-900">
      <div className="flex flex-wrap items-center gap-3">
      <label className="flex min-w-0 items-center gap-2 text-sm">
        <span className="text-neutral-500">Case</span>
        <select
          value={selectedCaseId}
          onChange={(event) => setSelectedCaseId(event.target.value)}
          className="h-8 max-w-[360px] truncate border border-neutral-300 bg-white px-2 text-sm"
        >
          {cases.map((teachingCase) => (
            <option key={teachingCase.case_id} value={teachingCase.case_id}>
              {teachingCase.task_label}: {teachingCase.letter_id}
            </option>
          ))}
        </select>
      </label>

      <div className="flex items-center gap-1">
        {PAPER_CELLS.map((cell) => {
          const active = selectedMethod === cell.id;
          const title = cell.headline
            ? `${cell.displayName} (headline)`
            : cell.displayName;
          return (
            <button
              key={cell.id}
              type="button"
              onClick={() => setSelectedMethod(cell.id as MethodType)}
              title={title}
              aria-label={title}
              className={`h-8 px-2.5 text-sm ${
                active ? "font-semibold" : "border border-transparent text-neutral-500"
              }`}
              style={active ? { boxShadow: `inset 0 0 0 1px ${ACCENT}` } : undefined}
            >
              {cell.shortLabel}
            </button>
          );
        })}
      </div>
      </div>
      {standIn && (
        <p className="mt-1 max-w-4xl text-xs leading-snug text-neutral-500">
          {standIn}
        </p>
      )}
      {(activeRun?.one_sentence || activeCase?.mechanism) && (
        <p className="mt-2 max-w-4xl text-sm leading-snug text-neutral-700">
          {activeRun?.one_sentence || activeCase?.mechanism}
        </p>
      )}
    </div>
  );
}
