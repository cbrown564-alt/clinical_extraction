import type { Metadata } from "next";
import ClinicalReviewWorkspace from "@/components/clinical-review/ClinicalReviewWorkspace";

export const metadata: Metadata = {
  title: "Clinical Review",
  description: "Blinded correctness and semantic-support review of ExECTv2 extractions.",
};

export default function ClinicalReviewPage() {
  return <ClinicalReviewWorkspace />;
}
