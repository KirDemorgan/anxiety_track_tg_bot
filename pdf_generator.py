from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, date
from collections import defaultdict
import io
import os

class PDFGenerator:
    def __init__(self):
        try:
            font_paths = [
                '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Ubuntu/Debian
                '/System/Library/Fonts/Helvetica.ttc',  # macOS
                'C:/Windows/Fonts/arial.ttf',  # Windows
                '/usr/share/fonts/TTF/DejaVuSans.ttf',  # Arch Linux
            ]
            
            font_registered = False
            for font_path in font_paths:
                if os.path.exists(font_path):
                    pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
                    font_registered = True
                    break
            
            font_name = 'DejaVuSans' if font_registered else 'Helvetica'
            
        except Exception:
            font_name = 'Helvetica'
        
        self.styles = getSampleStyleSheet()
        
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=font_name,
            fontSize=16,
            spaceAfter=30,
            alignment=1, 
            encoding='utf-8'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontName=font_name,
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            encoding='utf-8'
        )
        
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontName=font_name,
            fontSize=10,
            spaceAfter=6,
            encoding='utf-8'
        )
    
    def generate_report(self, user_data: dict, user_id: int) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=18)
        
        story = []
        
        title = Paragraph("Отчет о приеме лекарств", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        pills_by_date = defaultdict(list)
        notes_by_date = defaultdict(list)
        
        for pill in user_data['pills']:
            pill_date = pill['taken_at'].date()
            pills_by_date[pill_date].append(pill)
        
        for note in user_data['notes']:
            note_date = note['created_at'].date()
            notes_by_date[note_date].append(note)
        
        all_dates = set(pills_by_date.keys()) | set(notes_by_date.keys())
        sorted_dates = sorted(all_dates)
        
        for current_date in sorted_dates:
            date_str = current_date.strftime("%d.%m.%Y")
            date_heading = Paragraph(f"<b>{date_str}</b>", self.heading_style)
            story.append(date_heading)
            
            if current_date in pills_by_date:
                pills_heading = Paragraph("Принятые лекарства:", self.normal_style)
                story.append(pills_heading)
                
                for pill in pills_by_date[current_date]:
                    time_str = pill['taken_at'].strftime("%H:%M")
                    pill_text = f"• {time_str} - {pill['pill_name']} ({pill['dose']})"
                    pill_para = Paragraph(pill_text, self.normal_style)
                    story.append(pill_para)
                
                story.append(Spacer(1, 6))
            
            if current_date in notes_by_date:
                notes_heading = Paragraph("Заметки о состоянии:", self.normal_style)
                story.append(notes_heading)
                
                for note in notes_by_date[current_date]:
                    time_str = note['created_at'].strftime("%H:%M")
                    note_text = f"• {time_str} - {note['note']}"
                    note_para = Paragraph(note_text, self.normal_style)
                    story.append(note_para)
                
                story.append(Spacer(1, 6))
            
            story.append(Spacer(1, 12))
        
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()