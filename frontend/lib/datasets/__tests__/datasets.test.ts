/**
 * Unit tests for the dataset kernel: descriptor validation and URL handling.
 */

import { DATASETS, DEFAULT_DATASET, datasetSupports, getDataset } from "../registry";
import { parseDatasetId, resolveDatasetId, surfaceHref, DATASET_PARAM } from "../url";
import { exectv2Dataset } from "../exectv2";
import {
  exectv2RuntimeAdapter,
  gan2026RuntimeAdapter,
  getRuntimeAdapter,
} from "../runtime";

function ids(items: Array<{ id: string }>): string[] {
  return items.map((i) => i.id);
}

describe("dataset descriptors", () => {
  it("both datasets declare supported surfaces", () => {
    expect(datasetSupports("gan2026", "workbench")).toBe(true);
    expect(datasetSupports("gan2026", "gold-audit")).toBe(true);

    expect(datasetSupports("exectv2", "workbench")).toBe(true);
    expect(datasetSupports("exectv2", "gold-audit")).toBe(true);
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
    const href = surfaceHref("workbench", "exectv2", { run: "r1", letter: "EA0002", empty: "" });
    const url = new URL(href, "http://x");
    expect(url.pathname).toBe("/workbench");
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
  it("maps each dataset id to a workbench explorer", () => {
    expect(getRuntimeAdapter("gan2026")).toBe(gan2026RuntimeAdapter);
    expect(getRuntimeAdapter("exectv2")).toBe(exectv2RuntimeAdapter);

    for (const adapter of [gan2026RuntimeAdapter, exectv2RuntimeAdapter]) {
      expect(adapter.surfaces.ExampleExplorer).toBeDefined();
    }
  });
});
