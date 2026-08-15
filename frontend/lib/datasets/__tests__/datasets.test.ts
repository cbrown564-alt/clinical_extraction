/**
 * Unit tests for the dataset kernel: descriptor validation and URL handling.
 */

import { DATASETS, DEFAULT_DATASET, datasetSupports, getDataset } from "../registry";
import { parseDatasetId, resolveDatasetId, surfaceHref, DATASET_PARAM } from "../url";
import { exectv2Dataset } from "../exectv2";
import { gan2026Dataset } from "../gan2026";
import { filterBrowsableLetters, isBrowsableSplit } from "../splits";
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

  it("datasets only browse development letters", () => {
    expect(gan2026Dataset.splits).toEqual(["dev750"]);
    expect(exectv2Dataset.splits).toEqual(["dev140"]);
    expect(gan2026Dataset.defaultSplit).toBe("dev750");
    expect(exectv2Dataset.defaultSplit).toBe("dev140");
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

describe("browsable letter splits", () => {
  it("keeps only Gan dev750 and ExECT dev140 aliases", () => {
    expect(isBrowsableSplit("dev750")).toBe(true);
    expect(isBrowsableSplit("dev140")).toBe(true);
    expect(isBrowsableSplit("validation")).toBe(true);
    expect(isBrowsableSplit("dev")).toBe(true);
    expect(isBrowsableSplit("test60")).toBe(false);
    expect(isBrowsableSplit("test450")).toBe(false);
    expect(isBrowsableSplit("test")).toBe(false);
    expect(isBrowsableSplit("full200")).toBe(false);
  });

  it("drops holdout letters from mixed catalogs", () => {
    expect(
      filterBrowsableLetters([
        { id: "10", split: "dev750" },
        { id: "31", split: "test450" },
        { id: "EA0002", split: "dev140" },
        { id: "EA0001", split: "test60" },
      ]).map((letter) => letter.id)
    ).toEqual(["10", "EA0002"]);
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
