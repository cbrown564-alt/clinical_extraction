/** Case-insensitive alphabetical order for attribute names in explorer tables. */
export function compareAttributeKeys(left: string, right: string): number {
  return left.localeCompare(right, undefined, { sensitivity: "base" });
}

export function sortedAttributeKeys(keys: Iterable<string>): string[] {
  return Array.from(new Set(keys)).sort(compareAttributeKeys);
}
