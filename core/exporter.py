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
    def export_pdf(trace: ExecutionTrace, output_path: str, user_id: str = "Unknown"):
        """
        生成 Apple 风格的简约专业 PDF 报告。
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter, 
                                rightMargin=40, leftMargin=40, 
                                topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()
        
        # 定义 Apple 风格字体样式 (假设系统有类似 SF Pro 的字体，否则退而求其次)
        title_style = ParagraphStyle(
            'AppleTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.black,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold',
            spaceAfter=20
        )
        
        body_style = ParagraphStyle(
            'AppleBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor("#333333"),
            fontName='Helvetica',
            leading=16
        )
        
        meta_style = ParagraphStyle(
            'AppleMeta',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.gray,
            fontName='Helvetica'
        )

        elements = []

        # 标题
        elements.append(Paragraph("Execution Evidence", title_style))
        elements.append(Paragraph(f"USER: {user_id} | DATE: {trace.entries[0].timestamp[:10] if trace.entries else 'N/A'}", meta_style))
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey))
        elements.append(Spacer(1, 20))

        # 核心摘要
        summary_data = [
            ["Status", "Total Actions", "Total Cost", "Currency"],
            ["SUCCESS" if all(e.status.value == "SUCCESS" for e in trace.entries) else "FAILED", 
             len(trace.entries), f"{trace.total_cost:.4f}", "USD"]
        ]
        t = Table(summary_data, colWidths=[120, 120, 120, 120])
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

        # 详细步骤
        elements.append(Paragraph("Action Logs", styles['Heading2']))
        elements.append(Spacer(1, 10))
        
        for entry in trace.entries:
            # 每一个动作作为一个小卡片风格
            action_title = f"<b>{entry.action_id}</b> <font color='gray'>({entry.status.value})</font>"
            elements.append(Paragraph(action_title, body_style))
            
            # 缩进显示细节
            detail_text = f"Cost: {entry.cost:.4f} USD | Duration: {entry.metadata.get('duration_ms', 0):.2f}ms"
            elements.append(Paragraph(detail_text, meta_style))
            
            # 渲染结果摘要
            output_snippet = str(entry.payload)[:200] + "..." if len(str(entry.payload)) > 200 else str(entry.payload)
            elements.append(Paragraph(f"Result: {output_snippet}", body_style))
            
            elements.append(Spacer(1, 15))
            elements.append(HRFlowable(width="80%", thickness=0.2, color=colors.whitesmoke, dash=(2,2)))
            elements.append(Spacer(1, 15))

        # 页脚
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Artfish Runtime - Certified Execution Log", meta_style))

        doc.build(elements)
        return output_path

    @staticmethod
    def export_json(trace: ExecutionTrace, output_path: str):
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(trace.to_json())
        return output_path
