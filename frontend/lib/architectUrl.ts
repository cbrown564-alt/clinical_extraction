export function preserveWorkbenchDataset(
  next: URLSearchParams,
  current: Pick<URLSearchParams, "get">
): void {
  const dataset = current.get("dataset");
  if (dataset) next.set("dataset", dataset);
}

export function preserveWorkbenchView(
  next: URLSearchParams,
  current: Pick<URLSearchParams, "get">
): void {
  const view = current.get("view");
  if (view) next.set("view", view);
}
