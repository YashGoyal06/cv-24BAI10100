"""Automated submission-ready PDF generator for VisionGuard Project Report.

Compiles docs/PROJECT_REPORT.md into an impeccably formatted, publication-grade
academic PDF report matching the exact visual style, typography, and natural flow
of the Java VITyarthi Project Report without awkward page breaks or blank spaces.
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
    Image,
)
from reportlab.pdfgen import canvas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORT_MD_PATH = os.path.join(BASE_DIR, "docs", "PROJECT_REPORT.md")
OUTPUT_PDF_PATH = os.path.join(BASE_DIR, "VisionGuard_Project_Report.pdf")


class NumberedCanvas(canvas.Canvas):
    """Canvas for adding professional running headers and 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))

        # Suppress running header on cover page (page 1)
        if self._pageNumber > 1:
            self.drawString(45, 755, "VisionGuard: AI-Based Driver Drowsiness & Distraction Detection System")
            self.drawRightString(612 - 45, 755, "VITyarthi Academic Report")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(45, 748, 612 - 45, 748)

        # Footer across all pages
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(612 - 45, 32, page_str)
        self.drawString(45, 32, "VITyarthi — Build Your Own Project Evaluation  |  Reg No: 24BAI10100")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(45, 42, 612 - 45, 42)

        self.restoreState()


def build_pdf():
    """Build the formal report PDF."""
    print("Reading markdown report from:", REPORT_MD_PATH)
    with open(REPORT_MD_PATH, "r", encoding="utf-8") as f:
        raw_text = f.read()

    doc = SimpleDocTemplate(
        OUTPUT_PDF_PATH,
        pagesize=letter,
        leftMargin=45,
        rightMargin=45,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Typography styles tailored to match the Java report aesthetics
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=3,
    )
    sub_title_style = ParagraphStyle(
        "ReportSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#475569"),
        spaceAfter=12,
    )
    h1_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "SubSectionHeading",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14.5,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.0,
        leading=13.0,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=4,
    )
    bullet_style = ParagraphStyle(
        "Bullet",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=3,
    )
    code_style = ParagraphStyle(
        "Code",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=7.5,
        leading=10.0,
        textColor=colors.HexColor("#0f172a"),
        backColor=colors.HexColor("#f8fafc"),
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=5,
    )

    story = []

    # Title Banner (matching Java report top banner)
    story.append(Paragraph("Student Academic Project Report", sub_title_style))
    story.append(Paragraph("VisionGuard: Driver Drowsiness & Distraction Detection", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=12))

    # Boxed Cover Page Info (exact replica of Java report box)
    box_content = [
        [
            Paragraph(
                "<br/>"
                "<b>VISIONGUARD: AI-BASED DRIVER DROWSINESS AND DISTRACTION DETECTION</b><br/><br/>"
                "<i>Academic Project Report</i><br/><br/>"
                "<b>Submitted by:</b> Yash Goyal<br/>"
                "<b>Reg Number:</b> 24BAI10100<br/>"
                "<b>Course:</b> B.Tech | <b>Subject:</b> Computer Vision (Flipped Course Evaluation)<br/>"
                "<b>Session:</b> 2025 - 2026 | <b>Date:</b> 15/09/2026<br/><br/>"
                "<b>VITyarthi - Build Your Own Project</b><br/>",
                ParagraphStyle("BoxP", parent=body_style, alignment=1, fontSize=9.5, leading=14),
            )
        ]
    ]
    box_table = Table(box_content, colWidths=[doc.width])
    box_table.setStyle(
        TableStyle([
            ("BOX", (0, 0), (-1, -1), 1.2, colors.HexColor("#334155")),
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ])
    )
    story.append(box_table)
    story.append(Spacer(1, 10))

    # Map sections to their diagram/screenshot files
    diagram_map = {
        "7.1": os.path.join(BASE_DIR, "docs", "diagrams", "01-use-case-diagram.png"),
        "7.2": os.path.join(BASE_DIR, "docs", "diagrams", "02-class-diagram.png"),
        "7.3": os.path.join(BASE_DIR, "docs", "diagrams", "03-sequence-diagram.png"),
        "7.4": os.path.join(BASE_DIR, "docs", "diagrams", "04-architecture-diagram.png"),
        "7.5": os.path.join(BASE_DIR, "docs", "diagrams", "05-er-diagram.png"),
        "7.6": os.path.join(BASE_DIR, "docs", "diagrams", "06-process-flow-diagram.png"),
    }

    screenshot_map = {
        "10.1": os.path.join(BASE_DIR, "docs", "screenshots", "01_live_monitoring_safe.png"),
        "10.2": os.path.join(BASE_DIR, "docs", "screenshots", "02_drowsiness_detected.png"),
        "10.3": os.path.join(BASE_DIR, "docs", "screenshots", "03_distraction_detected.png"),
        "10.4": os.path.join(BASE_DIR, "docs", "screenshots", "04_yawn_detected_caution.png"),
        "10.5": os.path.join(BASE_DIR, "docs", "screenshots", "05_compound_high_risk.png"),
    }

    lines = raw_text.split("\n")
    i = 0
    in_table = False
    table_rows = []
    in_code = False
    code_lines = []

    # Skip any redundant initial title or cover lines up to section 1
    found_cover = False

    while i < len(lines):
        line = lines[i].strip()

        # Handle Markdown Code blocks
        if line.startswith("```"):
            if in_code:
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
                c_clean = c_clean.replace("$", "")
                row_cells.append(Paragraph(f"<b>{c_clean}</b>" if is_header else c_clean, body_style))
            table_rows.append(row_cells)
            in_table = True
            i += 1
            continue
        elif in_table:
            # Render Table cleanly
            num_cols = len(table_rows[0])
            first_w = 60 if num_cols >= 5 else 120
            rem_w = (doc.width - first_w) / (num_cols - 1)
            col_widths = [first_w] + [rem_w] * (num_cols - 1)
            t = Table(table_rows, colWidths=col_widths)
            t.setStyle(
                TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ])
            )
            story.append(t)
            story.append(Spacer(1, 5))
            table_rows = []
            in_table = False

        if not line:
            i += 1
            continue

        # Skip text before Section 1 to avoid duplicate title blocks
        if line.startswith("## 1. COVER PAGE"):
            found_cover = True

        if not found_cover and not line.startswith("## 1."):
            i += 1
            continue

        # Headings
        if line.startswith("## "):
            text = line[3:].strip()
            # Suppress duplicating Section 1 since it's already rendered in the cover box
            if text.startswith("1. COVER PAGE"):
                i += 1
                # Skip contents of section 1
                while i < len(lines) and not lines[i].strip().startswith("## 2."):
                    i += 1
                continue

            story.append(Spacer(1, 10))
            story.append(Paragraph(text, h1_style))
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#94a3b8"), spaceAfter=5))
        elif line.startswith("### "):
            text = line[4:].strip()
            story.append(Spacer(1, 4))
            story.append(Paragraph(text, h2_style))

            # Auto-embed diagram image if section matches
            for prefix, img_path in diagram_map.items():
                if text.startswith(prefix) and os.path.exists(img_path):
                    story.append(Spacer(1, 3))
                    story.append(Image(img_path, width=440, height=200))
                    story.append(Spacer(1, 3))

            # Auto-embed screenshot image if section matches
            for prefix, img_path in screenshot_map.items():
                if text.startswith(prefix) and os.path.exists(img_path):
                    story.append(Spacer(1, 3))
                    story.append(Image(img_path, width=380, height=190))
                    story.append(Spacer(1, 3))

        elif line.startswith("* ") or line.startswith("- "):
            text = line[2:].strip()
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
            text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
            text = text.replace("$", "")
            story.append(Paragraph(f"&bull; {text}", bullet_style))
        else:
            text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
            text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
            text = text.replace("$", "")
            story.append(Paragraph(text, body_style))

        i += 1

    print("Compiling publication-grade report with running headers & footers...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF Successfully generated at:", OUTPUT_PDF_PATH)


if __name__ == "__main__":
    build_pdf()
