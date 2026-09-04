"""Automated submission-ready PDF generator for VisionGuard Project Report.

Compiles docs/PROJECT_REPORT.md into a beautifully formatted, publication-grade
PDF using ReportLab, complete with title banners, tables, and metadata.
"""

import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_MD_PATH = os.path.join(BASE_DIR, "docs", "PROJECT_REPORT.md")
OUTPUT_PDF_PATH = os.path.join(BASE_DIR, "VisionGuard_Project_Report.pdf")


def build_pdf():
    """Convert docs/PROJECT_REPORT.md to VisionGuard_Project_Report.pdf."""
    print("Reading markdown report from:", REPORT_MD_PATH)
    with open(REPORT_MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        OUTPUT_PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=12,
    )
    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=20,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )
    callout_style = ParagraphStyle(
        "Callout",
        parent=body_style,
        fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#991b1b"),
        backColor=colors.HexColor("#fef2f2"),
        borderPadding=8,
        spaceBefore=6,
        spaceAfter=8,
    )

    story = []

    # Title Banner
    story.append(Paragraph("VisionGuard", title_style))
    story.append(
        Paragraph(
            "<b>AI-Based Driver Drowsiness and Distraction Detection System</b><br/>"
            "VITyarthi 'Build Your Own Project' Evaluation – Final Capstone Report<br/>"
            "Author: <b>Yash Goyal</b> | Vellore Institute of Technology (VIT)",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    # Parse markdown lines
    lines = md_text.split("\n")
    i = 0
    in_table = False
    table_rows = []

    while i < len(lines):
        line = lines[i].strip()

        # Handle Markdown Tables
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            # Skip separator line like |---|---|
            if any(all(ch == "-" or ch == ":" for ch in c) for c in cells):
                i += 1
                continue
            table_rows.append([Paragraph(f"<b>{c}</b>" if len(table_rows) == 0 else c, body_style) for c in cells])
            in_table = True
            i += 1
            continue
        elif in_table:
            # End of table block, render table
            col_widths = [110] + [(doc.width - 110) / (len(table_rows[0]) - 1)] * (len(table_rows[0]) - 1)
            t = Table(table_rows, colWidths=col_widths)
            t.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ])
            )
            story.append(t)
            story.append(Spacer(1, 8))
            table_rows = []
            in_table = False

        if not line:
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            pass  # Header handled in banner
        elif line.startswith("## "):
            text = line[3:].strip()
            story.append(Spacer(1, 6))
            story.append(Paragraph(text, h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=6))
        elif line.startswith("### "):
            text = line[4:].strip()
            story.append(Paragraph(text, h2_style))
        elif line.startswith("* ") or line.startswith("- "):
            text = line[2:].strip()
            # Clean markdown bolding
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(f"&bull; {text}", bullet_style))
        elif line.startswith("> "):
            text = line[2:].strip()
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(text, callout_style))
        else:
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
            story.append(Paragraph(text, body_style))

        i += 1

    print("Compiling PDF...")
    doc.build(story)
    print("PDF Successfully generated at:", OUTPUT_PDF_PATH)


if __name__ == "__main__":
    build_pdf()
