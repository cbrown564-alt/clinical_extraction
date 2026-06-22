/** Shared surface shell — the chrome both datasets render every surface into. */
export {
  SURFACE_META,
  SURFACE_ORDER,
  SURFACE_TONE_ACTIVE,
  SURFACE_TONE_ICON,
  type SurfaceMeta,
} from "./meta";
export { default as SurfaceHeader } from "./SurfaceHeader";
export { default as SurfaceLayout } from "./SurfaceLayout";
export { SurfaceLoading, SurfaceError, SurfaceEmpty } from "./SurfaceStates";
export { default as MetricStrip, type MetricTile } from "./MetricStrip";
export {
  formatMetricValue,
  metricTone,
  F1Cell,
  DecisionBadge,
  SurfaceLink,
  type MetricFormat,
} from "./atoms";
