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

PRETTY_MODEL = {
    "Qwen2.5-14B-Instruct": "Qwen2.5-14B",
    "Qwen2.5-32B-Instruct": "Qwen2.5-32B",
    "Qwen__Qwen2.5-7B-Instruct": "Qwen2.5-7B",
    "Qwen__Qwen3-14B": "Qwen3-14B",
    "Qwen__Qwen3-32B": "Qwen3-32B",
    "deepseek-ai__DeepSeek-R1-Distill-Llama-8B": "DeepSeek-R1-D8B",
    "mistralai__Mistral-7B-Instruct-v0.2": "Mistral-7B",
    "mistralai__Mistral-Small-3.1-24B-Instruct-2503": "Mistral-Small-24B",
    "gpt-5.2-2025-12-11": "gpt-5.2",
    "gemini-2.5-pro-preview-06-05": "Gemini-2.5-Pro",
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
        "\\caption{Official GitTaskBench summary on the comparable open-8 local cohort.}",
        "\\label{tab:model-summary}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        "Model & Process & Result \\\\",
        "\\midrule",
    ]
    for row in rows:
        lines.append(
            f'{escape_tex(pretty_model(row["model"]))} & '
            f'{row["official_process_true"]}/54 & '
            f'{row["official_result_true"]}/54 \\\\'
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
        "\\caption{Domain-level concentration under official GitTaskBench metrics. Rates are paper-side aggregates over official per-task outputs.}",
        "\\label{tab:domain-summary}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "Domain & Total & Process & Result \\\\",
        "\\midrule",
    ]
    for domain in DOMAIN_ORDER:
        item = stats[domain]
        lines.append(
            f'{domain} & {item["total"]} & {item["process"]} & {item["result"]} \\\\'
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
        "\\caption{Latest shared-task official outcomes across all locally available models. Each cell reports Process/Result.}",
        "\\label{tab:shared-trafilatura}",
        "\\centering",
        "\\small",
        "\\begin{tabular}{lcc}",
        "\\toprule",
        "Model & T01 & T02 \\\\",
        "\\midrule",
    ]
    for model in sorted(statuses):
        t1 = statuses[model].get(task_labels[0], "--")
        t2 = statuses[model].get(task_labels[1], "--")
        lines.append(f"{escape_tex(pretty_model(model))} & {t1} & {t2} \\\\")
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    write(TABLES / "shared_trafilatura.tex", "\n".join(lines))


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
    ax.barh(y + h / 2, process, height=h, color="#8ecae6", label="Process")
    ax.barh(y - h / 2, result, height=h, color="#1d3557", label="Result")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Official successes out of 54 tasks")
    ax.set_xlim(0, 10)
    ax.grid(axis="x", linestyle="--", alpha=0.3)
    ax.legend(frameon=False, loc="lower right")
    ax.set_title("Comparable open-8 cohort under GitTaskBench official metrics")
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
    ax.bar(x - w / 2, process_rates, width=w, color="#a8dadc", label="Process rate")
    ax.bar(x + w / 2, result_rates, width=w, color="#457b9d", label="Result rate")
    ax.set_xticks(x)
    ax.set_xticklabels(DOMAIN_ORDER, fontsize=8)
    ax.set_ylim(0, 0.25)
    ax.set_ylabel("Rate")
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.legend(frameon=False, loc="upper right")
    ax.set_title("Success mass concentrates in office, security, web, and speech")
    for idx, domain in enumerate(DOMAIN_ORDER):
        total = stats[domain]["total"]
        ax.text(
            x[idx] - w / 2,
            process_rates[idx] + 0.008,
            f'{stats[domain]["process"]}/{total}',
            ha="center",
            va="bottom",
            fontsize=7,
            rotation=90,
        )
        ax.text(
            x[idx] + w / 2,
            result_rates[idx] + 0.008,
            f'{stats[domain]["result"]}/{total}',
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
    im = ax.imshow(matrix, cmap="Blues", aspect="auto", vmin=0, vmax=1)
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

    build_model_summary_table(model_rows)
    build_domain_table(row_records)
    build_shared_table(shared_rows)
    plot_model_summary(model_rows)
    plot_domain_summary(row_records)
    plot_task_heatmap(row_records)


if __name__ == "__main__":
    main()
