"""
Enhanced Markdown to PDF Converter
Optimized for presentation slides with better formatting
"""

import os
import re
import sys
from pathlib import Path

try:
    import markdown
    from markdown.extensions import codehilite, tables, fenced_code
except ImportError:
    print("Installing markdown...")
    os.system("pip install markdown")
    import markdown
    from markdown.extensions import codehilite, tables, fenced_code

try:
    from xhtml2pdf import pisa
except ImportError:
    print("Installing xhtml2pdf...")
    os.system("pip install xhtml2pdf")
    from xhtml2pdf import pisa


def preprocess_presentation(content: str) -> str:
    """Preprocess presentation markdown for better slide separation"""
    
    # Remove header line
    content = re.sub(r'^#\s+.*?10-Slide Presentation.*?\n', '', content, flags=re.MULTILINE)
    
    # Handle Mermaid diagrams
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    def replace_mermaid(match):
        diagram_content = match.group(1)
        if 'graph' in diagram_content or 'flowchart' in diagram_content:
            diagram_type = "Architecture Diagram"
        elif 'sequenceDiagram' in diagram_content:
            diagram_type = "Sequence Diagram"
        elif 'stateDiagram' in diagram_content:
            diagram_type = "State Diagram"
        else:
            diagram_type = "Diagram"
        
        return f'\n\n<div style="background-color: #e8f4f8; padding: 25px; border: 3px solid #3498db; border-radius: 8px; margin: 25px 0; text-align: center;">\n<h3 style="color: #2c3e50; margin: 0 0 10px 0;">📊 {diagram_type}</h3>\n<p style="color: #555; margin: 0; font-style: italic;">See ARCHITECTURE_DIAGRAMS.md for visual version</p>\n</div>\n\n'
    
    content = re.sub(mermaid_pattern, replace_mermaid, content, flags=re.DOTALL)
    
    # Split by slide separators (---)
    slides = content.split('---')
    processed_slides = []
    
    for slide in slides:
        slide = slide.strip()
        if slide and len(slide) > 10:
            # Clean up whitespace
            slide = re.sub(r'\n{3,}', '\n\n', slide)
            # Wrap in slide div with explicit page break
            processed_slides.append(f'<div class="slide-page">{slide}</div>')
    
    return '\n'.join(processed_slides)


def create_presentation_html(md_content: str, title: str) -> str:
    """Create HTML for presentation with optimized styling"""
    
    # Convert markdown to HTML
    md = markdown.Markdown(extensions=[
        'codehilite',
        'tables',
        'fenced_code',
        'nl2br',
        'sane_lists'
    ])
    
    html_body = md.convert(md_content)
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4 landscape;
            margin: 1.2cm;
        }}
        
        * {{
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            margin: 0;
            padding: 0;
            color: #2c3e50;
        }}
        
        .slide-page {{
            page-break-after: always;
            page-break-inside: avoid;
            min-height: 100vh;
            padding: 60px 80px;
            display: block;
        }}
        
        .slide-page:last-child {{
            page-break-after: auto;
        }}
        
        .slide-page h1 {{
            font-size: 3.5em !important;
            text-align: center;
            color: #2c3e50;
            margin: 40px 0 50px 0;
            padding-bottom: 30px;
            border-bottom: 6px solid #3498db;
            font-weight: bold;
            line-height: 1.2;
        }}
        
        .slide-page h2 {{
            font-size: 2.8em !important;
            color: #34495e;
            margin: 30px 0 35px 0;
            padding-bottom: 20px;
            border-bottom: 4px solid #95a5a6;
            font-weight: bold;
            line-height: 1.3;
        }}
        
        .slide-page h3 {{
            font-size: 2.0em !important;
            color: #555;
            margin: 25px 0 20px 0;
            font-weight: bold;
            line-height: 1.4;
        }}
        
        .slide-page h4 {{
            font-size: 1.7em !important;
            color: #666;
            margin: 20px 0 15px 0;
            font-weight: bold;
        }}
        
        .slide-page p {{
            font-size: 1.5em !important;
            line-height: 1.8;
            margin: 20px 0;
            color: #333;
        }}
        
        .slide-page ul, .slide-page ol {{
            font-size: 1.5em !important;
            line-height: 2.0;
            margin: 25px 0;
            padding-left: 60px;
        }}
        
        .slide-page li {{
            margin: 18px 0;
            color: #333;
        }}
        
        .slide-page strong {{
            color: #2c3e50;
            font-weight: bold;
            font-size: 1.05em;
        }}
        
        .slide-page code {{
            background-color: #f4f4f4;
            padding: 5px 10px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 1.2em;
            color: #e74c3c;
        }}
        
        .slide-page pre {{
            background-color: #f8f8f8;
            border: 2px solid #ddd;
            border-radius: 6px;
            padding: 25px;
            margin: 30px 0;
            overflow-x: auto;
            font-size: 1.1em;
        }}
        
        .slide-page pre code {{
            background-color: transparent;
            padding: 0;
            color: #333;
        }}
        
        .slide-page table {{
            width: 100%;
            border-collapse: collapse;
            margin: 30px 0;
            font-size: 1.3em;
        }}
        
        .slide-page th {{
            background-color: #3498db;
            color: white;
            padding: 18px;
            text-align: left;
            font-weight: bold;
            font-size: 1.1em;
        }}
        
        .slide-page td {{
            border: 1px solid #ddd;
            padding: 15px;
            text-align: left;
        }}
        
        .slide-page tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        .slide-page blockquote {{
            border-left: 5px solid #3498db;
            margin: 25px 0;
            padding: 20px 30px;
            background-color: #f0f8ff;
            font-style: italic;
            font-size: 1.4em;
        }}
        
        .slide-page hr {{
            border: none;
            border-top: 3px solid #ddd;
            margin: 40px 0;
        }}
        
        /* Special styling for title slide */
        .slide-page:first-child h1 {{
            font-size: 4.5em !important;
            margin: 80px 0 60px 0;
        }}
        
        .slide-page:first-child p {{
            font-size: 2.0em !important;
            text-align: center;
            margin: 30px 0;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""
    
    return html_template


def create_document_html(md_content: str, title: str) -> str:
    """Create HTML for document with standard styling"""
    
    md = markdown.Markdown(extensions=[
        'codehilite',
        'tables',
        'fenced_code',
        'nl2br',
        'sane_lists'
    ])
    
    html_body = md.convert(md_content)
    
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-after: avoid;
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
            page-break-after: avoid;
        }}
        
        h3 {{
            color: #555;
            margin-top: 20px;
            page-break-after: avoid;
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
        
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            page-break-inside: avoid;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            page-break-inside: avoid;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        li {{
            margin: 8px 0;
        }}
    </style>
</head>
<body>
    {html_body}
</body>
</html>"""
    
    return html_template


def convert_markdown_to_pdf(md_file: str, output_pdf: str, is_presentation: bool = False):
    """Convert markdown file to PDF"""
    
    print(f"📄 Reading: {md_file}")
    
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Get title
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = Path(md_file).stem.replace('_', ' ').title()
    
    print(f"📝 Processing: {title}")
    
    # Preprocess
    if is_presentation:
        md_content = preprocess_presentation(md_content)
        html_content = create_presentation_html(md_content, title)
    else:
        html_content = create_document_html(md_content, title)
    
    # Save HTML
    html_file = output_pdf.replace('.pdf', '.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"💾 HTML saved: {html_file}")
    
    # Convert to PDF
    print("📄 Generating PDF...")
    try:
        with open(output_pdf, 'w+b') as pdf_file:
            pisa_status = pisa.CreatePDF(
                html_content,
                dest=pdf_file,
                encoding='utf-8'
            )
        
        if pisa_status.err:
            raise Exception(f"PDF creation error: {pisa_status.err}")
        
        print(f"✅ PDF created successfully: {output_pdf}")
        return True
    except Exception as e:
        print(f"❌ Error creating PDF: {e}")
        print(f"   HTML file saved at: {html_file}")
        print(f"   You can open it in a browser and print to PDF (Ctrl+P)")
        return False


def main():
    """Main conversion function"""
    
    base_dir = Path(__file__).parent
    
    print("=" * 70)
    print("RAKEZ Case Study - Enhanced PDF Converter")
    print("=" * 70)
    print()
    
    # Presentation Slides
    presentation_md = base_dir / "06_docs" / "presentation_slides.md"
    presentation_pdf = base_dir / "06_docs" / "RAKEZ_Presentation_Slides.pdf"
    
    if presentation_md.exists():
        print("\n" + "=" * 70)
        print("Converting Presentation Slides (Landscape Format)...")
        print("=" * 70)
        convert_markdown_to_pdf(str(presentation_md), str(presentation_pdf), is_presentation=True)
    else:
        print(f"❌ File not found: {presentation_md}")
    
    # Case Study Document
    case_study_md = base_dir / "RAKEZ_CASE_STUDY_FINAL.md"
    case_study_pdf = base_dir / "RAKEZ_Case_Study_Final.pdf"
    
    if case_study_md.exists():
        print("\n" + "=" * 70)
        print("Converting Case Study Document (Portrait Format)...")
        print("=" * 70)
        convert_markdown_to_pdf(str(case_study_md), str(case_study_pdf), is_presentation=False)
    else:
        print(f"❌ File not found: {case_study_md}")
    
    print("\n" + "=" * 70)
    print("✅ Conversion Complete!")
    print("=" * 70)
    print(f"\n📄 PDFs saved:")
    print(f"   - Presentation: {presentation_pdf}")
    print(f"   - Case Study: {case_study_pdf}")
    print("\n💡 Tips:")
    print("   - Presentation is in LANDSCAPE format (A4 landscape)")
    print("   - Each slide is on a separate page")
    print("   - Mermaid diagrams show as notes (see ARCHITECTURE_DIAGRAMS.md)")
    print("   - If PDF looks wrong, check the HTML file in browser first")


if __name__ == "__main__":
    main()

