"""Generate the sample earnings-call PDFs into data/pdfs/.

Run:  python scripts/generate_sample_pdfs.py

The repository already contains the generated PDFs, so you only need this if
you change scripts/transcripts.py or want to recreate them.
"""
from pathlib import Path
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from xml.sax.saxutils import escape

from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from transcripts import TRANSCRIPTS  # noqa: E402

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "pdfs"
DISCLAIMER = ("FICTIONAL SAMPLE DOCUMENT - generated for a software demo. "
              "The company and all figures are invented.")


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica-Oblique", 7)
    canvas.drawString(2 * cm, 1.2 * cm, DISCLAIMER)
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build(t: dict) -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / t["file"]
    styles = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10.5, leading=15, spaceAfter=8)
    story = [
        Paragraph(t["title"], styles["Title"]),
        Paragraph(t["date"], styles["Italic"]),
        Spacer(1, 12),
    ]
    for speaker, paragraphs in t["sections"]:
        story.append(Paragraph(speaker, styles["Heading2"]))
        story.extend(Paragraph(escape(p), body) for p in paragraphs)
    doc = SimpleDocTemplate(str(path), pagesize=A4, title=t["title"], author=t["company"],
                            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
    return path


if __name__ == "__main__":
    for t in TRANSCRIPTS:
        print("wrote", build(t))
