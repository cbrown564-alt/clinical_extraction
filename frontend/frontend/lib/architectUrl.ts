export function preserveWorkbenchDataset(
  next: URLSearchParams,
  current: Pick<URLSearchParams, "get">
): void {
  const dataset = current.get("dataset");
  if (dataset) next.set("dataset", dataset);
}
