import { aucFor, confusionFor, featuresFor, fitSyntheticModel, generatePatients, stateFor, syntheticPatients, targetFor } from "../syntheticPatients";

describe("fictional application dataset", () => {
  it("retains reproducible patient linkage, exact authored evidence and unknown states", () => {
    expect(generatePatients()).toEqual(syntheticPatients);
    expect(new Set(syntheticPatients.map(p => p.id)).size).toBe(72);
    for (const patient of syntheticPatients) {
      expect(patient.visits.map(v => v.month)).toEqual([0, 3, 6, 9, 12]);
      for (const v of patient.visits) {
        expect(v.note).toContain(v.evidence);
        expect(v.id).toBe(`${patient.id}-M${v.month}`);
        if (v.rate === null) expect(stateFor(v.rate)).toBe("Unknown");
      }
    }
    expect(stateFor(0)).toBe("Seizure free");
  });
  it("keeps future documentation out of predictive features", () => {
    for (const patient of syntheticPatients) {
      const changed = { ...patient, visits: patient.visits.map(v => v.month > 6 ? { ...v, rate: 999, note: "Future outcome" } : v) };
      expect(featuresFor(changed, true)).toEqual(featuresFor(patient, true));
      expect(featuresFor(changed, false)).toEqual(featuresFor(patient, false));
    }
  });
  it("compares models on the same patients without overlap or unknown targets", () => {
    const a = fitSyntheticModel(false), b = fitSyntheticModel(true);
    expect(a.train.map(p => p.id)).toEqual(b.train.map(p => p.id));
    expect(a.test.map(p => p.id)).toEqual(b.test.map(p => p.id));
    const trainingIds = new Set(a.train.map(p => p.id));
    expect(a.test.some(p => trainingIds.has(p.id))).toBe(false);
    expect([...a.train, ...a.test].every(p => targetFor(p) !== null)).toBe(true);
    expect(a.train.length + a.test.length + a.excluded).toBe(72);
    for (const model of [a, b]) {
      expect(model.rows.every(r => Number.isFinite(r.probability) && r.probability > 0 && r.probability < 1)).toBe(true);
      const c = confusionFor(model.rows, .5);
      expect(c.tp + c.fp + c.fn + c.tn).toBe(model.test.length);
    }
  });
  it("handles tied predictions and thresholds without overstating discrimination", () => {
    const rows = [{ probability: .5, target: 1 }, { probability: .5, target: 0 }];
    expect(aucFor(rows)).toBe(.5);
    expect(aucFor([{ probability: .9, target: 1 }])).toBeNull();
    expect(confusionFor(rows, .5)).toEqual({ tp: 1, fp: 1, fn: 0, tn: 0 });
    expect(confusionFor(rows, .6)).toEqual({ tp: 0, fp: 0, fn: 1, tn: 1 });
  });
});
