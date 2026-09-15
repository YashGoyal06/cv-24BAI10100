"""Automated submission-ready PDF generator for VisionGuard Project Report.

Compiles docs/PROJECT_REPORT.md into a beautifully formatted, publication-grade
20-page PDF matching the exact visual style, typography, spacing, and 14 sections
of the previous Java VITyarthi Project Report.
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
    PageBreak,
    Image,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_MD_PATH = os.path.join(BASE_DIR, "docs", "PROJECT_REPORT.md")
OUTPUT_PDF_PATH = os.path.join(BASE_DIR, "VisionGuard_Project_Report.pdf")


def build_pdf():
    """Convert docs/PROJECT_REPORT.md into a high-end, publication-grade PDF."""
    print("Reading markdown report from:", REPORT_MD_PATH)
    with open(REPORT_MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        OUTPUT_PDF_PATH,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=45,
        bottomMargin=45,
    )

    styles = getSampleStyleSheet()

    # Typography matching the Java project report style
    main_title_style = ParagraphStyle(
        "MainTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4,
    )
    main_sub_style = ParagraphStyle(
        "MainSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#475569"),
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13.5,
        leading=17,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.5,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=5,
    )
    bullet_style = ParagraphStyle(
        "Bullet_Custom",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3.5,
    )
    code_style = ParagraphStyle(
        "Code_Custom",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6,
    )

    story = []

    # Title Banner
    story.append(Paragraph("VisionGuard", main_title_style))
    story.append(Paragraph("AI-Based Driver Drowsiness and Distraction Detection System — Project Report", main_sub_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=14))

    # Boxed Cover Page metadata (matching the box in Java report)
    box_data = [
        [
            Paragraph(
                "<br/>"
                "<b>VISIONGUARD: AI-BASED DRIVER DROWSINESS & DISTRACTION DETECTION</b><br/><br/>"
                "<i>Academic Project Report</i><br/><br/>"
                "<b>Submitted by:</b> Yash Goyal<br/>"
                "<b>Reg Number:</b> 24BAI10100<br/>"
                "<b>Course:</b> B.Tech | <b>Subject:</b> Computer Vision (Flipped Course Evaluation)<br/>"
                "<b>Session:</b> 2025 - 2026 | <b>Date:</b> 15/09/2026<br/><br/>"
                "<b>VITyarthi - Build Your Own Project</b><br/>",
                ParagraphStyle("BoxContent", parent=body_style, alignment=1, fontSize=9.5, leading=14),
            )
        ]
    ]
    box_table = Table(box_data, colWidths=[doc.width])
    box_table.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.5, colors.HexColor("#334155")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ])
    )
    story.append(box_table)
    story.append(Spacer(1, 14))

    # Diagrams map
    diagram_map = {
        "7.1": os.path.join(BASE_DIR, "docs", "diagrams", "01-use-case-diagram.png"),
        "7.2": os.path.join(BASE_DIR, "docs", "diagrams", "02-class-diagram.png"),
        "7.3": os.path.join(BASE_DIR, "docs", "diagrams", "03-sequence-diagram.png"),
        "7.4": os.path.join(BASE_DIR, "docs", "diagrams", "04-architecture-diagram.png"),
        "7.5": os.path.join(BASE_DIR, "docs", "diagrams", "05-er-diagram.png"),
        "7.6": os.path.join(BASE_DIR, "docs", "diagrams", "06-process-flow-diagram.png"),
    }

    # Screenshots map
    screenshot_map = {
        "10.1": os.path.join(BASE_DIR, "docs", "screenshots", "01_live_monitoring_safe.png"),
        "10.2": os.path.join(BASE_DIR, "docs", "screenshots", "02_drowsiness_detected.png"),
        "10.3": os.path.join(BASE_DIR, "docs", "screenshots", "03_distraction_detected.png"),
        "10.4": os.path.join(BASE_DIR, "docs", "screenshots", "04_yawn_detected_caution.png"),
        "10.5": os.path.join(BASE_DIR, "docs", "screenshots", "05_compound_high_risk.png"),
    }

    lines = md_text.split("\n")
    i = 0
    in_table = False
    table_rows = []
    in_code = False
    code_lines = []

    while i < len(lines):
        line = lines[i].strip()

        # Handle Markdown Code blocks
        if line.startswith("```"):
            if in_code:
                # End of code block
                code_text = "<br/>".join(code_lines).replace(" ", "&nbsp;")
                story.append(Paragraph(code_text, code_style))
                code_lines = []
                in_code = False
            else:
                in_code = True
            i += 1
            continue
        elif in_code:
            code_lines.append(line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
            i += 1
            continue

        # Handle Markdown Tables
        if line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.split("|")[1:-1]]
            if any(all(ch == "-" or ch == ":" for ch in c) for c in cells):
                i += 1
                continue
            is_header = len(table_rows) == 0
            row_cells = []
            for c in cells:
                c_clean = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", c)
                row_cells.append(Paragraph(f"<b>{c_clean}</b>" if is_header else c_clean, body_style))
            table_rows.append(row_cells)
            in_table = True
            i += 1
            continue
        elif in_table:
            # Render Table
            num_cols = len(table_rows[0])
            first_w = 65 if num_cols >= 5 else 120
            rem_w = (doc.width - first_w) / (num_cols - 1)
            col_widths = [first_w] + [rem_w] * (num_cols - 1)
            t = Table(table_rows, colWidths=col_widths)
            t.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 5),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ])
            )
            story.append(t)
            story.append(Spacer(1, 6))
            table_rows = []
            in_table = False

        if not line:
            i += 1
            continue

        # Headings
        if line.startswith("# "):
            pass  # Title handled in banner
        elif line.startswith("## "):
            text = line[3:].strip()
            # Page break before major sections like in the 20-page report
            if any(text.startswith(f"{num}.") for num in [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]):
                story.append(PageBreak())
            else:
                story.append(Spacer(1, 8))
            story.append(Paragraph(text, h1_style))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=6))
        elif line.startswith("### "):
            text = line[4:].strip()
            story.append(Spacer(1, 4))
            story.append(Paragraph(text, h2_style))

            # Auto-embed diagram image if section matches
            for prefix, img_path in diagram_map.items():
                if text.startswith(prefix) and os.path.exists(img_path):
                    story.append(Spacer(1, 4))
                    story.append(Image(img_path, width=440, height=210))
                    story.append(Spacer(1, 4))

            # Auto-embed screenshot image if section matches
            for prefix, img_path in screenshot_map.items():
                if text.startswith(prefix) and os.path.exists(img_path):
                    story.append(Spacer(1, 4))
                    story.append(Image(img_path, width=380, height=200))
                    story.append(Spacer(1, 4))

        elif line.startswith("* ") or line.startswith("- "):
            text = line[2:].strip()
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(f"&bull; {text}", bullet_style))
        else:
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
            story.append(Paragraph(text, body_style))

        i += 1

    print("Compiling publication-grade 14-section PDF...")
    doc.build(story)
    print("PDF Successfully compiled at:", OUTPUT_PDF_PATH)


if __name__ == "__main__":
    build_pdf()
