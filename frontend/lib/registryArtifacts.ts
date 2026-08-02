/**
 * Whether a registry artifact path can drive frontend replay/selection.
 *
 * Historical rows may point at pruned experiments/*.jsonl paths; Decision 0048
 * retargets those to served mock-data/artifacts/*.json copies. Either form is
 * scoreable for selector filters.
 */
export function isReplayableArtifactPath(path: string): boolean {
  if (path.endsWith(".jsonl")) return true;
  const normalized = path.replace(/\\/g, "/");
  return (
    normalized.includes("mock-data/artifacts/") && normalized.endsWith(".json")
  );
}

export function hasReplayableArtifact(paths: string[] | undefined | null): boolean {
  return Boolean(paths?.some(isReplayableArtifactPath));
}

export function firstReplayableArtifactPath(
  paths: string[] | undefined | null
): string | undefined {
  return paths?.find(isReplayableArtifactPath);
}
