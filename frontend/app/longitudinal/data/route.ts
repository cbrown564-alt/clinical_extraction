import { readFile } from "node:fs/promises";
import path from "node:path";
import { type Frame, type Patient } from "@/lib/longitudinal";

export const runtime = "nodejs";
const root = path.resolve(process.cwd(), "../results/longitudinal/prototype_v0.1");

export async function GET(request: Request) {
  const params = new URL(request.url).searchParams;
  const patient = params.get("patient") ?? "authored_patient_001";
  const index = params.get("index") ?? "T1";
  const view = params.get("view") ?? "visit";
  const mode = params.get("mode") ?? "reference";
  const query = params.get("query") ?? "Q2";
  if (!/^authored_patient_\d{3}$/.test(patient) || !["T1", "T2"].includes(index) ||
      !["visit", "retrospective"].includes(view) || !["reference", "predicted"].includes(mode) ||
      !/^Q[1-5]$/.test(query)) {
    return Response.json({ error: "Choose a listed patient, view and query." }, { status: 400 });
  }
  try {
    const catalog: { program_version: string; patients: Patient[] } = JSON.parse(await readFile(path.join(root, "patients.json"), "utf8"));
    if (!catalog.patients.some(p => p.id === patient)) return Response.json({ error: "Patient not found." }, { status: 404 });
    const frames = await Promise.all(catalog.patients.map(async p => {
      const frame: Frame = JSON.parse(await readFile(path.join(root, "frames", p.id, `${index}_${view}.${mode}.json`), "utf8"));
      // A frame file contains only letters allowed by its selected cutoff.
      if (frame.documents.some(d => d.available_date > frame.requests[0].information_cutoff)) throw new Error("Invalid frame cutoff");
      return { patient: p, frame };
    }));
    const selected = frames.find(f => f.patient.id === patient)!.frame;
    // Raw model captures and telemetry remain in the versioned local artifact.
    const { documents, history, answers, requests, status, error, program_version, offset_repairs, provenance } = selected;
    return Response.json({ ...catalog,
      selected: { documents, history, answers, requests, status, error, program_version, offset_repairs,
        provenance: { mode: provenance.mode, attempt: provenance.attempt ? { model_requested: provenance.attempt.model_requested } : undefined,
          query_context_visible_during_extraction: provenance.query_context_visible_during_extraction } },
      cohort: frames.map(({ patient: p, frame }) => {
        const answer = frame.answers.find(a => a.query_id === query)!;
        return { patient: p.id, label: p.label, index_date: frame.requests[0].index_date,
          cutoff: frame.requests[0].information_cutoff, status: answer.status, reason: answer.reason ?? answer.error ?? "" };
      }),
    }, { headers: { "Cache-Control": "no-store" } });
  } catch {
    return Response.json({ error: "The saved demonstration could not be loaded. Retry after the local artifact is available." }, { status: 503 });
  }
}
