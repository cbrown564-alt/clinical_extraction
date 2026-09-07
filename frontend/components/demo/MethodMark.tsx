/** Small diagrams of the operation: retain a passage, then select an answer. */
export default function MethodMark({ stage }: { stage: "extract" | "decide" }) {
  return <svg width="40" height="36" viewBox="0 0 40 36" fill="none" aria-hidden="true">
    {stage === "extract" ? <>
      <path d="M8 5h24M8 31h24" stroke="currentColor" strokeOpacity=".3" strokeWidth="1.5" />
      <rect x="5" y="12" width="30" height="12" rx="2" fill="currentColor" fillOpacity=".09" />
      <path d="M9 15H7v6h2m22-6h2v6h-2M13 18h14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </> : <>
      <path d="M5 7h8m-8 11h8m-8 11h8M16 7l8 11-8 11" stroke="currentColor" strokeOpacity=".4" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M5 18h22" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      <rect x="27" y="13" width="9" height="10" rx="2" fill="currentColor" fillOpacity=".09" stroke="currentColor" strokeWidth="1.5" />
    </>}
  </svg>;
}
