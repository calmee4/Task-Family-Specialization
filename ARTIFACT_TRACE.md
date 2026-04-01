# Artifact Trace

Date: 2026-04-01

## Benchmark Source

- benchmark root:
  - `workspace/external/agent_laws/GitTaskBench`
- official evaluator:
  - `workspace/external/agent_laws/GitTaskBench/gittaskbench/evaluator.py`
- official analyzer:
  - `workspace/external/agent_laws/GitTaskBench/gittaskbench/result_analyzer.py`

## Survey Command

```bash
python3 workspace/_codex/experiments/20260401_gittaskbench_official_metrics_survey.py
```

## Source Run Artifacts

- full open-8 comparable cohort:
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260401-open8gpu-fullbench-v4-gpu*/run_manifest.json`
- shared-task broader cohort:
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260331-gpt52-trafilatura-*/run_manifest.json`
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260331-gemini25-trafilatura-v*/run_manifest.json`
- targeted provider screen:
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260401-provider14-gpt5chat-openrouter/run_manifest.json`
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260401-provider14-gpt52-openrouter/run_manifest.json`
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260401-provider14-gemini25pro-openrouter/run_manifest.json`
- full-54 provider supplement:
  - `workspace/_codex/experiments/agent_law_gittaskbench_runs/20260401-gpt5chat-full54-modelhub/run_manifest.json`
  - `workspace/_codex/experiments/agent_law_gittaskbench_launches/20260401-gpt5chat-full54-modelhub/gpt5chat.log`

## Paper-Local Data Copies

- `data/20260401-gittaskbench-official-metrics.full_open8_rows.csv`
- `data/20260401-gittaskbench-official-metrics.full_open8_model_summary.csv`
- `data/20260401-gittaskbench-official-metrics.full_open8_family_summary.csv`
- `data/20260401-gittaskbench-official-metrics.full_open8_process_true_result_false.csv`
- `data/20260401-gittaskbench-official-metrics.shared_trafilatura_latest.csv`
- `data/20260401-gittaskbench-official-metrics.metadata.json`
- `data/20260401-gittaskbench-provider14-partial-official-metrics.rows.csv`
- `data/20260401-gittaskbench-provider14-partial-official-metrics.model_summary.csv`
- `data/20260401-gittaskbench-provider14-partial-official-metrics.task_summary.csv`
- `data/20260401-gittaskbench-provider14-official-metrics.rows.csv`
- `data/20260401-gittaskbench-provider14-official-metrics.model_summary.csv`
- `data/20260401-gittaskbench-provider14-official-metrics.task_summary.csv`
- `data/20260401-gpt5chat-full54-official-metrics.rows.csv`
- `data/20260401-gpt5chat-full54-official-metrics.model_summary.csv`
- `data/20260401-gpt5chat-full54-official-metrics.task_summary.csv`

## Table And Figure Build

```bash
python3 scripts/build_agent_metrics_assets.py
```

Generated assets:

- figures:
  - `figures/figure_model_summary.pdf`
  - `figures/figure_domain_summary.pdf`
  - `figures/figure_task_heatmap.pdf`
- tables:
  - `tables/model_summary.tex`
  - `tables/domain_summary.tex`
  - `tables/shared_trafilatura.tex`
  - `tables/provider_screen.tex`
  - `tables/provider_full54_domain.tex`

## Scope Notes

- All benchmark-facing numbers in the paper come from official GitTaskBench `Process` and `Result`.
- Any rates, heatmaps, and domain summaries are paper-side aggregates over those official outputs, not new benchmark metrics.
- The paper uses shortened model labels such as `Qwen3-32B` and `Mistral-Small-24B`; exact raw identifiers remain in the released CSV artifacts.
- In paper language, `Process=True` is interpreted conservatively as “the run advanced far enough to receive an official benchmark record.” It is not assumed to mean every row is a clean semantic near-miss.
- The shared `Trafilatura_01/02` slice keeps the latest local run per model-task pair from the recorded manifests; it is broader, but not a synchronized frontier rerun.
- The supplementary provider screen currently included in the paper is the completed three-model targeted 14-task provider launch:
  - `gpt-5-chat-2025-08-07`
  - `gpt-5.2-2025-12-11`
  - `gemini-2.5-pro-preview-06-05`
- Those rows are reported separately from the full open-8 cohort.
- The full-54 provider supplement currently included in the paper is:
  - `gpt-5-chat-2025-08-07`
- That run is also reported separately from both the full open-8 cohort and the targeted 14-task provider screen.
