import os
import re
from pathlib import Path

import pdfplumber
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    FrameBreak,
    Image as RLImage,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SRC = Path(r"C:\Users\Bittu\Downloads\BTSecBench_IEEE.pdf")
RENDER_DIR = ROOT / "tmp" / "pdfs" / "rendered"
IMG_DIR = ROOT / "tmp" / "pdfs" / "figures"
OUT = ROOT / "output" / "pdf" / "BTSecBench_IEEE_corrected.pdf"
IEEE_OUT = ROOT / "output" / "pdf" / "BTSecBench_IEEE_corrected_ieee_format.pdf"


def clean_text(text: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2212": "-",
        "\u00d7": "x",
        "\u2713": "Yes",
        "\u2717": "No",
        "\ufb01": "fi",
        "\ufb02": "fl",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"(?<=\w)-\s+(?=\w)", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    text = text.replace("Index Terms-", "Index Terms - ")
    text = text.replace("BTSec Bench", "BTSecBench")
    text = text.replace("Bad Nets", "BadNets")
    text = text.replace("Wa Net", "WaNet")
    text = text.replace("TABLEOFACRONYMS", "")
    return text


def extract_column_text(page, x0, x1, y0=0, y1=None):
    if y1 is None:
        y1 = page.height
    crop = page.crop((x0, y0, x1, y1))
    text = crop.extract_text(x_tolerance=1, y_tolerance=4) or ""
    lines = []
    for line in text.splitlines():
        line = clean_text(line)
        if not line:
            continue
        lines.append(line)
    return lines


def crop_figures(pdf):
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    crops = {}
    scale = 120 / 72
    with pdfplumber.open(str(pdf)) as doc:
        for page_no, page in enumerate(doc.pages, 1):
            if not page.images:
                continue
            rendered = RENDER_DIR / f"page-{page_no:02d}.png"
            if not rendered.exists():
                continue
            base = Image.open(rendered).convert("RGB")
            groups = []
            if page_no == 7:
                xs0 = min(img["x0"] for img in page.images)
                xs1 = max(img["x1"] for img in page.images)
                tops = min(img["top"] for img in page.images)
                bottoms = max(img["bottom"] for img in page.images)
                groups.append((xs0, tops, xs1, bottoms))
            else:
                for img in page.images:
                    groups.append((img["x0"], img["top"], img["x1"], img["bottom"]))
            for idx, (x0, top, x1, bottom) in enumerate(groups, 1):
                pad = 8
                box = (
                    max(0, int(x0 * scale) - pad),
                    max(0, int(top * scale) - pad),
                    min(base.width, int(x1 * scale) + pad),
                    min(base.height, int(bottom * scale) + pad),
                )
                out = IMG_DIR / f"page_{page_no:02d}_fig_{idx}.png"
                base.crop(box).save(out)
                crops.setdefault(page_no, []).append(out)
    return crops


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        "PaperTitle",
        parent=styles["Title"],
        fontName="Times-Bold",
        fontSize=17.5,
        leading=21,
        alignment=TA_CENTER,
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        "Author",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8,
        leading=9.2,
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=10.2,
        leading=12,
        alignment=TA_CENTER,
        spaceBefore=8,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "Subsection",
        parent=styles["Heading3"],
        fontName="Times-Italic",
        fontSize=9,
        leading=10.2,
        spaceBefore=6,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        "BodyJustify",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8.8,
        leading=10.4,
        alignment=TA_JUSTIFY,
        firstLineIndent=9,
        spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        "Abstract",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8.4,
        leading=9.8,
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        "Caption",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8.2,
        leading=9.6,
        alignment=TA_CENTER,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        "TableTitle",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=8.2,
        leading=9.4,
        alignment=TA_CENTER,
        spaceBefore=5,
        spaceAfter=3,
    ))
    return styles


def add_table(story, title, rows, widths=None):
    styles = make_styles()
    story.append(Paragraph(title, styles["TableTitle"]))
    table = Table(rows, colWidths=widths, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Times-Roman", 6.9),
        ("FONT", (0, 0), (-1, 0), "Times-Bold", 6.9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEABOVE", (0, 0), (-1, 0), 0.75, colors.black),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("LINEBELOW", (0, -1), (-1, -1), 0.75, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f6f6f6")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(table)
    story.append(Spacer(1, 8))


def manual_tables():
    return {
        "acronyms": [
            ["Acronym", "Meaning"],
            ["TSR", "Traffic Sign Recognition"],
            ["GTSRB", "German Traffic Sign Recognition Benchmark"],
            ["CNN", "Convolutional Neural Network"],
            ["ASR", "Attack Success Rate"],
            ["MCC", "Matthews Correlation Coefficient"],
            ["STRIP", "STRong Intentional Perturbation"],
            ["ADAS", "Advanced Driver Assistance Systems"],
            ["AI", "Artificial Intelligence"],
            ["DL", "Deep Learning"],
        ],
        "dataset": [
            ["Characteristic", "Value"],
            ["Dataset", "GTSRB"],
            ["Number of Classes", "43"],
            ["Image Format", "RGB"],
            ["Image Size", "Variable, resized to 224x224"],
            ["Learning Task", "Image Classification"],
        ],
        "architectures": [
            ["Model", "Params (M)", "Efficiency", "Selected"],
            ["Baseline CNN", "Varies", "Moderate", "No"],
            ["ResNet18", "11.7", "Good", "No"],
            ["MobileNetV3", "5.4", "Excellent", "No"],
            ["EfficientNet-B0", "5.3", "Excellent", "Yes"],
        ],
        "clean": [
            ["Metric", "Value"],
            ["Validation Accuracy", "99.99%"],
            ["Precision", "99.99%"],
            ["Recall", "99.99%"],
            ["F1-Score", "99.99%"],
            ["Balanced Accuracy", "99.99%"],
            ["MCC", "0.9999"],
        ],
        "strip": [
            ["Metric", "Value"],
            ["Detection Accuracy", "56.61%"],
            ["Precision", "53.88%"],
            ["Recall", "91.70%"],
            ["F1-Score", "67.88%"],
            ["ROC-AUC", "0.528"],
        ],
        "finetune": [
            ["Metric", "Value"],
            ["Validation Accuracy", "99.94%"],
            ["Precision", "99.87%"],
            ["Recall", "99.93%"],
            ["F1-Score", "99.90%"],
            ["MCC", "0.9993"],
            ["Validation Loss", "0.004"],
        ],
        "attacks": [
            ["Attack", "Trigger Type", "Visibility"],
            ["BadNets", "Local patch", "High"],
            ["Blend", "Blended overlay", "Medium"],
            ["SIG", "Global sinusoidal", "Low"],
            ["WaNet", "Warping field", "Low"],
        ],
    }


def add_image(story, path, caption, styles):
    img = Image.open(path)
    max_w = 3.35 * inch
    max_h = 2.3 * inch
    scale = min(max_w / img.width, max_h / img.height, 1)
    story.append(KeepTogether([
        RLImage(str(path), width=img.width * scale, height=img.height * scale, hAlign="CENTER"),
        Paragraph(caption, styles["Caption"]),
    ]))


TITLE = (
    "BTSecBench: A Comprehensive Benchmark Framework for Backdoor Attack "
    "Detection and Defense in Traffic Sign Recognition Using Deep Learning"
)

AUTHORS = [
    "Pavan Rishi Gillela<br/>Master of Science in Data Science<br/>University of Europe for Applied Sciences<br/>Potsdam, Germany<br/>pavan.gillela@ue-germany.de",
    "Purnachandar Vallala<br/>Master of Science in Data Science<br/>University of Europe for Applied Sciences<br/>Potsdam, Germany<br/>purnachandar.vallala@ue-germany.de",
    "Hitesh Sri Sai Manepalli<br/>Master of Science in Data Science<br/>University of Europe for Applied Sciences<br/>Potsdam, Germany<br/>hitesh.manepalli@ue-germany.de",
]


def draw_first_page_header(canvas, doc):
    styles = make_styles()
    width, height = letter
    margin = 0.55 * inch
    y = height - 0.55 * inch
    title = Paragraph(TITLE, styles["PaperTitle"])
    tw, th = title.wrap(width - 2 * margin, 1.2 * inch)
    y -= th
    title.drawOn(canvas, margin, y)
    y -= 16

    author_table = Table(
        [[Paragraph(a, styles["Author"]) for a in AUTHORS]],
        colWidths=[(width - 2 * margin) / 3] * 3,
    )
    author_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    aw, ah = author_table.wrap(width - 2 * margin, 1 * inch)
    y -= ah
    author_table.drawOn(canvas, margin, y)


def make_ieee_doc(path):
    width, height = letter
    margin_x = 0.55 * inch
    bottom = 0.55 * inch
    top = 0.55 * inch
    gap = 0.22 * inch
    col_w = (width - 2 * margin_x - gap) / 2
    first_top = 8.25 * inch

    first_frames = [
        Frame(margin_x, bottom, col_w, first_top - bottom, id="first-left", showBoundary=0),
        Frame(margin_x + col_w + gap, bottom, col_w, first_top - bottom, id="first-right", showBoundary=0),
    ]
    body_h = height - top - bottom
    later_frames = [
        Frame(margin_x, bottom, col_w, body_h, id="left", showBoundary=0),
        Frame(margin_x + col_w + gap, bottom, col_w, body_h, id="right", showBoundary=0),
    ]
    doc = BaseDocTemplate(
        str(path),
        pagesize=letter,
        leftMargin=margin_x,
        rightMargin=margin_x,
        topMargin=top,
        bottomMargin=bottom,
    )
    doc.addPageTemplates([
        PageTemplate(id="First", frames=first_frames, onPage=draw_first_page_header, autoNextPageTemplate="Later"),
        PageTemplate(id="Later", frames=later_frames),
    ])
    return doc


def should_skip(line):
    skip_prefixes = (
        "BTSecBench:",
        "Pavan Rishi",
        "Purnachandar",
        "Hitesh Sri",
        "Master of Science",
        "University of Europe",
        "Potsdam, Germany",
        "pavan.gillela",
        "purnachandar",
        "hitesh.manepalli",
    )
    if line.startswith(skip_prefixes):
        return True
    if line in {"I. INTRODUCTION", "A. Background"}:
        return True
    if line.startswith("TABLE ") or line.startswith("Table "):
        return True
    if re.match(r"^(Acronym|Metric|Model|Dataset|Attack|Characteristic)\b", line):
        return True
    if re.match(r"^(TSR|GTSRB|CNN|ASR|MCC|STRIP|ADAS|AI|DL)\s+", line):
        return True
    if re.match(r"^(Validation Accuracy|Precision|Recall|F1-Score|Balanced Accuracy|Detection Accuracy|ROC-AUC|Validation Loss)\s+", line):
        return True
    if re.match(r"^(Baseline CNN|ResNet18|MobileNetV3|EfficientNet-B0|BadNets|Blend|SIG|WaNet)\s+", line):
        return True
    if re.match(r"^(Number of Classes|Image Format|Image Size|Learning Task)\s+", line):
        return True
    return False


def add_paragraphs(story, lines, styles):
    buf = []

    def flush():
        nonlocal buf
        if buf:
            text = clean_text(" ".join(buf))
            if text:
                story.append(Paragraph(text, styles["BodyJustify"]))
            buf = []

    for line in lines:
        line = clean_text(line)
        if not line or should_skip(line):
            continue
        if re.match(r"^[IVX]+\.\s+", line):
            flush()
            story.append(Paragraph(line, styles["Section"]))
        elif re.match(r"^[A-Z]\.\s+", line):
            flush()
            story.append(Paragraph(line, styles["Subsection"]))
        elif line.startswith("Fig."):
            flush()
            story.append(Paragraph(line, styles["Caption"]))
        else:
            buf.append(line)
    flush()


def main():
    IEEE_OUT.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    figures = crop_figures(SRC)
    tables = manual_tables()

    doc = make_ieee_doc(IEEE_OUT)
    story = []

    with pdfplumber.open(str(SRC)) as pdf:
        left_first = extract_column_text(pdf.pages[0], 45, 306, 330, 740)
        abstract = []
        keywords = []
        in_keywords = False
        for line in left_first:
            if line.startswith("Index Terms"):
                in_keywords = True
            if in_keywords:
                keywords.append(line)
            else:
                abstract.append(line)
        abstract_text = clean_text(" ".join(abstract)).replace("Abstract-", "")
        story.append(Paragraph(f"<b><i>Abstract-</i></b> {abstract_text}", styles["Abstract"]))
        story.append(Paragraph(clean_text(" ".join(keywords)), styles["Abstract"]))
        story.append(FrameBreak())
        add_table(story, "TABLE OF ACRONYMS", tables["acronyms"], [0.72 * inch, 2.58 * inch])
        story.append(Paragraph("I. INTRODUCTION", styles["Section"]))
        story.append(Paragraph("A. Background", styles["Subsection"]))

        all_lines = []
        all_lines.extend(extract_column_text(pdf.pages[0], 306, 570, 470, 740))
        for i, page in enumerate(pdf.pages[1:], 2):
            all_lines.extend(extract_column_text(page, 45, 306, 45, 740))
            all_lines.extend(extract_column_text(page, 306, 570, 45, 740))

    add_paragraphs(story, all_lines[:150], styles)
    add_table(story, "TABLE I: Dataset Characteristics", tables["dataset"], [1.38 * inch, 1.92 * inch])
    add_paragraphs(story, all_lines[150:310], styles)
    add_table(story, "TABLE II: Comparison of Evaluated Deep Learning Architectures", tables["architectures"], [1.05 * inch, 0.7 * inch, 0.85 * inch, 0.55 * inch])
    add_table(story, "TABLE III: EfficientNet-B0 Validation Performance", tables["clean"], [1.75 * inch, 0.9 * inch])
    add_paragraphs(story, all_lines[310:470], styles)
    add_table(story, "TABLE IV: Comparison of Implemented Backdoor Attacks", tables["attacks"], [0.85 * inch, 1.55 * inch, 0.7 * inch])
    add_paragraphs(story, all_lines[470:610], styles)
    add_table(story, "TABLE V: STRIP Detection Performance", tables["strip"], [1.75 * inch, 0.9 * inch])
    add_table(story, "TABLE VI: Fine-Tuning Configuration", [["Setting", "Value"], ["Learning Strategy", "Fine-Tuning"], ["Backbone", "EfficientNet-B0"], ["Input Size", "224x224"], ["Evaluation Metrics", "Accuracy, Precision, Recall, F1, MCC, ASR"]], [1.35 * inch, 1.95 * inch])
    add_table(story, "TABLE VII: Fine-Tuning Performance", tables["finetune"], [1.75 * inch, 0.9 * inch])
    add_paragraphs(story, all_lines[610:760], styles)
    add_table(story, "TABLE VIII: Clean Classification Performance", tables["clean"], [1.75 * inch, 0.9 * inch])
    add_table(story, "TABLE IX: STRIP Detection Performance", tables["strip"], [1.75 * inch, 0.9 * inch])
    add_table(story, "TABLE X: Fine-Tuning Performance", tables["finetune"], [1.75 * inch, 0.9 * inch])
    add_paragraphs(story, all_lines[760:], styles)

    story.append(PageBreak())
    story.append(Paragraph("Figures", styles["Section"]))
    fig_no = 1
    for page_no in sorted(figures):
        for fig in figures[page_no]:
            add_image(story, fig, f"Fig. {fig_no}: Extracted figure artwork from the original PDF.", styles)
            fig_no += 1

    doc.build(story)
    print(IEEE_OUT)


if __name__ == "__main__":
    main()
