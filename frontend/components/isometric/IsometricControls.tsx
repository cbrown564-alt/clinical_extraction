"use client";

import {
  useIsometricStore,
  type MethodType,
} from "@/lib/isometricStore";
import { ACCENT } from "@/lib/isometricLayout";

const METHODS: { id: MethodType; label: string }[] = [
  { id: "rules", label: "Rules" },
  { id: "llm", label: "Model" },
  { id: "llm_with_rules", label: "Hybrid" },
];

export default function IsometricControls() {
  const { cases, selectedCaseId, selectedMethod, setSelectedCaseId, setSelectedMethod } =
    useIsometricStore();

  return (
    <div className="flex flex-wrap items-center gap-3 border-b border-neutral-200 bg-white px-4 py-2 text-neutral-900">
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
        {METHODS.map((method) => {
          const active = selectedMethod === method.id;
          return (
            <button
              key={method.id}
              type="button"
              onClick={() => setSelectedMethod(method.id)}
              className={`h-8 px-2.5 text-sm ${
                active ? "font-semibold" : "border border-transparent text-neutral-500"
              }`}
              style={active ? { boxShadow: `inset 0 0 0 1px ${ACCENT}` } : undefined}
            >
              {method.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
