"use client";

import { useEffect, useCallback, useMemo } from "react";
import { useSearchParams } from "next/navigation";
import {
  FileText,
  AlertCircle,
} from "lucide-react";
import { useArchitectStore } from "@/lib/stores";
import {
  useLetters,
  useLetter,
  usePipelineFamilies,
  useRunNote,
} from "@/lib/hooks";
import { fetchRegistry, fetchArtifact, fetchLetter } from "@/lib/api";
import { firstReplayableArtifactPath } from "@/lib/registryArtifacts";
import { adaptDeterministicTrace, adaptTrace, isReplaySupported } from "@/lib/traceAdapter";
import {
  ganOverallScore,
  ganPipelineOptionLabel,
  groupGanPipelineOptions,
  isGanAggregateRunId,
  resolveGanPipelineOption,
} from "@/lib/ganPipelineOptions";
import {
  ControlBar,
  ControlField,
  ControlCombobox,
  LetterPicker,
  MethodBadge,
  MetricChips,
} from "@/components/surface";

function isDeterministicFamily(family: string): boolean {
  return family === "rules" || family === "rules_only" || family.includes("deterministic");
}

function isLiveFamily(family: string): boolean {
  return isDeterministicFamily(family);
}

export default function TraceControls() {
  const searchParams = useSearchParams();
  const requestedRunId = searchParams.get("run");
  const {
    noteText,
    split,
    sourceRowIndex,
    selectedRunId,
    pipelineFamily,
    ablationConfig,
    replayRunId,
    setNoteText,
    setSourceRowIndex,
    setSelectedRunId,
    setTrace,
    setIsLoading,
    setError,
    setReplayRunId,
    setReplayArtifactRows,
    setReplayRowIndex,
  } = useArchitectStore();

  const runNote = useRunNote();
  const lettersQuery = useLetters("gan2026");
  const recordQuery = useLetter(
    "gan2026",
    sourceRowIndex === null ? null : String(sourceRowIndex)
  );
  const familiesQuery = usePipelineFamilies();

  const pipelineOptions = useMemo(
    () => familiesQuery.data?.families ?? [],
    [familiesQuery.data?.families]
  );
  const pipelineGroups = useMemo(
    () => groupGanPipelineOptions(pipelineOptions),
    [pipelineOptions]
  );
  const selectedOption = useMemo(
    () => pipelineOptions.find((option) => option.run_id === selectedRunId),
    [pipelineOptions, selectedRunId]
  );
  const isAggregateOnly =
    selectedOption?.availability === "aggregate_only" ||
    isGanAggregateRunId(selectedRunId);
  const isLive = isLiveFamily(pipelineFamily);
  const isReplay = !isLive && !isAggregateOnly;
  const overallScore = useMemo(
    () => ganOverallScore(selectedOption),
    [selectedOption]
  );

  // When dataset record loads, update note text
  useEffect(() => {
    if (recordQuery.data?.note_text) {
      setNoteText(recordQuery.data.note_text);
    }
  }, [recordQuery.data, setNoteText]);

  // Restore an exact run from the URL once the Gan comparison catalog arrives.
  useEffect(() => {
    if (pipelineOptions.length === 0) return;
    const requestedOption = pipelineOptions.find(
      (option) => option.run_id === requestedRunId
    );
    if (!requestedOption) return;
    const current = useArchitectStore.getState();
    if (
      requestedOption.run_id !== current.selectedRunId ||
      requestedOption.pipeline_family !== current.pipelineFamily
    ) {
      setSelectedRunId(requestedOption.run_id, requestedOption.pipeline_family);
    }
  }, [pipelineOptions, requestedRunId, setSelectedRunId]);

  // Keep adapter family aligned, or fall back from a legacy registry run id.
  useEffect(() => {
    if (pipelineOptions.length === 0) return;
    if (pipelineOptions.some((option) => option.run_id === requestedRunId)) return;
    const option = resolveGanPipelineOption(pipelineOptions, selectedRunId);
    if (
      option &&
      (option.run_id !== selectedRunId || option.pipeline_family !== pipelineFamily)
    ) {
      setSelectedRunId(option.run_id, option.pipeline_family);
    }
  }, [pipelineOptions, pipelineFamily, requestedRunId, selectedRunId, setSelectedRunId]);

  const loadReplayLetter = useCallback(
    async (letterIndex: number) => {
      setIsLoading(true);
      setError(null);
      try {
        const registry = await fetchRegistry();
        const matchingRun = registry.runs.find((r) => r.run_id === selectedRunId);
        if (!matchingRun) {
          setError(`No replay artifact found for ${selectedRunId}`);
          return;
        }
        const replayPath = firstReplayableArtifactPath(matchingRun.artifact_paths);
        if (!replayPath) {
          setError(`No replay artifact found for ${selectedRunId}`);
          return;
        }
        const [record, artifact] = await Promise.all([
          fetchLetter("gan2026", String(letterIndex)),
          fetchArtifact(matchingRun.run_id, replayPath, undefined, String(letterIndex)),
        ]);
        const row = artifact.content[0];
        if (!row) {
          setError(`No replay row for letter ${letterIndex}`);
          return;
        }
        setNoteText(record.note_text);
        setSourceRowIndex(letterIndex);
        setReplayRunId(matchingRun.run_id);
        setReplayArtifactRows([row]);
        setReplayRowIndex(0);
        if (!isReplaySupported(pipelineFamily)) {
          setError(
            `Replay not yet supported for ${pipelineFamily}. The artifact format for this family is not yet mapped to the trace viewer.`
          );
          return;
        }
        setTrace(adaptTrace(row, pipelineFamily, record));
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load replay letter");
      } finally {
        setIsLoading(false);
      }
    },
    [
      pipelineFamily,
      selectedRunId,
      setError,
      setIsLoading,
      setNoteText,
      setReplayArtifactRows,
      setReplayRowIndex,
      setReplayRunId,
      setSourceRowIndex,
      setTrace,
    ]
  );

  const handleRun = useCallback(() => {
    if (!noteText.trim()) return;
    if (!isLiveFamily(pipelineFamily)) return;

    setIsLoading(true);
    setError(null);
    runNote.mutate(
      {
        note_text: noteText,
        pipeline: pipelineFamily,
        source_row_index: sourceRowIndex ?? 0,
        gold_label: recordQuery.data?.gold_label,
        ablation_config: ablationConfig,
      },
      {
        onSuccess: (data) => {
          const trace = adaptDeterministicTrace(
            data,
            noteText,
            sourceRowIndex ?? 0,
            split ?? "validation"
          );
          setTrace(trace);
          setIsLoading(false);
        },
        onError: (e) => {
          setError(e instanceof Error ? e.message : "Run failed");
          setIsLoading(false);
        },
      }
    );
  }, [
    noteText,
    pipelineFamily,
    sourceRowIndex,
    split,
    ablationConfig,
    recordQuery.data,
    runNote,
    setTrace,
    setIsLoading,
    setError,
  ]);

  const isLoading = useArchitectStore((s) => s.isLoading);
  const error = useArchitectStore((s) => s.error);
  const trace = useArchitectStore((s) => s.trace);

  // Auto-run when live specimen changes or is loaded initially
  useEffect(() => {
    if (isLive && noteText && recordQuery.data && !isLoading) {
      // Check if the current trace matches the selected index and split
      const currentTraceMatches = trace && trace.sourceRowIndex === sourceRowIndex && trace.split === (split ?? "validation") && trace.noteText === noteText;
      if (!currentTraceMatches) {
        handleRun();
      }
    }
  }, [isLive, noteText, recordQuery.data, sourceRowIndex, split, handleRun, trace, isLoading]);

  useEffect(() => {
    if (!isReplay || sourceRowIndex === null || isAggregateOnly) return;
    const currentTraceMatches =
      Boolean(trace) &&
      replayRunId === selectedRunId &&
      trace?.sourceRowIndex === sourceRowIndex;
    if (currentTraceMatches || isLoading) return;
    void loadReplayLetter(sourceRowIndex);
  }, [
    isAggregateOnly,
    isLoading,
    isReplay,
    loadReplayLetter,
    replayRunId,
    selectedRunId,
    sourceRowIndex,
    trace,
  ]);

  const letterItems = useMemo(
    () =>
      lettersQuery.data?.letters.map((letter) => ({
        value: String(letter.id),
        label: `${letter.id} · ${letter.label}`,
      })) ?? [],
    [lettersQuery.data]
  );

  const methodItems = useMemo(
    () =>
      pipelineGroups.flatMap((group) =>
        group.options.map((opt) => ({
          value: opt.run_id,
          label:
            ganPipelineOptionLabel(opt.label) +
            (opt.availability === "aggregate_only"
              ? " · aggregate only"
              : opt.availability === "not_retained"
                ? " · not retained"
                : ""),
          group: group.label,
          disabled: opt.availability === "not_retained",
        }))
      ),
    [pipelineGroups]
  );

  return (
    <ControlBar
      left={
        <>
          {/* Method selection on the far left */}
          <ControlField label="Method" htmlFor="architect-method-select">
            {selectedOption?.kind && (
              <MethodBadge method={selectedOption.kind} />
            )}
            <ControlCombobox
              id="architect-method-select"
              noun="method"
              className="min-w-0 flex-1 sm:min-w-[240px] sm:flex-none"
              items={methodItems}
              value={selectedRunId}
              onChange={(runId) => {
                const option = pipelineOptions.find((opt) => opt.run_id === runId);
                if (option) {
                  setSelectedRunId(option.run_id, option.pipeline_family);
                }
              }}
            />
          </ControlField>

          {!isAggregateOnly && (
            <ControlField label="Letter" htmlFor="architect-row-select" icon={<FileText className="h-3 w-3 text-muted" />}>
              <LetterPicker
                id="architect-row-select"
                items={letterItems}
                value={sourceRowIndex === null ? "" : String(sourceRowIndex)}
                onChange={(next) =>
                  setSourceRowIndex(next ? parseInt(next, 10) : null)
                }
                disabled={!lettersQuery.data}
                placeholder="Letter…"
                className="min-w-0 flex-1 sm:min-w-[200px] sm:flex-none"
              />
            </ControlField>
          )}
        </>
      }
      right={
        <div className="flex flex-wrap items-center gap-2">
          {/* Error */}
          {error && (
            <div className="flex items-center gap-1 rounded-md border border-error/20 bg-error/5 px-2 py-1 text-xs text-error max-w-xs truncate shrink-0">
              <AlertCircle className="h-3 w-3 shrink-0" />
              <span className="truncate">{error}</span>
            </div>
          )}

          {overallScore !== null && overallScore !== undefined && (
            <MetricChips
              chips={[
                {
                  label: "Overall",
                  value: overallScore,
                  format: "f1",
                  shade: true,
                },
              ]}
            />
          )}
        </div>
      }
    />
  );
}
