import { mergeFamilyHighlights } from "../letterHighlights";

function span(
  entity: string,
  start: number,
  end: number,
  label = `${entity}:${start}-${end}`
) {
  return { entity, start, end, label };
}

describe("mergeFamilyHighlights", () => {
  it("joins a split plural onto the same diagnosis phrase", () => {
    const letter = "Focal motor seizure s, (left arm jerks)";
    const seizure = letter.indexOf("Focal motor seizure");
    const plural = letter.indexOf(" s,") + 1;

    const merged = mergeFamilyHighlights(
      [
        span("Diagnosis", seizure, seizure + "Focal motor seizure".length),
        span("Diagnosis", plural, plural + 1),
      ],
      letter
    );

    expect(merged).toHaveLength(1);
    expect(merged[0]).toMatchObject({
      entity: "Diagnosis",
      start: seizure,
      end: plural + 1,
    });
    expect(letter.slice(merged[0].start, merged[0].end)).toBe(
      "Focal motor seizure s"
    );
  });

  it("joins an investigation heading to its finding across a tab", () => {
    const letter = "Investigations:\tCT Head 1/3/2015 gliosis";
    const heading = 0;
    const finding = letter.indexOf("CT Head");

    const merged = mergeFamilyHighlights(
      [
        span("Investigations", heading, "Investigations:".length),
        span("Investigations", finding, letter.length),
      ],
      letter
    );

    expect(merged).toHaveLength(1);
    expect(merged[0]).toMatchObject({
      entity: "Investigations",
      start: 0,
      end: letter.length,
    });
  });

  it("absorbs a nested short mention into the longer same-family run", () => {
    const letter = "Symptomatic structural epilepsy was diagnosed";
    const phrase = letter.indexOf("Symptomatic structural epilepsy");
    const nested = letter.indexOf("epilepsy");

    expect(
      mergeFamilyHighlights(
        [
          span(
            "Diagnosis",
            phrase,
            phrase + "Symptomatic structural epilepsy".length
          ),
          span("Diagnosis", nested, nested + "epilepsy".length),
        ],
        letter
      )
    ).toEqual([
      span(
        "Diagnosis",
        phrase,
        phrase + "Symptomatic structural epilepsy".length,
        "Diagnosis:0-31"
      ),
    ]);
  });

  it("does not merge different families or a non-whitespace gap", () => {
    const letter = "Focal motor seizures and 2-3 per month";
    const diagnosis = [0, "Focal motor seizures".length] as const;
    const frequency = [
      letter.indexOf("2-3 per month"),
      letter.length,
    ] as const;

    const merged = mergeFamilyHighlights(
      [
        span("Diagnosis", diagnosis[0], diagnosis[1]),
        span("SeizureFrequency", frequency[0], frequency[1]),
        span("Diagnosis", letter.indexOf("month"), letter.length),
      ],
      letter
    );

    expect(merged.map((item) => [item.entity, item.start, item.end])).toEqual([
      ["Diagnosis", diagnosis[0], diagnosis[1]],
      ["SeizureFrequency", frequency[0], frequency[1]],
      ["Diagnosis", letter.indexOf("month"), letter.length],
    ]);
  });
});
