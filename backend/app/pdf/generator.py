import io
import os
import logging
from typing import Dict, Any, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether
)
from backend.app.pdf.styles import get_pdf_styles

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generates an executive investment-grade diagnostic PDF report."""

    def __init__(self):
        self.styles = get_pdf_styles()

    def generate_report(self, session_data: Dict[str, Any]) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        elements = []
        pitch = session_data.get("pitch", {})
        verdict = session_data.get("verdict", {})
        rounds_history = session_data.get("rounds_history", [])

        # Header Title
        elements.append(Paragraph("DEVIL'S ADVOCATE PANEL", self.styles['PanelTitle']))
        elements.append(Paragraph("Adversarial Startup Stress Test & Investment Diagnostic Report", self.styles['PanelSubtitle']))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#BE123C"), spaceAfter=15))

        # Pitch Metadata Table
        pitch_info = [
            [
                Paragraph("<b>Startup Name:</b>", self.styles['BodyRegular']),
                Paragraph(str(pitch.get("title", "N/A")), self.styles['BodyRegular']),
                Paragraph("<b>Overall Score:</b>", self.styles['BodyRegular']),
                Paragraph(f"<b>{verdict.get('overall_score', 'N/A')}/100</b>", self.styles['QuestionHighlight'])
            ],
            [
                Paragraph("<b>Tagline:</b>", self.styles['BodyRegular']),
                Paragraph(str(pitch.get("tagline", "N/A")), self.styles['BodyRegular']),
                Paragraph("<b>Recommendation:</b>", self.styles['BodyRegular']),
                Paragraph(str(verdict.get("investment_recommendation", "N/A")), self.styles['BodyRegular'])
            ],
            [
                Paragraph("<b>Business Model:</b>", self.styles['BodyRegular']),
                Paragraph(str(pitch.get("business_model", "N/A")), self.styles['BodyRegular']),
                Paragraph("<b>24-Mo Survival Odds:</b>", self.styles['BodyRegular']),
                Paragraph(f"{verdict.get('survival_odds_percentage', 'N/A')}%", self.styles['BodyRegular'])
            ]
        ]
        t = Table(pitch_info, colWidths=[110, 200, 110, 120])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#CBD5E1")),
            ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 15))

        # Executive Summary
        if verdict.get("executive_summary"):
            elements.append(Paragraph("1. Executive Summary & Investment Verdict", self.styles['SectionHeader']))
            elements.append(Paragraph(verdict.get("executive_summary", ""), self.styles['BodyRegular']))
            elements.append(Spacer(1, 10))

        # Persona Scores Breakdown
        persona_scores = verdict.get("persona_scores", [])
        if persona_scores:
            elements.append(Paragraph("2. Persona Scorecard", self.styles['SectionHeader']))
            score_data = [["Persona", "Score", "Verdict", "Key Assessment"]]
            for ps in persona_scores:
                score_data.append([
                    Paragraph(f"<b>{ps.get('persona')}</b>", self.styles['BodyRegular']),
                    Paragraph(f"<b>{ps.get('score')}/100</b>", self.styles['BodyRegular']),
                    Paragraph(ps.get('verdict', ''), self.styles['BodyRegular']),
                    Paragraph(ps.get('key_takeaway', ''), self.styles['BodyRegular'])
                ])
            st = Table(score_data, colWidths=[120, 60, 90, 270])
            st.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#BE123C")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('ALIGN', (1,0), (1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            elements.append(st)
            elements.append(Spacer(1, 12))

        # Ranked Weaknesses & Recommended Fixes
        ranked_weaknesses = verdict.get("ranked_weaknesses", [])
        if ranked_weaknesses:
            elements.append(Paragraph("3. Ranked Weaknesses & Actionable Mitigations", self.styles['SectionHeader']))
            for w in ranked_weaknesses:
                w_elements = [
                    Paragraph(f"<b>[{w.get('severity', 'HIGH').upper()}] {w.get('title')}</b> <i>({w.get('category')})</i>", self.styles['QuestionHighlight']),
                    Paragraph(f"<b>Risk:</b> {w.get('description')}", self.styles['BodyRegular']),
                    Paragraph(f"<b>Prescribed Fix:</b> {w.get('recommended_fix')}", self.styles['BodyRegular']),
                    Spacer(1, 6)
                ]
                elements.append(KeepTogether(w_elements))
            elements.append(Spacer(1, 10))

        # Multi-Round Interrogation Transcript
        if rounds_history:
            elements.append(Paragraph("4. Complete Adversarial Round Transcripts", self.styles['SectionHeader']))
            for r in rounds_history:
                r_num = r.get("round_number", 1)
                elements.append(Paragraph(f"<b>--- ROUND {r_num} GAUNTLET ---</b>", self.styles['PanelSubtitle']))
                
                challenges = r.get("challenges", [])
                for ch in challenges:
                    elements.append(Paragraph(f"<b>{ch.get('persona')} [Severity: {ch.get('severity', 'High')}]:</b>", self.styles['BodyRegular']))
                    if ch.get("reasoning_summary"):
                        elements.append(Paragraph(f"<i>Reasoning:</i> {ch.get('reasoning_summary')}", self.styles['ReasoningBox']))
                    elements.append(Paragraph(f"<b>Challenge:</b> {ch.get('question')}", self.styles['QuestionHighlight']))
                    elements.append(Spacer(1, 4))

                elements.append(Paragraph("<b>Founder's Rebuttal:</b>", self.styles['BodyRegular']))
                elements.append(Paragraph(f"\"{r.get('founder_response', 'No response recorded.')}\"", self.styles['BodyRegular']))
                elements.append(Spacer(1, 10))

        doc.build(elements)
        buffer.seek(0)
        return buffer

pdf_generator = PDFReportGenerator()
