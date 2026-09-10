import { emergencyPatients, emergencyFeatures, fitEmergencyModel, generateEmergencyPatients, reviewAtCapacity } from "../emergencyRisk";

describe("emergency-care teaching simulation", () => {
  it("preserves evidence consistency and excludes future outcomes from inputs", () => {
    expect(generateEmergencyPatients()).toEqual(emergencyPatients);
    for (const p of emergencyPatients) {
      const changed = { ...p, emergencyOutcome: 1, visits: p.visits.map(v => v.month > 6 ? { ...v, rate: 999 } : v) };
      expect(emergencyFeatures(changed, true)).toEqual(emergencyFeatures(p, true));
      const rate = p.visits.find(v => v.month === 6)!.rate;
      if (rate !== null && p.tonicClonic !== null) expect(p.tonicClonic).toBeLessThanOrEqual(rate * 3);
      if (p.tonicClonic === null) expect(p.riskNote).toContain("frequency was not documented");
      if (p.adherenceConcern === null) expect(p.riskNote).toContain("not discussed");
    }
  });
  it("uses identical disjoint partitions and handles zero/full review capacity", () => {
    const a = fitEmergencyModel(false), b = fitEmergencyModel(true);
    expect(a.test.map(p => p.id)).toEqual(b.test.map(p => p.id));
    expect(a.train.map(p => p.id)).toEqual(b.train.map(p => p.id));
    expect(a.train.some(p => a.test.some(t => p.id === t.id))).toBe(false);
    expect(a.excluded).toBe(emergencyPatients.filter(p => p.emergencyOutcome === null).length);
    for (const model of [a, b]) {
      expect(model.rows.every(r => Number.isFinite(r.probability))).toBe(true);
      const none = reviewAtCapacity(model.rows, 0), all = reviewAtCapacity(model.rows, model.rows.length);
      expect(none.selected).toHaveLength(0);
      expect(all.missed).toBe(0);
      expect(all.captured).toBe(none.missed);
      expect(all.captured + all.withoutEvent).toBe(model.rows.length);
    }
  });
});
