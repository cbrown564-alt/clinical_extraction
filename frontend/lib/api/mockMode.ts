import { fetchJson } from "./client";

export type MockModeReason = "env" | "health-check";

let mockMode = process.env.NEXT_PUBLIC_MOCK_API === "1";
let mockModeReason: MockModeReason | null = mockMode ? "env" : null;
let resolved = mockMode;
let resolvePromise: Promise<void> | null = null;

const listeners = new Set<() => void>();

function notify() {
  listeners.forEach((listener) => listener());
}

export function isMockMode(): boolean {
  return mockMode;
}

export function getMockModeReason(): MockModeReason | null {
  return mockModeReason;
}

export function enableMockMode(reason: MockModeReason): void {
  if (mockMode) return;
  mockMode = true;
  mockModeReason = reason;
  resolved = true;
  notify();
}

export function subscribeMockMode(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Resolves mock vs live mode once on the client (env var skips the health probe). */
export function ensureMockModeResolved(): Promise<void> {
  if (resolved) return Promise.resolve();
  if (typeof window === "undefined") return Promise.resolve();

  if (!resolvePromise) {
    resolvePromise = fetchJson<{ status: string }>("/health")
      .then(() => {
        resolved = true;
      })
      .catch(() => {
        enableMockMode("health-check");
      });
  }

  return resolvePromise;
}
