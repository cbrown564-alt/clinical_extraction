"use client";

import {
  ControlBar,
  ControlField,
  ControlSelect,
} from "@/components/surface";
import {
  getActiveAssemblyCase,
  useAssemblyLineStore,
} from "@/lib/assemblyLineStore";
import type { MethodType } from "@/lib/isometricStore";
import { PAPER_CELLS, teachingStandInCaption } from "@/lib/paperCells";

export default function AssemblyLineControls() {
  const cases = useAssemblyLineStore((state) => state.cases);
  const selectedCaseId = useAssemblyLineStore((state) => state.selectedCaseId);
  const selectedMethod = useAssemblyLineStore((state) => state.selectedMethod);
  const setSelectedCaseId = useAssemblyLineStore((state) => state.setSelectedCaseId);
  const setSelectedMethod = useAssemblyLineStore((state) => state.setSelectedMethod);
  const activeCase = useAssemblyLineStore(getActiveAssemblyCase);
  const standIn = activeCase
    ? teachingStandInCaption(activeCase.task, selectedMethod)
    : null;

  return (
    <>
    <ControlBar
      left={
        <ControlField label="Case" htmlFor="assembly-case">
          <ControlSelect
            id="assembly-case"
            value={selectedCaseId}
            onChange={(event) => setSelectedCaseId(event.target.value)}
          >
            {cases.map((teachingCase) => (
              <option key={teachingCase.case_id} value={teachingCase.case_id}>
                {teachingCase.task_label}: {teachingCase.letter_id}
              </option>
            ))}
          </ControlSelect>
        </ControlField>
      }
      right={
        <ControlField label="Cell">
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
                  className={`h-7 rounded-md px-2.5 text-xs ${
                    active
                      ? "bg-deterministic/10 font-semibold text-deterministic"
                      : "text-muted hover:bg-surface-raised hover:text-foreground"
                  }`}
                >
                  {cell.shortLabel}
                </button>
              );
            })}
          </div>
        </ControlField>
      }
    />
    {standIn && (
      <p className="border-b border-border px-4 py-1.5 text-[12px] leading-snug text-muted">
        {standIn}
      </p>
    )}
    </>
  );
}

export function AssemblyLineStory() {
  const activeCase = useAssemblyLineStore(getActiveAssemblyCase);
  if (!activeCase?.story) return null;
  return (
    <p className="border-b border-border px-4 py-2 font-serif text-[13px] leading-relaxed text-muted">
      {activeCase.story}
    </p>
  );
}
