export type PickerItem = {
  value: string;
  label: string;
};

/** Case-insensitive substring match on the id or the visible label. */
export function filterPickerItems(
  items: readonly PickerItem[],
  query: string
): PickerItem[] {
  const needle = query.trim().toLowerCase();
  if (!needle) return [...items];
  return items.filter(
    (item) =>
      item.value.toLowerCase().includes(needle) ||
      item.label.toLowerCase().includes(needle)
  );
}

/** Next or previous catalog value. Does not wrap. */
export function adjacentPickerValue(
  items: readonly PickerItem[],
  value: string,
  delta: -1 | 1
): string | null {
  const index = items.findIndex((item) => item.value === value);
  if (index < 0) return null;
  const next = index + delta;
  if (next < 0 || next >= items.length) return null;
  return items[next].value;
}

/** Keep the current value highlighted when it is still in the filtered list. */
export function highlightedPickerIndex(
  filtered: readonly PickerItem[],
  currentValue: string
): number {
  if (filtered.length === 0) return -1;
  const index = filtered.findIndex((item) => item.value === currentValue);
  return index >= 0 ? index : 0;
}
