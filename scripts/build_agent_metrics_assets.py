#!/usr/bin/env python3

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIGURES = ROOT / "figures"
TABLES = ROOT / "tables"

MODEL_CSV = DATA / "20260401-gittaskbench-official-metrics.full_open8_model_summary.csv"
ROWS_CSV = DATA / "20260401-gittaskbench-official-metrics.full_open8_rows.csv"
SHARED_CSV = DATA / "20260401-gittaskbench-official-metrics.shared_trafilatura_latest.csv"
PROVIDER14_ROWS_CSV = DATA / "20260401-gittaskbench-provider14-official-metrics.rows.csv"
PROVIDER14_MODEL_CSV = DATA / "20260401-gittaskbench-provider14-official-metrics.model_summary.csv"
PROVIDER14_ROWS_FALLBACK_CSV = DATA / "20260401-gittaskbench-provider14-partial-official-metrics.rows.csv"
PROVIDER14_MODEL_FALLBACK_CSV = DATA / "20260401-gittaskbench-provider14-partial-official-metrics.model_summary.csv"
PROVIDER54_MODEL_CSVS = [
    DATA / "20260401-gpt5chat-full54-official-metrics.model_summary.csv",
    DATA / "20260401-gpt52-full54-official-metrics.model_summary.csv",
    DATA / "20260401-gemini25pro-full54-official-metrics.model_summary.csv",
]

FAMILY_TO_DOMAIN = {
    "AnimeGANv3": "Image",
    "DeOldify": "Image",
    "DeScratch": "Image",
    "StyleTransfer": "Image",
    "SuperResolution": "Image",
    "TransparentBackground": "Image",
    "VideoPose3D": "Video",
    "FunASR": "Speech",
    "SpeechBrain": "Speech",
    "NeuroKit": "Physio",
    "Faker": "Security",
    "InvisibleWatermark": "Security",
    "Stegano": "Security",
    "Trafilatura": "Web",
    "Scrapy": "Web",
    "Eparse": "Office",
    "PDFPlumber": "Office",
    "PyPDF2": "Office",
}

DOMAIN_ORDER = ["Office", "Security", "Web", "Speech", "Physio", "Image", "Video"]

TABLE_HEADER = "cyan!12"
TABLE_ALT = "cyan!4"
MODEL_PROCESS_COLOR = "#9fd3f2"
MODEL_RESULT_COLOR = "#ffc4b3"
DOMAIN_PROCESS_COLOR = "#b7e4c7"
DOMAIN_RESULT_COLOR = "#ffd8a8"
HEATMAP_CMAP = "GnBu"

PRETTY_MODEL = {
    "Qwen2.5-14B-Instruct": "Qwen2.5-14B",
    "Qwen2.5-32B-Instruct": "Qwen2.5-32B",
    "Qwen__Qwen2.5-7B-Instruct": "Qwen2.5-7B",
    "Qwen__Qwen3-14B": "Qwen3-14B",
    "Qwen__Qwen3-32B": "Qwen3-32B",
    "deepseek-ai__DeepSeek-R1-Distill-Llama-8B": "DeepSeek-R1-D8B",
    "mistralai__Mistral-7B-Instruct-v0.2": "Mistral-7B",
    "mistralai__Mistral-Small-3.1-24B-Instruct-2503": "Mistral-Small-24B",
    "gpt-5-chat-2025-08-07": "gpt-5-chat",
    "gpt-5.2-2025-12-11": "gpt-5.2",
    "gemini-2.5-pro-preview-06-05": "Gemini-2.5-Pro",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def read_optional_csv(primary, fallback=None):
    if primary.exists():
        return read_csv(primary)
    if fallback is not None and fallback.exists():
        return read_csv(fallback)
    return []


def read_many_csv(paths):
    rows = []
    for path in paths:
        if path.exists():
            rows.extend(read_csv(path))
    return rows


def escape_tex(text):
    return (
        text.replace("\\", "\\textbackslash{}")
        .replace("_", "\\_")
        .replace("%", "\\%")
        .replace("&", "\\&")
    )


def ensure_dirs():
    FIGURES.mkdir(exist_ok=True)
    TABLES.mkdir(exist_ok=True)


def write(path, text):
    path.write_text(text, encoding="utf-8")


def pretty_model(name):
    return PRETTY_MODEL.get(name, name)


def format_family_list(text, items_per_line=3):
    if not text:
        return "--"
    parts = [escape_tex(part.strip()) for part in text.split(";") if part.strip()]
    if len(parts) <= items_per_line:
        return ", ".join(parts)
    lines = [
        ", ".join(parts[idx:idx + items_per_line])
        for idx in range(0, len(parts), items_per_line)
    ]
    return "\\shortstack[l]{" + "\\\\ ".join(lines) + "}"


def build_model_summary_table(rows):
    rows = sorted(
        rows,
        key=lambda row: (
            -int(row["official_result_true"]),
            -int(row["official_process_true"]),
            pretty_model(row["model"]),
        ),
    )
    lines = [
        "\\begin{table}[t]",
        "\\caption{Comparable open-model cohort on the full official GitTaskBench task roster. Process and Result are counts of official \\processmetric$=$True and \\resultmetric$=$True rows per model.}",
        "\\label{tab:model-summary}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        f"\\rowcolor{{{TABLE_HEADER}}}",
        "Model & Process & Result \\\\",
        "\\midrule",
        f"\\rowcolors{{2}}{{{TABLE_ALT}}}{{white}}",
    ]
    for row in rows:
        lines.append(
            f'{escape_tex(pretty_model(row["model"]))} & '
            f'{row["official_process_true"]} & '
            f'{row["official_result_true"]} \\\\'
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    write(TABLES / "model_summary.tex", "\n".join(lines))


def build_domain_table(row_records):
    stats = defaultdict(lambda: {"total": 0, "process": 0, "result": 0})
    for row in row_records:
        domain = FAMILY_TO_DOMAIN[row["family"]]
        stats[domain]["total"] += 1
        stats[domain]["process"] += int(row["official_process"] == "True")
        stats[domain]["result"] += int(row["official_result"] == "True")

    lines = [
        "\\begin{table}[t]",
        "\\caption{Comparable cohort summarized by a fixed family-to-domain map. Process and Result are paper-side aggregates of official \\processmetric$=$True and \\resultmetric$=$True rows.}",
        "\\label{tab:domain-summary}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lrr}",
        "\\toprule",
        f"\\rowcolor{{{TABLE_HEADER}}}",
        "Domain & Process & Result \\\\",
        "\\midrule",
        f"\\rowcolors{{2}}{{{TABLE_ALT}}}{{white}}",
    ]
    for domain in DOMAIN_ORDER:
        item = stats[domain]
        lines.append(
            f'{domain} & {item["process"]} & {item["result"]} \\\\'
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    write(TABLES / "domain_summary.tex", "\n".join(lines))


def build_shared_table(rows):
    task_labels = ["Trafilatura_01", "Trafilatura_02"]
    statuses = defaultdict(dict)
    for row in rows:
        status = f'{int(row["official_process"] == "True")}/{int(row["official_result"] == "True")}'
        statuses[row["model"]][row["task_id"]] = status

    lines = [
        "\\begin{table}[t]",
        "\\caption{Shared benchmark tasks \\texttt{Trafilatura\\_01} and \\texttt{Trafilatura\\_02} across open and provider models. Each cell reports the benchmark's official \\processmetric/\\resultmetric pair for that task.}",
        "\\label{tab:shared-trafilatura}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        f"\\rowcolor{{{TABLE_HEADER}}}",
        "Model & T01 & T02 \\\\",
        "\\midrule",
        f"\\rowcolors{{2}}{{{TABLE_ALT}}}{{white}}",
    ]
    for model in sorted(statuses):
        t1 = statuses[model].get(task_labels[0], "--")
        t2 = statuses[model].get(task_labels[1], "--")
        lines.append(f"{escape_tex(pretty_model(model))} & {t1} & {t2} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    write(TABLES / "shared_trafilatura.tex", "\n".join(lines))


def build_provider_screen_table(model_rows):
    if not model_rows:
        return
    rows = sorted(
        model_rows,
        key=lambda row: (
            -int(row["official_result_true"]),
            -int(row["official_process_true"]),
            pretty_model(row["model"]),
        ),
    )

    lines = [
        "\\begin{table}[t]",
        "\\caption{Targeted provider robustness screen covering the main success-bearing families, the main graded-but-unsuccessful families, and one image/video stress check. Reported separately from the comparable cohort; listed families contain at least one official \\resultmetric$=$True row.}",
        "\\label{tab:provider-screen}",
        "\\centering",
        "\\small",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{tabular}{@{}p{0.17\\columnwidth}ccp{0.47\\columnwidth}@{}}",
        "\\toprule",
        f"\\rowcolor{{{TABLE_HEADER}}}",
        "Model & Process & Result & Families with Result \\\\",
        "\\midrule",
        f"\\rowcolors{{2}}{{{TABLE_ALT}}}{{white}}",
    ]
    for row in rows:
        lines.append(
            f'{escape_tex(pretty_model(row["model"]))} & '
            f'{row["official_process_true"]} & '
            f'{row["official_result_true"]} & '
            f'{format_family_list(row["families_with_official_result"])} \\\\'
        )
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\setlength{\\tabcolsep}{6pt}",
        "\\end{table}",
        "",
    ])
    write(TABLES / "provider_screen.tex", "\n".join(lines))


def build_provider_full54_summary_table(model_rows):
    if not model_rows:
        return
    rows = sorted(
        model_rows,
        key=lambda row: (
            -int(row["official_result_true"]),
            -int(row["official_process_true"]),
            pretty_model(row["model"]),
        ),
    )

    lines = [
        "\\begin{table}[t]",
        "\\caption{Supplementary full-benchmark provider sweeps under the same GitTaskBench evaluation protocol. Listed families contain at least one official \\resultmetric$=$True row.}",
        "\\label{tab:provider-full54-summary}",
        "\\centering",
        "\\scriptsize",
        "\\setlength{\\tabcolsep}{3.5pt}",
        "\\begin{tabular}{@{}p{0.17\\columnwidth}ccp{0.47\\columnwidth}@{}}",
        "\\toprule",
        f"\\rowcolor{{{TABLE_HEADER}}}",
        "Model & Process & Result & Families with Result \\\\",
        "\\midrule",
        f"\\rowcolors{{2}}{{{TABLE_ALT}}}{{white}}",
    ]
    for row in rows:
        lines.append(
            f'{escape_tex(pretty_model(row["model"]))} & '
            f'{row["official_process_true"]} & '
            f'{row["official_result_true"]} & '
            f'{format_family_list(row["families_with_official_result"], items_per_line=2)} \\\\'
        )
    lines.extend([
        "\\bottomrule",
        "\\end{tabular}",
        "\\setlength{\\tabcolsep}{6pt}",
        "\\end{table}",
        "",
    ])
    write(TABLES / "provider_full54_summary.tex", "\n".join(lines))


def plot_model_summary(rows):
    rows = sorted(
        rows,
        key=lambda row: (
            -int(row["official_result_true"]),
            -int(row["official_process_true"]),
            pretty_model(row["model"]),
        ),
    )
    labels = [pretty_model(row["model"]) for row in rows]
    process = np.array([int(row["official_process_true"]) for row in rows])
    result = np.array([int(row["official_result_true"]) for row in rows])

    y = np.arange(len(labels))
    h = 0.38
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.barh(y + h / 2, process, height=h, color=MODEL_PROCESS_COLOR, label="Process")
    ax.barh(y - h / 2, result, height=h, color=MODEL_RESULT_COLOR, label="Result")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Official success count")
    ax.set_xlim(0, 10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Comparable open-model cohort under GitTaskBench official metrics")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for idx, value in enumerate(process):
        ax.text(value + 0.12, y[idx] + h / 2, str(value), va="center", fontsize=8)
    for idx, value in enumerate(result):
        ax.text(value + 0.12, y[idx] - h / 2, str(value), va="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_model_summary.pdf")
    fig.savefig(FIGURES / "figure_model_summary.png", dpi=220)
    plt.close(fig)


def plot_domain_summary(row_records):
    stats = defaultdict(lambda: {"total": 0, "process": 0, "result": 0})
    for row in row_records:
        domain = FAMILY_TO_DOMAIN[row["family"]]
        stats[domain]["total"] += 1
        stats[domain]["process"] += int(row["official_process"] == "True")
        stats[domain]["result"] += int(row["official_result"] == "True")

    process_rates = [stats[d]["process"] / stats[d]["total"] if stats[d]["total"] else 0 for d in DOMAIN_ORDER]
    result_rates = [stats[d]["result"] / stats[d]["total"] if stats[d]["total"] else 0 for d in DOMAIN_ORDER]

    x = np.arange(len(DOMAIN_ORDER))
    w = 0.36
    fig, ax = plt.subplots(figsize=(8.0, 3.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.bar(x - w / 2, process_rates, width=w, color=DOMAIN_PROCESS_COLOR, label="Process rate")
    ax.bar(x + w / 2, result_rates, width=w, color=DOMAIN_RESULT_COLOR, label="Result rate")
    ax.set_xticks(x)
    ax.set_xticklabels(DOMAIN_ORDER, fontsize=8)
    ax.set_ylim(0, 0.25)
    ax.set_ylabel("Rate")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Success mass concentrates in office, security, web, and speech")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for idx, domain in enumerate(DOMAIN_ORDER):
        total = stats[domain]["total"]
        ax.text(
            x[idx] - w / 2,
            process_rates[idx] + 0.008,
            f'{process_rates[idx]:.2f}',
            ha="center",
            va="bottom",
            fontsize=7,
            rotation=90,
        )
        ax.text(
            x[idx] + w / 2,
            result_rates[idx] + 0.008,
            f'{result_rates[idx]:.2f}',
            ha="center",
            va="bottom",
            fontsize=7,
            rotation=90,
        )
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_domain_summary.pdf")
    fig.savefig(FIGURES / "figure_domain_summary.png", dpi=220)
    plt.close(fig)


def plot_task_heatmap(row_records):
    selected_tasks = sorted(
        {row["task_id"] for row in row_records if row["official_result"] == "True"},
        key=lambda task: (task.split("_")[0], task),
    )
    models = [row["model"] for row in read_csv(MODEL_CSV)]
    matrix = np.zeros((len(models), len(selected_tasks)))
    lookup = {(row["model"], row["task_id"]): int(row["official_result"] == "True") for row in row_records}
    for i, model in enumerate(models):
        for j, task_id in enumerate(selected_tasks):
            matrix[i, j] = lookup.get((model, task_id), 0)

    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    im = ax.imshow(matrix, cmap=HEATMAP_CMAP, aspect="auto", vmin=0, vmax=1)
    ax.set_yticks(np.arange(len(models)))
    ax.set_yticklabels([pretty_model(m) for m in models], fontsize=8)
    ax.set_xticks(np.arange(len(selected_tasks)))
    ax.set_xticklabels(selected_tasks, rotation=40, ha="right", fontsize=8)
    ax.set_title("Tied headline scores still hide task-family specialization")
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_ticks([0, 1])
    cbar.set_ticklabels(["0", "1"])
    fig.tight_layout()
    fig.savefig(FIGURES / "figure_task_heatmap.pdf")
    fig.savefig(FIGURES / "figure_task_heatmap.png", dpi=220)
    plt.close(fig)


def main():
    ensure_dirs()
    model_rows = read_csv(MODEL_CSV)
    row_records = read_csv(ROWS_CSV)
    shared_rows = read_csv(SHARED_CSV)
    provider_rows = read_optional_csv(PROVIDER14_ROWS_CSV, PROVIDER14_ROWS_FALLBACK_CSV)
    provider_model_rows = read_optional_csv(PROVIDER14_MODEL_CSV, PROVIDER14_MODEL_FALLBACK_CSV)
    provider54_model_rows = read_many_csv(PROVIDER54_MODEL_CSVS)

    build_model_summary_table(model_rows)
    build_domain_table(row_records)
    build_shared_table(shared_rows)
    build_provider_screen_table(provider_model_rows)
    build_provider_full54_summary_table(provider54_model_rows)
    plot_model_summary(model_rows)
    plot_domain_summary(row_records)
    plot_task_heatmap(row_records)


if __name__ == "__main__":
    main()
