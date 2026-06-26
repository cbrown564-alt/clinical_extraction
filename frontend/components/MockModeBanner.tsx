"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import { AlertTriangle } from "lucide-react";
import {
  ensureMockModeResolved,
  getMockModeReason,
  isMockMode,
  subscribeMockMode,
} from "@/lib/api";

function useMockModeActive() {
  return useSyncExternalStore(
    subscribeMockMode,
    () => isMockMode(),
    () => process.env.NEXT_PUBLIC_MOCK_API === "1"
  );
}

export default function MockModeBanner() {
  const active = useMockModeActive();
  const [ready, setReady] = useState(process.env.NEXT_PUBLIC_MOCK_API === "1");

  useEffect(() => {
    void ensureMockModeResolved().finally(() => setReady(true));
  }, []);

  if (!ready || !active) return null;

  const reason = getMockModeReason();
  const detail =
    reason === "env"
      ? "NEXT_PUBLIC_MOCK_API is enabled."
      : "Backend health check failed — serving static demo data.";

  return (
    <div
      role="status"
      className="shrink-0 flex items-center gap-2 border-b border-amber-500/30 bg-amber-500/10 px-4 py-1.5 text-xs text-amber-900 dark:text-amber-100"
    >
      <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-600 dark:text-amber-400" />
      <span>
        <strong className="font-semibold">Mock API mode</strong>
        {" — "}
        {detail} Data shown is not live.
      </span>
    </div>
  );
}
