import { syntheticPatients, fitSyntheticModel, type SyntheticPatient } from "./syntheticPatients";

/** Emergency-care simulation v1, seed 91026. Arbitrary teaching assumptions,
 * not published coefficients. Assessment at month 6, follow-up through month 18.
 * Additional notes and feature records are co-authored, never extracted by an LLM.
 */
export type EmergencyPatient = SyntheticPatient & {
  priorEmergency: number;
  tonicClonic: number | null;
  adherenceConcern: boolean | null;
  riskNote: string;
  emergencyOutcome: number | null;
};
export function generateEmergencyPatients(): EmergencyPatient[] {
  let seed = 91026;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  return syntheticPatients.map(patient => {
    const priorEmergency = Number(random() < .25);
    const recentRate = patient.visits.find(v => v.month === 6)?.rate;
    const tonicClonic = random() < .15 ? null : Math.min(Math.floor(random() * 5), recentRate == null ? 4 : recentRate * 3);
    const adherenceConcern = random() < .15 ? null : random() < .3;
    const known = patient.visits.filter(v => v.month <= 6 && v.rate !== null);
    const latest = known.at(-1)?.rate ?? 0;
    const change = latest - (known[0]?.rate ?? latest);
    const probability = 1 / (1 + Math.exp(-(-3 + .7 * priorEmergency + .55 * (tonicClonic ?? 1) + .9 * Number(adherenceConcern === true) + .08 * latest + .09 * change)));
    const outcome = Number(random() < probability);
    const emergencyOutcome = random() < .08 ? null : outcome;
    const riskNote = `SIMULATED CLINIC ADDENDUM · ${patient.id} · Month 6\n\n${tonicClonic === null ? "Tonic-clonic seizure frequency was not documented." : `${tonicClonic} tonic-clonic seizures were reported over the preceding three months.`}\n${adherenceConcern === null ? "Medication adherence was not discussed." : adherenceConcern ? "The patient reports missing medication doses most weeks." : "The patient reports taking medication regularly without missed doses."}\n\nCo-authored teaching text; not a real patient or extraction output.`;
    return { ...patient, priorEmergency, tonicClonic, adherenceConcern, riskNote, emergencyOutcome };
  });
}
export const emergencyPatients = generateEmergencyPatients();
export function emergencyFeatures(patient: SyntheticPatient, includeNotes: boolean) {
  const p = patient as EmergencyPatient;
  const structured = [p.age, p.medications, p.priorEmergency];
  if (!includeNotes) return structured;
  const known = p.visits.filter(v => v.month <= 6 && v.rate !== null);
  const latest = known.at(-1)?.rate ?? 0;
  return [...structured, latest, latest - (known[0]?.rate ?? latest), 3 - known.length,
    p.tonicClonic ?? 0, Number(p.tonicClonic === null), Number(p.adherenceConcern === true), Number(p.adherenceConcern === null)];
}
export function fitEmergencyModel(includeNotes: boolean) {
  const model = fitSyntheticModel(includeNotes, {
    patients: emergencyPatients,
    features: emergencyFeatures,
    target: p => (p as EmergencyPatient).emergencyOutcome,
  });
  return { ...model, featureNames: ["Age", "Medication count", "Prior emergency care", ...(includeNotes ? ["Latest frequency", "Frequency change", "Missing-frequency visits", "Tonic-clonic burden", "Unknown tonic-clonic burden", "Reported missed doses", "Unknown adherence"] : [])] };
}
export function reviewAtCapacity(rows: { patient: SyntheticPatient; probability: number; target: number }[], capacity: number) {
  const ranked = [...rows].sort((a, b) => b.probability - a.probability || a.patient.id.localeCompare(b.patient.id));
  const selected = ranked.slice(0, Math.max(0, Math.min(ranked.length, capacity)));
  const captured = selected.filter(r => r.target === 1).length;
  return { ranked, selected, captured, missed: ranked.filter(r => r.target === 1).length - captured, withoutEvent: selected.length - captured };
}
