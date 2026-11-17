#!/bin/bash
# Step 3: export the deck to PDF (LibreOffice, headless) and render each slide to PNG.
set -e
cd "$(dirname "$0")"
SOFFICE=${SOFFICE:-/Applications/LibreOffice.app/Contents/MacOS/soffice}
"$SOFFICE" --headless --convert-to pdf output/Netflix_Music_AI_Experience_Report.pptx --outdir output >/dev/null 2>&1
python3 render_slides.py output/Netflix_Music_AI_Experience_Report.pdf output/slides
