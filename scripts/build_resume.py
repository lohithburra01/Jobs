import os
import sys
import json
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib import colors

# --- CONFIGURATION ---
# Usage: python scripts/build_resume.py <application.json> <output-dir>

BLACK = colors.HexColor('#111111')
DARK  = colors.HexColor('#222222')
GREY  = colors.HexColor('#666666')

def clean(text):
    if not isinstance(text, str): return text
    return text.replace('—', '-').replace('–', '-')

def get_styles():
    s = getSampleStyleSheet()
    def add_style(name, base_name, **kwargs):
        if name in s: return s[name]
        new_style = ParagraphStyle(name, parent=s[base_name], **kwargs)
        s.add(new_style)
        return new_style

    # ULTRA-DENSE RESUME STYLES (8.5pt base, compressed leading)
    add_style('Name', 'Normal', fontName='Helvetica-Bold', fontSize=16, leading=18, alignment=TA_CENTER, spaceAfter=2)
    add_style('Contact', 'Normal', fontName='Helvetica', fontSize=8, leading=10, textColor=GREY, alignment=TA_CENTER, spaceAfter=2)
    add_style('Visa', 'Normal', fontName='Helvetica', fontSize=8.5, leading=10, alignment=TA_CENTER, spaceAfter=6)
    
    add_style('H1', 'Normal', fontName='Helvetica-Bold', fontSize=10, spaceBefore=6, spaceAfter=2, textColor=BLACK)
    
    add_style('Body', 'Normal', fontName='Helvetica', fontSize=8.5, leading=11, spaceAfter=2)
    add_style('BulletCustom', 'Normal', fontName='Helvetica', fontSize=8.5, leading=11, leftIndent=10, firstLineIndent=-10, spaceAfter=1.5)
    
    add_style('ItemH', 'Normal', fontName='Helvetica-Bold', fontSize=9, leading=10, spaceBefore=2)
    add_style('ItemComp', 'Normal', fontName='Helvetica-Oblique', fontSize=8.5, leading=10, textColor=DARK, spaceAfter=1)
    add_style('ItemDate', 'Normal', fontName='Helvetica', fontSize=8.5, leading=10, alignment=TA_RIGHT)
    
    # CL STYLES
    add_style('CL_Name', 'Normal', fontName='Helvetica-Bold', fontSize=15, leading=20, spaceAfter=2)
    add_style('CL_Contact', 'Normal', fontName='Helvetica', fontSize=8.5, leading=12, textColor=GREY, spaceAfter=20)
    add_style('CL_Body', 'Normal', fontName='Helvetica', fontSize=10, leading=15, alignment=TA_JUSTIFY, spaceAfter=12)
    
    return s

def make_resume(data, company, output_dir):
    path = os.path.join(output_dir, f"Lohith_Burra_{company}.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=0.5*inch, rightMargin=0.5*inch, topMargin=0.5*inch, bottomMargin=0.5*inch, compress=0)
    styles = get_styles()
    story = []

    def add_section_header(text):
        story.append(Paragraph(clean(text), styles['H1']))
        line = Table([['']], colWidths=[7.5*inch], rowHeights=[1])
        line.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,-1), 0.75, BLACK), ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)]))
        story.append(line)
        story.append(Spacer(1, 2))

    # Header
    story.append(Paragraph("Lohith Burra", styles['Name']))
    contact_str = 'Heilbronn, Germany | burralohith01@gmail.com | +49 1573 7742759 | <a href="https://linkedin.com/in/lohithburra"><font color="#1155CC">LinkedIn</font></a> | <a href="https://lohithburra.framer.website"><font color="#1155CC">Portfolio</font></a> | <a href="https://github.com/lohithburra01"><font color="#1155CC">GitHub</font></a>'
    story.append(Paragraph(contact_str, styles['Contact']))
    story.append(Paragraph("EU Chancenkarte visa - authorized to work in Germany/EU immediately, no sponsorship required", styles['Visa']))

    # Summary
    add_section_header("SUMMARY")
    story.append(Paragraph(clean(data['summary']), styles['Body']))

    # Skills
    add_section_header("CORE SKILLS")
    for sk in data['skills']:
        story.append(Paragraph(clean(f"<b>{sk['label']}:</b> {sk['value']}"), styles['Body']))

    # Experience
    add_section_header("PROFESSIONAL EXPERIENCE")
    for ex in data['experience']:
        t = Table([
            [Paragraph(clean(ex['title']), styles['ItemH']), Paragraph(clean(ex['period']), styles['ItemDate'])]
        ], colWidths=[6.0*inch, 1.5*inch])
        t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 0)]))
        
        block = [t, Paragraph(clean(ex['company']), styles['ItemComp'])]
        for b in ex['bullets']:
            block.append(Paragraph(clean(f"• {b}"), styles['BulletCustom']))
        story.append(KeepTogether(block))

    # Projects
    add_section_header("KEY PROJECTS")
    for pr in data['projects']:
        t = Table([
            [Paragraph(clean(pr['name']), styles['ItemH']), Paragraph(clean(pr['period']), styles['ItemDate'])]
        ], colWidths=[6.0*inch, 1.5*inch])
        t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('PADDING', (0,0), (-1,-1), 0)]))
        
        block = [t]
        for b in pr['bullets']:
            block.append(Paragraph(clean(f"• {b}"), styles['BulletCustom']))
        story.append(KeepTogether(block))

    # Education
    add_section_header("EDUCATION")
    for ed in data['education']:
        story.append(Paragraph(clean(f"<b>{ed['degree']}</b> - {ed['school']} ({ed['year']})"), styles['Body']))

    doc.build(story)
    return path

def make_cl(data, company, output_dir):
    path = os.path.join(output_dir, f"Lohith_Burra_{company}_CoverLetter.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter, leftMargin=1.1*inch, rightMargin=1.1*inch, topMargin=0.9*inch, bottomMargin=0.9*inch)
    styles = get_styles()
    story = []
    
    story.append(Paragraph("Lohith Burra", styles['CL_Name']))
    
    contact_parts = [
        'Heilbronn, Germany',
        'burralohith01@gmail.com', '+49 1573 7742759',
        '<a href="https://linkedin.com/in/lohithburra"><font color="#1155CC">LinkedIn</font></a>',
        '<a href="https://lohithburra.framer.website"><font color="#1155CC">Portfolio</font></a>',
        '<a href="https://github.com/lohithburra01"><font color="#1155CC">GitHub</font></a>'
    ]
    story.append(Paragraph(' | '.join(contact_parts), styles['CL_Contact']))
    
    story.append(Paragraph(clean(data['date']), styles['CL_Body']))
    addr = data['company_address'].replace('\n', '<br/>')
    story.append(Paragraph(clean(addr), styles['CL_Body']))
    
    story.append(Paragraph(clean(data['salutation']), styles['CL_Body']))
    for p in data['paragraphs']:
        story.append(Paragraph(clean(p), styles['CL_Body']))

    story.append(Spacer(1, 12))
    story.append(Paragraph("Best regards,<br/><br/><b>Lohith Burra</b>", styles['CL_Body']))
    doc.build(story)
    return path

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python scripts/build_resume.py <application.json> <output-dir>")
        sys.exit(1)

    json_input, output_dir = sys.argv[1], sys.argv[2]

    if not os.path.exists(json_input):
        print(f"Error: no such file: {json_input}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    with open(json_input, 'r', encoding='utf-8') as f:
        d = json.load(f)
    c_name = d['company_name'].replace(" ", "_")
    r = make_resume(d['resume'], c_name, output_dir)
    c = make_cl(d['cover_letter'], c_name, output_dir)
    print(f"Wrote: {r}")
    print(f"Wrote: {c}")