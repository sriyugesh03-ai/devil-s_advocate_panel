from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def get_pdf_styles():
    styles = getSampleStyleSheet()

    # Custom palette
    primary_color = colors.HexColor("#BE123C")   # Rose 700
    dark_bg = colors.HexColor("#0F172A")         # Slate 900
    text_dark = colors.HexColor("#1E293B")       # Slate 800
    subtext = colors.HexColor("#475569")         # Slate 600

    styles.add(ParagraphStyle(
        name='PanelTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name='PanelSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=dark_bg,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name='SectionHeader',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8
    ))

    styles.add(ParagraphStyle(
        name='BodyRegular',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=text_dark,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='ReasoningBox',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        textColor=subtext,
        spaceAfter=6
    ))

    styles.add(ParagraphStyle(
        name='QuestionHighlight',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#9F1239"),
        spaceAfter=6
    ))

    return styles
