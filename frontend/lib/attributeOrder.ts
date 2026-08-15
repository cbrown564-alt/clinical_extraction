/** Case-insensitive alphabetical order for attribute names in explorer tables. */
export function compareAttributeKeys(left: string, right: string): number {
  return left.localeCompare(right, undefined, { sensitivity: "base" });
}

const PINNED_ATTRIBUTE_KEYS = ["CUI", "CUIPhrase"] as const;
const PINNED_ATTRIBUTE_KEY_SET = new Set<string>(PINNED_ATTRIBUTE_KEYS);

/** CUI / CUIPhrase restated in the mention header; keep them first and quieter. */
export function isIdentityAttributeKey(key: string): boolean {
  return PINNED_ATTRIBUTE_KEY_SET.has(key);
}

export function sortedAttributeKeys(keys: Iterable<string>): string[] {
  const unique = Array.from(new Set(keys));
  const pinned = PINNED_ATTRIBUTE_KEYS.filter((key) => unique.includes(key));
  const rest = unique
    .filter((key) => !PINNED_ATTRIBUTE_KEY_SET.has(key))
    .sort(compareAttributeKeys);
  return [...pinned, ...rest];
}
