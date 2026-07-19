"use client";

import { Suspense, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { DATASET_PARAM } from "@/lib/datasets";

/**
 * Legacy ExECTv2 destination. ExECTv2 now lives in the explorer as a dataset, so
 * this route redirects to the integrated Example Explorer, forwarding any run /
 * letter selection and pinning `dataset=exectv2`.
 */
function Exectv2Redirect() {
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString());
    params.set(DATASET_PARAM, "exectv2");
    router.replace(`/workbench?${params.toString()}`);
  }, [router, searchParams]);

  return (
    <div className="flex h-full items-center justify-center bg-background text-muted">
      <p className="text-sm font-medium">Opening ExECTv2 in the Example Explorer…</p>
    </div>
  );
}

export default function Exectv2Page() {
  return (
    <Suspense fallback={null}>
      <Exectv2Redirect />
    </Suspense>
  );
}
