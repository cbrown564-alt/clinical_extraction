export type PickerItem = {
  value: string;
  label: string;
  group?: string;
  disabled?: boolean;
};

function matchesQuery(item: PickerItem, needle: string): boolean {
  return (
    item.value.toLowerCase().includes(needle) ||
    item.label.toLowerCase().includes(needle) ||
    (item.group?.toLowerCase().includes(needle) ?? false)
  );
}

/** Case-insensitive substring match on the id, visible label, or group. */
export function filterPickerItems(
  items: readonly PickerItem[],
  query: string
): PickerItem[] {
  const needle = query.trim().toLowerCase();
  if (!needle) return [...items];
  return items.filter((item) => matchesQuery(item, needle));
}

/** Next or previous selectable catalog value. Does not wrap. Skips disabled. */
export function adjacentPickerValue(
  items: readonly PickerItem[],
  value: string,
  delta: -1 | 1
): string | null {
  const index = items.findIndex((item) => item.value === value);
  if (index < 0) return null;
  for (let next = index + delta; next >= 0 && next < items.length; next += delta) {
    if (!items[next].disabled) return items[next].value;
  }
  return null;
}

/** Keep the current value highlighted when it is still visible and selectable. */
export function highlightedPickerIndex(
  filtered: readonly PickerItem[],
  currentValue: string
): number {
  if (filtered.length === 0) return -1;
  const index = filtered.findIndex((item) => item.value === currentValue);
  if (index >= 0 && !filtered[index].disabled) return index;
  return filtered.findIndex((item) => !item.disabled);
}

/** Move the highlight to the next or previous enabled item. */
export function stepPickerIndex(
  items: readonly PickerItem[],
  current: number,
  delta: -1 | 1
): number {
  if (items.length === 0) return -1;
  const start =
    current < 0 || current >= items.length
      ? delta > 0
        ? -1
        : items.length
      : current;
  for (let next = start + delta; next >= 0 && next < items.length; next += delta) {
    if (!items[next].disabled) return next;
  }
  return current >= 0 && current < items.length ? current : -1;
}
