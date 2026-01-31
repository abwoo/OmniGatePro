from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from core.trace import ExecutionTrace
import json
import os

class Exporter:
    @staticmethod
    def export_pdf(trace: ExecutionTrace, output_path: str):
        """
        Generate a minimal execution report.
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter, 
                                rightMargin=40, leftMargin=40, 
                                topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=20
        )
        
        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            fontName='Helvetica',
            leading=14
        )
        
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            fontName='Helvetica'
        )

        elements = []

        # Title
        elements.append(Paragraph("Execution Report", title_style))
        date_str = trace.events[0].timestamp.strftime("%Y-%m-%d %H:%M:%S") if trace.events else 'N/A'
        elements.append(Paragraph(f"DATE: {date_str}", meta_style))
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        elements.append(Spacer(1, 20))

        # Summary
        summary_data = [
            ["Status", "Total Actions"],
            ["SUCCESS" if all(e.status.value in ["success", "completed"] for e in trace.events) else "FAILED", 
             len(trace.events)]
        ]
        t = Table(summary_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (-1,0), colors.gray),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 30))

        # Logs
        elements.append(Paragraph("Action Logs", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        for event in trace.events:
            action_title = f"<b>{event.action_id}</b> <font color='gray'>({event.status.value})</font>"
            elements.append(Paragraph(action_title, body_style))
            
            detail_text = f"Time: {event.timestamp.strftime('%H:%M:%S.%f')}"
            elements.append(Paragraph(detail_text, meta_style))
            
            output_snippet = str(event.result_payload)[:200] + "..." if len(str(event.result_payload)) > 200 else str(event.result_payload)
            elements.append(Paragraph(f"Result: {output_snippet}", body_style))
            
            elements.append(Spacer(1, 15))
            elements.append(HRFlowable(width="80%", thickness=0.2, color=colors.whitesmoke, dash=(2,2)))
            elements.append(Spacer(1, 15))

        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Artfish Runtime - Execution Log", meta_style))

        doc.build(elements)
        return output_path

    @staticmethod
    def export_json(trace: ExecutionTrace, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(trace.to_json())
        return output_path
