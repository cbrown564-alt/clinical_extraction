import { categoryNames } from "@/lib/viva";
import styles from "./demo.module.css";

/** Categorical frequency marks, not a numeric scale. */
export function CategoryMark({ category }: { category: string }) {
  return <svg width="24" height="16" viewBox="0 0 24 16" fill="none" aria-hidden="true">
    {category === "currently_no_seizure" ? <path d="M3 8h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      : category === "seizure_freq_unknown" ? <path d="M3 8h3m4.5 0h3m4.5 0h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
      : <>
        <path d="M2 13h20" stroke="currentColor" strokeOpacity=".25" strokeWidth="1.5" />
        {(category === "seizure_infrequent" ? [11] : [3, 8, 13, 18]).map(x => <rect key={x} x={x} y="3" width="3" height="10" rx=".75" fill="currentColor" />)}
      </>}
  </svg>;
}

export default function CategoryPill({ category }: { category: string }) {
  return <span className={styles.categoryPill} data-category={category}><CategoryMark category={category} />{categoryNames[category] ?? category}</span>;
}
