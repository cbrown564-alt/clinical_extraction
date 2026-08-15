/** Splits the explorer may list as individual letters. */
const BROWSABLE_SPLITS = new Set([
  "dev750",
  "validation",
  "validation750",
  "development",
  "development750",
  "dev140",
  "dev",
]);

/** Locked holdout or mixed-corpus splits. Letter text must stay hidden. */
const LOCKED_SPLITS = new Set([
  "test",
  "test450",
  "test60",
  "holdout",
  "full200",
  "full-200",
  "full",
]);

export function isBrowsableSplit(split: string | undefined | null): boolean {
  if (!split) return false;
  const key = split.trim().toLowerCase();
  return BROWSABLE_SPLITS.has(key) && !LOCKED_SPLITS.has(key);
}

export function filterBrowsableLetters<T extends { split?: string }>(
  letters: readonly T[]
): T[] {
  return letters.filter((letter) => isBrowsableSplit(letter.split));
}
