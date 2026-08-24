import { ganRecord } from "../../_mock";
import { proxyPython } from "../../_upstream";

export const dynamic = "force-static";

export async function POST(request: Request) {
  const raw = await request.text();
  const upstream = await proxyPython("/run/note", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: raw,
  });
  if (upstream) return upstream;
  const body = JSON.parse(raw) as {
    source_row_index?: number;
    gold_label?: string;
  };
  const sourceRowIndex = body.source_row_index ?? 0;
  const record = ganRecord(String(sourceRowIndex));
  const goldLabel = body.gold_label ?? String(record?.gold_label ?? "unknown");
  const evidence = String(record?.gold_reference ?? goldLabel);
  const eventId = `mock-${sourceRowIndex}`;
  return Response.json({
    pipeline: "rules",
    source_row_index: sourceRowIndex,
    gold_label: goldLabel,
    result: {
      output: {
        final_value: goldLabel,
        rationale: "Static demonstration fixture; deterministic result replayed from the bundled record.",
        evidence,
      },
      diagnostics: {
        candidate_events: [
          {
            event_id: eventId,
            kind: "frequency",
            raw_value: goldLabel,
            evidence,
            start_char: null,
            end_char: null,
            rule_id: "mock_fixture",
            rule_group: "mock",
            portability: "portable",
            match_groups: {},
          },
        ],
        normalized_events: [
          {
            event_id: eventId,
            normalized_label: goldLabel,
            semantic_kind: "frequency",
            monthly_frequency: 0,
            validation_errors: [],
          },
        ],
        final_selection: {
          final_label: goldLabel,
          rationale: "Static demonstration fixture.",
          evidence,
          selected_event_ids: [eventId],
        },
        evidence_valid: true,
      },
    },
  });
}
