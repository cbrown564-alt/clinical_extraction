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
  DEMO_GAN_RUN_ID,
  DEMO_MODEL_LABEL,
  demoMethodLabel,
  isDemoSurface,
  lockDemoGanFamilies,
} from "@/lib/demoSurface";
import {
  ganMethodChoices,
  ganMethodRequiresModel,
  ganModelsForMethod,
  ganOverallScore,
  ganPickerMethodId,
  ganPipelineOptionLabel,
  isGanAggregateRunId,
  isGanRulesRunId,
  paperGanFamilies,
  resolveGanMethodModel,
  resolveGanPipelineOption,
} from "@/lib/ganPipelineOptions";
import { isPaperCellId } from "@/lib/paperCells";
import {
  ControlBar,
  ControlField,
  ControlCombobox,
  ControlFixedValue,
  LetterPicker,
  MetricChips,
} from "@/components/surface";

function isDeterministicFamily(family: string): boolean {
  return isGanRulesRunId(family) || family.includes("deterministic");
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

  const demoLocked = isDemoSurface();
  const pipelineOptions = useMemo(() => {
    const families = paperGanFamilies(familiesQuery.data?.families ?? []);
    return demoLocked ? lockDemoGanFamilies(families) : families;
  }, [demoLocked, familiesQuery.data?.families]);
  const methodChoices = useMemo(
    () => ganMethodChoices(pipelineOptions),
    [pipelineOptions]
  );
  const selectedOption = useMemo(
    () => pipelineOptions.find((option) => option.run_id === selectedRunId),
    [pipelineOptions, selectedRunId]
  );
  const selectedMethodId = selectedOption
    ? ganPickerMethodId(selectedOption)
    : "llm_extract";
  const modelOptions = useMemo(
    () => ganModelsForMethod(pipelineOptions, selectedMethodId),
    [pipelineOptions, selectedMethodId]
  );
  const isAggregateOnly =
    selectedOption?.availability === "aggregate_only" ||
    isGanAggregateRunId(selectedRunId);
  const isLive =
    isLiveFamily(pipelineFamily) || isGanRulesRunId(selectedRunId);
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
    if (demoLocked) {
      const locked =
        resolveGanPipelineOption(pipelineOptions, DEMO_GAN_RUN_ID) ??
        pipelineOptions[0];
      if (
        locked &&
        (locked.run_id !== selectedRunId ||
          locked.pipeline_family !== pipelineFamily)
      ) {
        setSelectedRunId(locked.run_id, locked.pipeline_family);
      }
      return;
    }
    const requestedOption = resolveGanPipelineOption(
      pipelineOptions,
      requestedRunId ?? ""
    );
    if (!requestedOption || !isPaperCellId(ganPickerMethodId(requestedOption))) {
      return;
    }
    const current = useArchitectStore.getState();
    if (
      requestedOption.run_id !== current.selectedRunId ||
      requestedOption.pipeline_family !== current.pipelineFamily
    ) {
      setSelectedRunId(requestedOption.run_id, requestedOption.pipeline_family);
    }
  }, [
    demoLocked,
    pipelineFamily,
    pipelineOptions,
    requestedRunId,
    selectedRunId,
    setSelectedRunId,
  ]);

  // Keep adapter family aligned, or fall back from a legacy registry run id.
  useEffect(() => {
    if (pipelineOptions.length === 0) return;
    if (demoLocked) return;
    if (
      requestedRunId &&
      resolveGanPipelineOption(pipelineOptions, requestedRunId)
    ) {
      return;
    }
    const option = resolveGanPipelineOption(pipelineOptions, selectedRunId);
    const selectedIsPaper =
      option !== undefined && isPaperCellId(ganPickerMethodId(option));
    const next = selectedIsPaper
      ? option
      : resolveGanMethodModel(pipelineOptions, "llm_extract") ??
        resolveGanMethodModel(pipelineOptions, "rules_only");
    if (
      next &&
      (next.run_id !== selectedRunId || next.pipeline_family !== pipelineFamily)
    ) {
      setSelectedRunId(next.run_id, next.pipeline_family);
    }
  }, [
    demoLocked,
    pipelineOptions,
    pipelineFamily,
    requestedRunId,
    selectedRunId,
    setSelectedRunId,
  ]);

  const loadReplayLetter = useCallback(
    async (letterIndex: number) => {
      setIsLoading(true);
      setError(null);
      try {
        const registry = await fetchRegistry();
        const matchingRun = registry.runs.find((r) => r.run_id === selectedRunId);
        const replayPath = firstReplayableArtifactPath(matchingRun?.artifact_paths);
        const [record, artifact] = await Promise.all([
          fetchLetter("gan2026", String(letterIndex)),
          fetchArtifact(selectedRunId, replayPath, undefined, String(letterIndex)),
        ]);
        const row = artifact.content[0];
        if (!row) {
          setError(`No replay row for letter ${letterIndex}`);
          return;
        }
        setNoteText(record.note_text);
        setSourceRowIndex(letterIndex);
        setReplayRunId(selectedRunId);
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
    const liveRules = isLiveFamily(pipelineFamily) || isGanRulesRunId(selectedRunId);
    if (!liveRules) return;

    setIsLoading(true);
    setError(null);
    runNote.mutate(
      {
        note_text: noteText,
        pipeline: isGanRulesRunId(selectedRunId) ? "rules" : pipelineFamily,
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
    selectedRunId,
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
      methodChoices.map((method) => ({
        value: method.id,
        label: method.label,
      })),
    [methodChoices]
  );
  const modelItems = useMemo(
    () =>
      modelOptions.map((opt) => ({
        value: opt.model ?? opt.run_id,
        label:
          ganPipelineOptionLabel(opt.model_label ?? opt.label) +
          (opt.availability === "aggregate_only"
            ? " · aggregate only"
            : opt.availability === "not_retained"
              ? " · not retained"
              : ""),
        disabled: opt.availability === "not_retained",
      })),
    [modelOptions]
  );

  return (
    <ControlBar
      left={
        <>
          <ControlField label="Method">
            {demoLocked ? (
              <ControlFixedValue className="min-w-0 flex-1 sm:min-w-[220px] sm:flex-none">
                {demoMethodLabel()}
              </ControlFixedValue>
            ) : (
              <ControlCombobox
                id="architect-method-select"
                noun="method"
                className="min-w-0 flex-1 sm:min-w-[220px] sm:flex-none"
                items={methodItems}
                value={selectedMethodId}
                onChange={(methodId) => {
                  const option = resolveGanMethodModel(
                    pipelineOptions,
                    methodId,
                    selectedOption?.model
                  );
                  if (option) {
                    setSelectedRunId(option.run_id, option.pipeline_family);
                  }
                }}
              />
            )}
          </ControlField>

          {ganMethodRequiresModel(selectedMethodId) && (
            <ControlField label="Model">
              {demoLocked ? (
                <ControlFixedValue className="min-w-0 flex-1 sm:min-w-[200px] sm:flex-none">
                  {DEMO_MODEL_LABEL}
                </ControlFixedValue>
              ) : (
                <ControlCombobox
                  id="architect-model-select"
                  noun="model"
                  className="min-w-0 flex-1 sm:min-w-[200px] sm:flex-none"
                  items={modelItems}
                  value={selectedOption?.model ?? ""}
                  onChange={(model) => {
                    const option = resolveGanMethodModel(
                      pipelineOptions,
                      selectedMethodId,
                      model
                    );
                    if (option) {
                      setSelectedRunId(option.run_id, option.pipeline_family);
                    }
                  }}
                />
              )}
            </ControlField>
          )}

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
