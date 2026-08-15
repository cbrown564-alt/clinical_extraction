/** Shared surface shell – the chrome both datasets render every surface into. */
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
export { default as MetricChips, type MetricChip } from "./MetricChips";
export { default as LensStrip, type LensItem } from "./LensStrip";
export { default as ExplorerBody } from "./ExplorerBody";
export {
  default as SourceDocument,
  type RenderSpan,
  type HighlightTone,
} from "./SourceDocument";
export { ControlBar, ControlField, ControlSelect, LetterPicker } from "./ExplorerControls";
export {
  formatMetricValue,
  metricTone,
  F1Cell,
  DecisionBadge,
  MethodBadge,
  SurfaceLink,
  type MetricFormat,
} from "./atoms";
