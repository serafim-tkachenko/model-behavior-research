"""Build the concise SAE report from committed Markdown and evidence tables."""

from __future__ import annotations

import html
import posixpath
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports/sae_context_study"
MODELS = [
    ("zero", "Zero effect"),
    ("fit_mean", "Fit-set mean"),
    ("nuisance", "Nuisance variables"),
    ("context", "Nuisance + context"),
    ("pc8_only", "Nuisance + PCs"),
    ("pc8_context", "Nuisance + PCs + context"),
    ("scalar_gain", "Scalar gain"),
]


def figures_and_checks(text: str) -> None:
    frame = pd.read_csv(ROOT / "evidence/sae_prediction/prediction_summary.csv")
    pooled = frame[frame.train_source == "pooled"].pivot(
        index="model", columns="feature_id", values="mse"
    )
    # Keep the hand-written table tied to the evidence; fail if its numbers drift.
    for model, label in MODELS:
        line = next(
            line for line in text.splitlines() if line.startswith(f"| {label} |")
        )
        displayed = [float(cell.strip()) for cell in line.strip("|").split("|")[1:]]
        np.testing.assert_allclose(
            displayed, pooled.loc[model, [1645, 2966, 28027]], rtol=1e-5, atol=0
        )
    plt.rcParams.update(
        {"font.size": 10, "axes.spines.top": False, "axes.spines.right": False}
    )
    fig, axes = plt.subplots(1, 3, figsize=(10, 3.3), sharey=True)
    for axis, feature in zip(axes, [1645, 2966, 28027]):
        ratios = [
            pooled.loc[m, feature] / pooled.loc["fit_mean", feature] for m, _ in MODELS
        ]
        axis.barh(
            range(len(MODELS)), ratios, color=["#808b96", "#808b96"] + ["#246080"] * 5
        )
        axis.axvline(1, color="#b75335", linewidth=1.3, linestyle="--")
        axis.set_title(f"Feature {feature}")
        axis.set_xlim(0, 1.65)
        axis.set_xlabel("MSE / fit-mean MSE")
        axis.set_yticks(range(len(MODELS)), [label for _, label in MODELS])
        axis.grid(axis="x", alpha=0.15)
        axis.set_axisbelow(True)
    axes[0].invert_yaxis()
    fig.tight_layout()
    fig.savefig(OUT / "prediction_baselines.png", dpi=200, facecolor="white")
    plt.close(fig)

    controls = pd.read_csv(ROOT / "evidence/sae_prediction/paired_controls.csv")
    selected = (
        controls[controls.feature_id == 1645]
        .set_index("metric")
        .loc[["interaction_norm", "beyond_gain_norm"]]
    )
    fig, axis = plt.subplots(figsize=(8.5, 2.5))
    axis.errorbar(
        selected["mean"],
        [1, 0],
        xerr=[selected["mean"] - selected.low, selected.high - selected["mean"]],
        fmt="o",
        color="#246080",
        capsize=5,
        markersize=7,
    )
    axis.axvline(0, color="#b75335", linestyle="--", linewidth=1)
    axis.set_yticks([1, 0], ["Raw interaction", "Beyond scalar gain"])
    axis.set_ylim(-0.6, 1.6)
    axis.set_xlabel("Learned minus mean random control (diagnostic logit units)")
    axis.set_title("Feature 1645: 16 check groups")
    axis.grid(axis="x", alpha=0.15)
    fig.tight_layout()
    fig.savefig(OUT / "interaction_controls.png", dpi=200, facecolor="white")
    plt.close(fig)


def markup(text: str) -> str:
    text = html.escape(text)

    def link(match):
        label, url = match.groups()
        if not url.startswith(("https://", "http://")):
            url = (
                "https://github.com/serafim-tkachenko/model-behavior-research/blob/main/"
                + posixpath.normpath("reports/sae_context_study/" + url)
            )
        return f'<a href="{url}" color="#246080">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    return re.sub(r"`([^`]+)`", r'<font name="Courier" size="8.5">\1</font>', text)


def build_pdf(text: str) -> None:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "BodyStudy",
            fontName="Helvetica",
            fontSize=10,
            leading=13.5,
            spaceAfter=8,
            textColor=colors.HexColor("#202a34"),
        )
    )
    styles.add(
        ParagraphStyle(
            "TitleStudy",
            parent=styles["Title"],
            alignment=TA_LEFT,
            fontSize=23,
            leading=27,
            spaceAfter=12,
            textColor=colors.HexColor("#173f56"),
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionStudy",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            spaceBefore=12,
            spaceAfter=7,
            keepWithNext=True,
        )
    )
    styles.add(
        ParagraphStyle(
            "CellStudy",
            parent=styles["BodyStudy"],
            fontSize=8,
            leading=11,
            spaceAfter=0,
        )
    )
    story, lines = [], text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("# "):
            story.append(Paragraph(markup(line[2:]), styles["TitleStudy"]))
        elif line.startswith("## "):
            story.append(Paragraph(markup(line[3:]), styles["SectionStudy"]))
        elif line.startswith("!["):
            name = re.search(r"\]\(([^)]+)\)", line).group(1)
            picture = Image(str(OUT / name))
            picture.drawHeight *= 475 / picture.drawWidth
            picture.drawWidth = 475
            story.extend([Spacer(1, 5), picture, Spacer(1, 6)])
        elif line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [
                    cell.strip() for cell in lines[i].strip().strip("|").split("|")
                ]
                if not all(re.fullmatch(r"[:\- ]+", cell) for cell in cells):
                    rows.append(
                        [Paragraph(markup(cell), styles["CellStudy"]) for cell in cells]
                    )
                i += 1
            widths = (
                [170, 100, 100, 105]
                if "Predictor" in rows[0][0].text
                else [60, 95, 160, 160]
            )
            table = Table(rows, colWidths=widths, repeatRows=1, hAlign="LEFT")
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eff3")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#f6f8f9")],
                        ),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.HexColor("#acbec9")),
                    ]
                )
            )
            story.extend([table, Spacer(1, 10)])
            continue
        elif line.startswith("- "):
            story.append(
                Paragraph(markup(line[2:]), styles["BodyStudy"], bulletText="-")
            )
        else:
            paragraph = [line]
            while (
                i + 1 < len(lines)
                and lines[i + 1].strip()
                and not lines[i + 1].startswith(("#", "|", "![", "- "))
            ):
                i += 1
                paragraph.append(lines[i].strip())
            story.append(Paragraph(markup(" ".join(paragraph)), styles["BodyStudy"]))
        i += 1

    def footer(canvas, doc):
        canvas.setStrokeColor(colors.HexColor("#d4dde2"))
        canvas.line(60, 43, A4[0] - 60, 43)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#526572"))
        canvas.drawString(
            60, 29, "SAE context and intervention prediction | September 2026"
        )
        canvas.drawRightString(A4[0] - 60, 29, str(doc.page))

    doc = SimpleDocTemplate(
        str(OUT / "report.pdf"),
        pagesize=A4,
        leftMargin=60,
        rightMargin=60,
        topMargin=48,
        bottomMargin=58,
        title="Can activation context predict SAE intervention effects?",
        author="Serafim Tkachenko",
    )
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    source = (OUT / "report.md").read_text(encoding="utf-8")
    figures_and_checks(source)
    build_pdf(source)
    print(
        f"Built {OUT / 'report.pdf'}; checked all 21 displayed prediction values against evidence."
    )
