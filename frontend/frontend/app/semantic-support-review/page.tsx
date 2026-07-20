import type { Metadata } from "next";
import ClinicalReviewWorkspace from "@/components/clinical-review/ClinicalReviewWorkspace";

export const metadata: Metadata = {
  title: "Semantic Support Review",
  description: "Blinded independent review of ExECTv2 evidence and clinical conclusions.",
};

export default function SemanticSupportReviewPage() {
  return <ClinicalReviewWorkspace defaultTask="semantic" />;
}
