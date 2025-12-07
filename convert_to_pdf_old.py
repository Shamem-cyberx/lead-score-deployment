"""
Convert Markdown files to PDF
Supports both presentation slides and detailed documents
"""

import os
import re
import sys
from pathlib import Path

try:
    import markdown
    from markdown.extensions import codehilite, tables, fenced_code
except ImportError:
    print("Installing required packages...")
    os.system("pip install markdown weasyprint")
    import markdown
    from markdown.extensions import codehilite, tables, fenced_code

try:
    from xhtml2pdf import pisa
except ImportError:
    print("Installing xhtml2pdf...")
    os.system("pip install xhtml2pdf")
    from xhtml2pdf import pisa


def preprocess_markdown(content: str, is_presentation: bool = False) -> str:
    """Preprocess markdown content for better PDF rendering"""
    
    # Handle Mermaid diagrams - replace with note
    mermaid_pattern = r'```mermaid\n(.*?)\n```'
    
    def replace_mermaid(match):
        diagram_content = match.group(1)
        # Extract diagram type
        if 'graph' in diagram_content or 'flowchart' in diagram_content:
            diagram_type = "Architecture Diagram"
        elif 'sequenceDiagram' in diagram_content:
            diagram_type = "Sequence Diagram"
        elif 'stateDiagram' in diagram_content:
            diagram_type = "State Diagram"
        else:
            diagram_type = "Diagram"
        
        return f'\n\n<div style="background-color: #f0f0f0; padding: 20px; border-left: 4px solid #3498db; margin: 20px 0;">\n<strong>📊 {diagram_type}</strong><br/>\n<i>See ARCHITECTURE_DIAGRAMS.md for visual version</i>\n</div>\n\n'
    
    content = re.sub(mermaid_pattern, replace_mermaid, content, flags=re.DOTALL)
    
    # For presentations, split by slide markers and wrap in slide divs
    if is_presentation:
        # Remove the header line "## 10-Slide Presentation"
        content = re.sub(r'^##\s+10-Slide Presentation\s*$', '', content, flags=re.MULTILINE)
        
        # Split by slide separators (---)
        slides = content.split('---')
        processed_slides = []
        
        for slide in slides:
            slide = slide.strip()
            if slide and len(slide) > 10:  # Only process non-empty slides
                # Clean up any extra whitespace
                slide = re.sub(r'\n{3,}', '\n\n', slide)  # Replace 3+ newlines with 2
                
                # Wrap each slide in a div with slide class and page break
                processed_slides.append(f'<div class="slide" style="page-break-after: always; page-break-inside: avoid;">{slide}</div>')
        
        content = '\n\n'.join(processed_slides)
    
    return content


def markdown_to_html(md_content: str, title: str = "Document", is_presentation: bool = False) -> str:
    """Convert markdown to HTML"""
    
    # Configure markdown extensions
    md = markdown.Markdown(extensions=[
        'codehilite',
        'tables',
        'fenced_code',
        'nl2br',
        'sane_lists'
    ])
    
    html_body = md.convert(md_content)
    
    # Presentation-specific page settings
    if is_presentation:
        page_size = "A4 landscape"
        page_margin = "1.5cm"
        slide_style = """
        .slide {
            page-break-after: always !important;
            page-break-inside: avoid !important;
            min-height: 100vh;
            padding: 50px 70px;
            box-sizing: border-box;
        }
        .slide h1 {
            font-size: 3.2em !important;
            text-align: center;
            margin: 30px 0 40px 0;
            color: #2c3e50;
            border-bottom: 5px solid #3498db;
            padding-bottom: 25px;
            font-weight: bold;
        }
        .slide h2 {
            font-size: 2.6em !important;
            color: #34495e;
            margin: 25px 0 30px 0;
            border-bottom: 3px solid #95a5a6;
            padding-bottom: 15px;
            font-weight: bold;
        }
        .slide h3 {
            font-size: 1.9em !important;
            color: #555;
            margin: 20px 0 15px 0;
            font-weight: bold;
        }
        .slide h4 {
            font-size: 1.6em !important;
            color: #666;
            margin: 15px 0 12px 0;
            font-weight: bold;
        }
        .slide ul, .slide ol {
            font-size: 1.4em !important;
            line-height: 2.0;
            margin: 20px 0;
            padding-left: 50px;
        }
        .slide li {
            margin: 15px 0;
        }
        .slide p {
            font-size: 1.4em !important;
            line-height: 1.8;
            margin: 18px 0;
        }
        .slide strong {
            font-size: 1.1em;
            font-weight: bold;
        }
        .slide code {
            font-size: 1.2em;
            background-color: #f4f4f4;
            padding: 4px 8px;
        }
        .slide pre {
            font-size: 1.1em;
            padding: 20px;
            margin: 25px 0;
            background-color: #f8f8f8;
            border: 2px solid #ddd;
        }
        .slide table {
            font-size: 1.2em;
            margin: 25px 0;
        }
        .slide th {
            font-size: 1.2em;
            padding: 15px;
        }
        .slide td {
            font-size: 1.1em;
            padding: 12px;
        }
        """
    else:
        page_size = "A4"
        page_margin = "2cm"
        slide_style = ""
    
    # Create full HTML document
    html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @page {{
            size: {page_size};
            margin: {page_margin};
        }}
        
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
        }}
        
        {slide_style}
        
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            page-break-after: avoid;
            {'font-size: 3em; text-align: center; margin: 20px 0;' if is_presentation else ''}
        }}
        
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 30px;
            page-break-after: avoid;
            {'font-size: 2.4em; margin-top: 15px; margin-bottom: 20px;' if is_presentation else ''}
        }}
        
        h3 {{
            color: #555;
            margin-top: 20px;
            page-break-after: avoid;
            {'font-size: 1.8em; margin-top: 15px; margin-bottom: 12px; font-weight: bold;' if is_presentation else ''}
        }}
        
        h4 {{
            color: #666;
            margin-top: 15px;
            page-break-after: avoid;
            {'font-size: 1.5em; margin-top: 12px; margin-bottom: 10px;' if is_presentation else ''}
        }}
        
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        pre {{
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            page-break-inside: avoid;
        }}
        
        pre code {{
            background-color: transparent;
            padding: 0;
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
            text-align: left;
        }}
        
        th {{
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
            {'font-size: 1.3em; line-height: 1.8;' if is_presentation else ''}
        }}
        
        li {{
            margin: 8px 0;
            {'margin: 12px 0;' if is_presentation else ''}
        }}
        
        blockquote {{
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding-left: 20px;
            color: #555;
            font-style: italic;
        }}
        
        strong {{
            color: #2c3e50;
            font-weight: bold;
        }}
        
        em {{
            color: #555;
        }}
        
        hr {{
            border: none;
            border-top: 2px solid #ddd;
            margin: 30px 0;
        }}
        
        .page-break {{
            page-break-after: always;
        }}
        
        .footer {{
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            text-align: center;
            font-size: 0.8em;
            color: #999;
            padding: 10px;
        }}
        
        /* Better spacing for presentations */
        {'p { font-size: 1.3em; line-height: 1.7; margin: 12px 0; }' if is_presentation else ''}
        {'strong { font-size: 1.1em; }' if is_presentation else ''}
        {'code { font-size: 1.1em; padding: 4px 8px; }' if is_presentation else ''}
        {'pre { font-size: 1em; padding: 20px; }' if is_presentation else ''}
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
    
    # Read markdown file
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Get title from first heading or filename
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    if title_match:
        title = title_match.group(1)
    else:
        title = Path(md_file).stem.replace('_', ' ').title()
    
    print(f"📝 Processing: {title}")
    
    # Preprocess markdown
    md_content = preprocess_markdown(md_content, is_presentation)
    
    # Convert to HTML
    print("🔄 Converting to HTML...")
    html_content = markdown_to_html(md_content, title, is_presentation)
    
    # Save HTML (for debugging)
    html_file = output_pdf.replace('.pdf', '.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"💾 HTML saved: {html_file}")
    
    # Convert HTML to PDF
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
        print(f"   You can open it in a browser and print to PDF")
        return False


def main():
    """Main conversion function"""
    
    base_dir = Path(__file__).parent
    
    print("=" * 60)
    print("RAKEZ Case Study - Markdown to PDF Converter")
    print("=" * 60)
    print()
    
    # File 1: Presentation Slides
    presentation_md = base_dir / "06_docs" / "presentation_slides.md"
    presentation_pdf = base_dir / "06_docs" / "RAKEZ_Presentation_Slides.pdf"
    
    if presentation_md.exists():
        print("\n" + "=" * 60)
        print("Converting Presentation Slides...")
        print("=" * 60)
        convert_markdown_to_pdf(str(presentation_md), str(presentation_pdf), is_presentation=True)
    else:
        print(f"❌ File not found: {presentation_md}")
    
    # File 2: Case Study Document
    case_study_md = base_dir / "RAKEZ_CASE_STUDY_FINAL.md"
    case_study_pdf = base_dir / "RAKEZ_Case_Study_Final.pdf"
    
    if case_study_md.exists():
        print("\n" + "=" * 60)
        print("Converting Case Study Document...")
        print("=" * 60)
        convert_markdown_to_pdf(str(case_study_md), str(case_study_pdf), is_presentation=False)
    else:
        print(f"❌ File not found: {case_study_md}")
    
    print("\n" + "=" * 60)
    print("✅ Conversion Complete!")
    print("=" * 60)
    print(f"\n📄 PDFs saved in: {base_dir}")
    print(f"   - Presentation: {presentation_pdf.name}")
    print(f"   - Case Study: {case_study_pdf.name}")
    print("\n💡 Note: Mermaid diagrams are replaced with notes.")
    print("   For visual diagrams, see: 06_docs/ARCHITECTURE_DIAGRAMS.md")


if __name__ == "__main__":
    main()

