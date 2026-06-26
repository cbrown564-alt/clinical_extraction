/**
 * Unit tests for the dataset kernel: descriptor validation, URL handling, and
 * the ExECTv2 error/component adapters.
 */

import { DATASETS, DEFAULT_DATASET, datasetSupports, getDataset } from "../registry";
import { parseDatasetId, resolveDatasetId, surfaceHref, DATASET_PARAM } from "../url";
import { exectv2Dataset } from "../exectv2";
import {
  exectv2RuntimeAdapter,
  gan2026RuntimeAdapter,
  getRuntimeAdapter,
} from "../runtime";
import { deriveLetterErrors, summarizeErrors } from "../adapters/exectv2Errors";
import { classifyComponentOwner, summarizeComponents } from "../adapters/exectv2Components";
import type { Exectv2LetterRecord, Exectv2Mention, Exectv2RunSummary } from "../../types";

function ids(items: Array<{ id: string }>): string[] {
  return items.map((i) => i.id);
}

describe("dataset descriptors", () => {
  it("both datasets declare all four surfaces", () => {
    for (const dataset of DATASETS) {
      expect(datasetSupports(dataset.id, "workbench")).toBe(true);
      expect(datasetSupports(dataset.id, "observatory")).toBe(true);
      expect(datasetSupports(dataset.id, "laboratory")).toBe(true);
      expect(datasetSupports(dataset.id, "gallery")).toBe(true);
    }
  });

  it("metric, component, and error class ids are unique and non-empty per dataset", () => {
    for (const dataset of DATASETS) {
      for (const group of [dataset.metrics, dataset.componentTypes, dataset.errorClasses]) {
        const idList = ids(group);
        expect(idList.every((id) => id.length > 0)).toBe(true);
        expect(new Set(idList).size).toBe(idList.length);
      }
    }
  });

  it("exectv2 owns the four key-finding families and is not coerced into Gan categories", () => {
    expect(exectv2Dataset.families.map((f) => f.id)).toEqual([
      "Diagnosis",
      "SeizureFrequency",
      "Prescription",
      "Investigations",
    ]);
    expect(exectv2Dataset.specimenLabel).toBe("letter");
  });
});

describe("dataset url handling", () => {
  it("parses known ids and rejects unknown ones", () => {
    expect(parseDatasetId("exectv2")).toBe("exectv2");
    expect(parseDatasetId("gan2026")).toBe("gan2026");
    expect(parseDatasetId("nonsense")).toBeNull();
    expect(parseDatasetId(null)).toBeNull();
  });

  it("resolves bare values to the default dataset (Gan back-compat)", () => {
    expect(resolveDatasetId(null)).toBe(DEFAULT_DATASET);
    expect(resolveDatasetId(undefined)).toBe(DEFAULT_DATASET);
    expect(DEFAULT_DATASET).toBe("gan2026");
  });

  it("surfaceHref always carries the dataset plus extra selectors", () => {
    const href = surfaceHref("gallery", "exectv2", { run: "r1", letter: "EA0002", empty: "" });
    const url = new URL(href, "http://x");
    expect(url.pathname).toBe("/gallery");
    expect(url.searchParams.get(DATASET_PARAM)).toBe("exectv2");
    expect(url.searchParams.get("run")).toBe("r1");
    expect(url.searchParams.get("letter")).toBe("EA0002");
    expect(url.searchParams.has("empty")).toBe(false);
  });

  it("getDataset falls back to the default for unknown ids", () => {
    // @ts-expect-error intentional invalid id
    expect(getDataset("bogus").id).toBe(DEFAULT_DATASET);
  });
});

describe("dataset runtime adapters", () => {
  it("maps each dataset id to a runtime adapter with four surfaces", () => {
    expect(getRuntimeAdapter("gan2026")).toBe(gan2026RuntimeAdapter);
    expect(getRuntimeAdapter("exectv2")).toBe(exectv2RuntimeAdapter);

    for (const adapter of [gan2026RuntimeAdapter, exectv2RuntimeAdapter]) {
      expect(adapter.surfaces.ErrorGallery).toBeDefined();
      expect(adapter.surfaces.AggregatePerformance).toBeDefined();
      expect(adapter.surfaces.ComponentImpact).toBeDefined();
      expect(adapter.surfaces.ExampleExplorer).toBeDefined();
      expect(typeof adapter.useRunCatalog).toBe("function");
      expect(typeof adapter.useRunSelection).toBe("function");
    }
  });
});

// ── Fixtures ──────────────────────────────────────────────────────────

function mention(partial: Partial<Exectv2Mention> & { entity: string; text: string }): Exectv2Mention {
  return {
    id: `${partial.entity}:${partial.text}`,
    source: "predicted",
    evidence: partial.text,
    evidence_valid: true,
    component_owner: "",
    source_lane: "",
    source_model: "",
    confidence: "",
    assertion: "",
    attributes: {},
    status: "predicted",
    headline_status: "",
    ...partial,
  };
}

function syntheticLetter(): Exectv2LetterRecord {
  return {
    letter_id: "EA9999",
    split: "dev",
    stage: "dev140",
    letter_text: "synthetic",
    gold_mentions: [
      mention({ entity: "Diagnosis", text: "focal epilepsy", source: "gold", attributes: { CUI: "C1" } }),
      mention({ entity: "SeizureFrequency", text: "weekly", source: "gold" }),
      mention({ entity: "Prescription", text: "lamotrigine", source: "gold", attributes: { CUI: "D1", Negation: "Affirmed" } }),
      mention({ entity: "Investigations", text: "MRI brain", source: "gold" }),
    ],
    predicted_mentions: [
      // exact match → no error
      mention({ entity: "Diagnosis", text: "focal epilepsy", attributes: { CUI: "C1" }, component_owner: "hybrid_diagnosis_route", source_lane: "focused_diagnosis_reconciler_v01" }),
      // false positive (no gold "daily")
      mention({ entity: "SeizureFrequency", text: "daily", component_owner: "hybrid_sf_route+deterministic_union_arbitration", source_lane: "focused_sf_union_arbitration_v08" }),
      // attribute mismatch (CUI differs)
      mention({ entity: "Prescription", text: "lamotrigine", attributes: { CUI: "D2", Negation: "Affirmed" }, component_owner: "deterministic_prescription_repair_v03" }),
      // evidence invalid
      mention({ entity: "Investigations", text: "MRI brain", evidence_valid: false, component_owner: "llm_investigations_verifier" }),
    ],
    family_counts: {
      gold: { Diagnosis: 1, SeizureFrequency: 1, Prescription: 1, Investigations: 1 },
      predicted: { Diagnosis: 1, SeizureFrequency: 1, Prescription: 1, Investigations: 1 },
    },
    evidence_spans: [],
  };
}

describe("exectv2 error adapter", () => {
  const rows = deriveLetterErrors("run-x", syntheticLetter());

  it("produces one error of each derivable class and skips the exact match", () => {
    const summary = summarizeErrors(rows);
    expect(summary.byClass.false_positive).toBe(1);
    expect(summary.byClass.false_negative).toBe(1); // gold "weekly" unmatched
    expect(summary.byClass.attribute_mismatch).toBe(1);
    expect(summary.byClass.evidence_invalid).toBe(1);
    expect(summary.total).toBe(4);
  });

  it("attributes the CUI mismatch detail and the owning component", () => {
    const attr = rows.find((r) => r.errorClass === "attribute_mismatch");
    expect(attr?.family).toBe("Prescription");
    expect(attr?.detail).toContain("CUI D1 → D2");
    expect(attr?.componentOwner).toBe("deterministic_prescription_repair_v03");
  });

  it("false negatives carry the gold text and no prediction", () => {
    const fn = rows.find((r) => r.errorClass === "false_negative");
    expect(fn?.goldText).toBe("weekly");
    expect(fn?.predictedText).toBeNull();
  });
});

describe("exectv2 component adapter", () => {
  it("classifies owners into component types by provenance keyword", () => {
    expect(classifyComponentOwner("hybrid_diagnosis_route")).toBe("llm_producer");
    expect(classifyComponentOwner("deterministic_prescription_repair_v03")).toBe("dictionary");
    expect(classifyComponentOwner("llm_investigations_verifier")).toBe("evidence_validation");
    expect(classifyComponentOwner("deterministic_union_arbitration")).toBe("assembler");
  });

  it("splits compound owners and tallies per-family contributions", () => {
    const run = {
      run_id: "run-x",
      letters: [syntheticLetter()],
      metrics: { families: {} },
    } as unknown as Exectv2RunSummary;
    const components = summarizeComponents(run);
    const owners = components.map((c) => c.owner);
    // compound "hybrid_sf_route+deterministic_union_arbitration" split into two
    expect(owners).toContain("hybrid_sf_route");
    expect(owners).toContain("deterministic_union_arbitration");
    const repair = components.find((c) => c.owner === "deterministic_prescription_repair_v03");
    expect(repair?.deterministic).toBe(true);
    expect(repair?.byFamily.Prescription).toBe(1);
  });
});
