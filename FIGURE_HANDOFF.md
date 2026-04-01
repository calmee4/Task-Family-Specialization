# Figure Handoff

Date: 2026-04-01

## Current Figure Set

1. `figures/figure_model_summary.pdf`
   - grouped official `Process` and `Result` counts by model
   - purpose: show that the open-8 cohort has low absolute success totals and multiple ties at `5/54`

2. `figures/figure_domain_summary.pdf`
   - domain-level paper-side rates aggregated from official `Process` and `Result`
   - purpose: show concentration in office/security/web/speech and zeros in image/video

3. `figures/figure_task_heatmap.pdf`
   - binary official `Result` heatmap over all tasks with at least one observed success
   - purpose: show that tied totals still hide task-family specialization

## What To Improve Next

- merge the model and domain panels into a more polished unified overview figure with consistent typography and annotated counts
- consider abbreviating long model names on-axis and moving the full names into the caption or appendix
- add direct callouts for the singleton wins:
  - `Trafilatura_01` on `Qwen__Qwen3-32B`
  - `Trafilatura_03` on `mistralai__Mistral-Small-3.1-24B-Instruct-2503`
- if space allows, add a compact fourth panel for `Process=True, Result=False` family counts
- if that panel is added, frame it as an official graded-but-unsuccessful regime, not as a fully resolved failure taxonomy

## Figure Design Direction

- keep the palette restrained and measurement-first, not hype-first
- prefer navy / slate / desaturated teal rather than bright benchmark-dashboard colors
- keep text labels legible in grayscale print
- annotate exact official counts where the story depends on small differences

## Reviewer-Facing Figure Story

- Figure 1 should answer: why is one global success rate insufficient?
- Figure 2 should answer: where does official success actually occur?
- Figure 3 should answer: do tied totals mean the same competence profile?
- Any added `Process=True, Result=False` panel should answer: what benchmark-visible middle state is hidden by a single pass rate?
