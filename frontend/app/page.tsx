import Link from "next/link";

export default function Home() {
  return (
    <main className="flex min-h-full flex-col items-center justify-center gap-6 p-8">
      <h1 className="text-3xl font-semibold text-foreground">
        Clinical Extraction Observatory
      </h1>
      <p className="max-w-md text-center text-muted">
        Interactive lens for hybrid clinical-extraction pipelines. Inspect,
        compare, and understand stage-by-stage extraction.
      </p>
      <Link
        href="/workbench"
        className="rounded-md bg-deterministic px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-deterministic/90"
      >
        Open the Workbench
      </Link>
    </main>
  );
}
