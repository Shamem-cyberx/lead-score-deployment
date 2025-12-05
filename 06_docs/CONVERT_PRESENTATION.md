# Converting Presentation to PPT/PDF

The presentation content is available in `presentation_slides.md` in Markdown format.

## Option 1: Using Pandoc (Recommended)

### Install Pandoc
```bash
# Windows (using Chocolatey)
choco install pandoc

# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc
```

### Convert to PowerPoint
```bash
pandoc presentation_slides.md -o RAKEZ_case_study_slides.pptx
```

### Convert to PDF
```bash
pandoc presentation_slides.md -o RAKEZ_case_study_slides.pdf
```

## Option 2: Using Online Tools

1. Copy content from `presentation_slides.md`
2. Use online Markdown to PPT converters:
   - https://www.markdowntopresentation.com/
   - https://gitpitch.com/
3. Or import to PowerPoint/Google Slides manually

## Option 3: Manual Creation

1. Open PowerPoint
2. Create 10 slides
3. Copy content from each slide section in `presentation_slides.md`
4. Add diagrams from `01_architecture/` folder
5. Export as PDF

## Option 4: Using Python (python-pptx)

```python
from pptx import Presentation
import re

# Read markdown file
with open('presentation_slides.md', 'r') as f:
    content = f.read()

# Split into slides
slides = content.split('---')

# Create presentation
prs = Presentation()

for slide_content in slides:
    if slide_content.strip():
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        title, body = slide_content.split('\n', 1)
        slide.shapes.title.text = title.replace('#', '').strip()
        slide.placeholders[1].text = body.strip()

prs.save('RAKEZ_case_study_slides.pptx')
```

## Note

The Mermaid diagrams in the architecture folder can be:
1. Rendered online at https://mermaid.live/
2. Exported as PNG
3. Inserted into PowerPoint slides

