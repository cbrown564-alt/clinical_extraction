import type { Metadata } from "next";
import SemanticSupportReviewWorkspace from "@/components/semantic-support-review/SemanticSupportReviewWorkspace";

export const metadata: Metadata = {
  title: "Semantic Support Review",
  description: "Blinded independent review of ExECTv2 evidence and clinical conclusions.",
};

export default function SemanticSupportReviewPage() {
  return <SemanticSupportReviewWorkspace />;
}
