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

const METHODS: { id: MethodType; label: string }[] = [
  { id: "rules", label: "Rules" },
  { id: "llm", label: "LLM" },
  { id: "llm_with_rules", label: "LLM + rules" },
];

export default function AssemblyLineControls() {
  const cases = useAssemblyLineStore((state) => state.cases);
  const selectedCaseId = useAssemblyLineStore((state) => state.selectedCaseId);
  const selectedMethod = useAssemblyLineStore((state) => state.selectedMethod);
  const setSelectedCaseId = useAssemblyLineStore((state) => state.setSelectedCaseId);
  const setSelectedMethod = useAssemblyLineStore((state) => state.setSelectedMethod);

  return (
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
        <ControlField label="Method">
          <div className="flex items-center gap-1">
            {METHODS.map((method) => {
              const active = selectedMethod === method.id;
              return (
                <button
                  key={method.id}
                  type="button"
                  onClick={() => setSelectedMethod(method.id)}
                  className={`h-7 rounded-md px-2.5 text-xs ${
                    active
                      ? "bg-deterministic/10 font-semibold text-deterministic"
                      : "text-muted hover:bg-surface-raised hover:text-foreground"
                  }`}
                >
                  {method.label}
                </button>
              );
            })}
          </div>
        </ControlField>
      }
    />
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
