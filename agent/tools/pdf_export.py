"""
PDF 导出工具：把 Markdown 报告转成 PDF
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# 注册中文字体（Windows 自带的宋体）
def _register_chinese_font():
    try:
        font_path = "C:/Windows/Fonts/simsun.ttc"
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont("Chinese", font_path))
            return "Chinese"
    except Exception:
        pass
    return "Helvetica"


def markdown_to_pdf(markdown_text: str, output_path: str):
    """
    把 Markdown 文本转成 PDF
    简单实现：按行解析标题、段落
    """
    font_name = _register_chinese_font()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()

    # 自定义样式
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontName=font_name,
        fontSize=20,
        spaceAfter=20,
    )
    h2_style = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName=font_name,
        fontSize=16,
        spaceBefore=15,
        spaceAfter=10,
    )
    h3_style = ParagraphStyle(
        "H3",
        parent=styles["Heading3"],
        fontName=font_name,
        fontSize=13,
        spaceBefore=10,
        spaceAfter=5,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontName=font_name,
        fontSize=11,
        leading=18,
        spaceAfter=8,
    )

    story = []

    lines = markdown_text.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
            continue

        if line.startswith("# "):
            story.append(Paragraph(line[2:], title_style))
        elif line.startswith("## "):
            story.append(Paragraph(line[3:], h2_style))
        elif line.startswith("### "):
            story.append(Paragraph(line[4:], h3_style))
        elif line.startswith("- "):
            # 列表项
            story.append(Paragraph(f"• {line[2:]}", body_style))
        else:
            story.append(Paragraph(line, body_style))

    doc.build(story)
    return output_path
