/** Authored simulation v1, seed 8056. No source patients, benchmark rows or model calls.
 * Latent burden follows a noisy trajectory; visit documentation sometimes omits frequency.
 * The notes and structured records are co-generated, NOT pipeline extraction outputs.
 */
export type Visit = { id: string; month: number; rate: number | null; evidence: string; note: string };
export type SyntheticPatient = { id: string; age: number; type: "Focal" | "Generalised"; medications: number; visits: Visit[]; partition: "train" | "test" };
export const visitMonths = [0, 3, 6, 9, 12];
export function generatePatients(): SyntheticPatient[] {
  let seed = 8056;
  const random = () => { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
  return Array.from({ length: 72 }, (_, i) => {
    const id = `S${String(i + 1).padStart(3, "0")}`;
    const age = 18 + Math.floor(random() * 60);
    const type = random() > .3 ? "Focal" as const : "Generalised" as const;
    const medications = 1 + Math.floor(random() * 3);
    let burden = random() * 12;
    const drift = (random() - .57) * 5;
    const visits = visitMonths.map(month => {
      burden = Math.max(0, Math.min(20, burden + drift + (random() - .5) * 8));
      const rate = random() < .12 ? null : Math.round(burden);
      const evidence = rate === null ? "Seizures were discussed, but their frequency was not recorded." : rate === 0 ? "No seizures have occurred in the past three months." : `There have been ${rate} seizures per month over the past three months.`;
      return { id: `${id}-M${month}`, month, rate, evidence, note: `SIMULATED CLINIC NOTE\nPatient ${id} · Month ${month}\n\n${age}-year-old adult with ${type.toLowerCase()} epilepsy. ${medications} antiseizure medication${medications === 1 ? " is" : "s are"} listed.\n\n${evidence}\n\nThis fictional visit was generated for an interface demonstration. It is not a clinical record.` };
    });
    return { id, age, type, medications, visits, partition: i % 3 === 0 ? "test" : "train" };
  });
}
export const syntheticPatients = generatePatients();
export function stateFor(rate: number | null) { return rate === null ? "Unknown" : rate === 0 ? "Seizure free" : rate < 4 ? "1–3 / month" : "4+ / month"; }
export function featuresFor(patient: SyntheticPatient, includeNotes: boolean): number[] {
  const structured = [patient.age, patient.medications];
  if (!includeNotes) return structured;
  // Only information available by month 6; future visits are never read here.
  const visits = patient.visits.filter(v => v.month <= 6);
  const known = visits.filter((v): v is Visit & { rate: number } => v.rate !== null);
  const latest = known.at(-1)?.rate ?? 0;
  return [...structured, latest, known.length > 1 ? latest - known[0].rate : 0, visits.filter(v => v.rate === null).length];
}
export function targetFor(p: SyntheticPatient): number | null {
  const rate = p.visits.find(v => v.month === 12)?.rate;
  return rate == null ? null : Number(rate > 0);
}
export function aucFor(rows: { probability: number; target: number }[]): number | null {
  const positives = rows.filter(r => r.target === 1), negatives = rows.filter(r => r.target === 0);
  if (!positives.length || !negatives.length) return null;
  return positives.reduce((sum, p) => sum + negatives.reduce((s, n) => s + (p.probability > n.probability ? 1 : p.probability === n.probability ? .5 : 0), 0), 0) / (positives.length * negatives.length);
}
export function fitSyntheticModel(includeNotes: boolean, options = { patients: syntheticPatients, features: featuresFor, target: targetFor }) {
  const { patients, features, target } = options;
  const eligible = patients.filter(p => target(p) !== null);
  const train = eligible.filter(p => p.partition === "train");
  const test = eligible.filter(p => p.partition === "test");
  const raw = train.map(p => features(p, includeNotes));
  const means = raw[0].map((_, j) => raw.reduce((sum, x) => sum + x[j], 0) / raw.length);
  const scales = means.map((mean, j) => Math.sqrt(raw.reduce((sum, x) => sum + (x[j] - mean) ** 2, 0) / raw.length) || 1);
  const vector = (p: SyntheticPatient) => [1, ...features(p, includeNotes).map((x, j) => (x - means[j]) / scales[j])];
  const weights = Array(means.length + 1).fill(0) as number[];
  const sigmoid = (z: number) => 1 / (1 + Math.exp(-Math.max(-30, Math.min(30, z))));
  const predict = (x: number[]) => sigmoid(x.reduce((sum, value, j) => sum + value * weights[j], 0));
  const vectors = train.map(vector);
  for (let step = 0; step < 700; step++) {
    const gradient = weights.map(() => 0);
    vectors.forEach((x, i) => { const error = predict(x) - target(train[i])!; x.forEach((value, j) => { gradient[j] += error * value / train.length; }); });
    weights.forEach((w, j) => { weights[j] -= .08 * (gradient[j] + (j ? .04 * w : 0)); });
  }
  const rows = test.map(p => ({ patient: p, probability: predict(vector(p)), target: target(p)! }));
  return { train, test, rows, weights, auc: aucFor(rows), excluded: patients.length - eligible.length, featureNames: ["Age", "Medication count", ...(includeNotes ? ["Latest recorded frequency", "Change in frequency", "Missing-frequency visits"] : [])] };
}
export function confusionFor(rows: { probability: number; target: number }[], threshold: number) {
  return rows.reduce((c, r) => { if (r.probability >= threshold) { if (r.target) c.tp++; else c.fp++; } else { if (r.target) c.fn++; else c.tn++; } return c; }, { tp: 0, fp: 0, fn: 0, tn: 0 });
}
