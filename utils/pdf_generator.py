from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
import io

def create_pdf_report(analysis_results):
    """
    Generate a PDF report from the ATS analysis results
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30
    )
    story.append(Paragraph("ATS Resume Analysis Report", title_style))
    story.append(Spacer(1, 12))

    # Overall Score
    score_style = ParagraphStyle(
        'Score',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=colors.HexColor('#2E7D32')
    )
    story.append(Paragraph(f"Overall Score: {analysis_results['overall_score']}%", score_style))
    story.append(Spacer(1, 12))

    # Section Scores
    story.append(Paragraph("Section Scores", styles['Heading2']))
    section_data = [[section, f"{score}%"] for section, score in analysis_results['section_scores'].items()]
    section_table = Table(
        [["Section", "Score"]] + section_data,
        colWidths=[4*inch, 2*inch]
    )
    section_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(section_table)
    story.append(Spacer(1, 20))

    # Format Analysis
    story.append(Paragraph("Format Analysis", styles['Heading2']))
    for item in analysis_results['format_analysis']:
        story.append(Paragraph(f"• {item}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Content Analysis
    story.append(Paragraph("Content Analysis", styles['Heading2']))
    for section, details in analysis_results['content_analysis'].items():
        story.append(Paragraph(section, styles['Heading3']))
        for detail in details:
            story.append(Paragraph(f"• {detail}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Recommendations
    story.append(Paragraph("Recommendations", styles['Heading2']))
    for category, recommendations in analysis_results['recommendations'].items():
        story.append(Paragraph(category, styles['Heading3']))
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", styles['Normal']))

    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
