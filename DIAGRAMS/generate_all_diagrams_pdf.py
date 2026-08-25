"""Generate All_Diagrams.pdf from the PNG/JPG diagrams in this folder.

Each diagram image is placed on its own A4 landscape page with a centred title
at the top. UI mock designs are appended after the sequence diagrams.
"""

from pathlib import Path

from PIL import Image
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

DIAGRAMS_DIR = Path(__file__).resolve().parent
OUTPUT_PDF = DIAGRAMS_DIR / "All_Diagrams.pdf"

# Ordered list of (title, image path) pairs to place in the PDF.
PAGES = [
    ("Class Diagram", DIAGRAMS_DIR / "CLASS" / "CLASS_DIAGRAM.png"),
    ("ERD Diagram", DIAGRAMS_DIR / "ERD DIAGRAM" / "ERD_DIAGRAM.png"),
    ("Use Case Diagram", DIAGRAMS_DIR / "USE CASE" / "USE_CASE_DIAGRAM.png"),
    ("Sequence Diagram 1", DIAGRAMS_DIR / "SEQUENCE" / "SEQUENCE_DIAGRAM_1.png"),
    ("Sequence Diagram 2", DIAGRAMS_DIR / "SEQUENCE" / "SEQUENCE_DIAGRAM_2.png"),
    ("Sequence Diagram 3", DIAGRAMS_DIR / "SEQUENCE" / "SEQUENCE_DIAGRAM_3.png"),
    ("Sequence Diagram 4", DIAGRAMS_DIR / "SEQUENCE" / "SEQUENCE_DIAGRAM_4.png"),
    ("Sequence Diagram 5", DIAGRAMS_DIR / "SEQUENCE" / "SEQUENCE_DIAGRAM_5.png"),
    ("Sequence Diagram 6", DIAGRAMS_DIR / "SEQUENCE" / "SEQUENCE_DIAGRAM_6.png"),
    ("UI Mock Design - Login Window", DIAGRAMS_DIR / "UI_MOCK_DESIGNS" / "ASD_Login_window.jpg"),
    ("UI Mock Design - Manager Dashboard", DIAGRAMS_DIR / "UI_MOCK_DESIGNS" / "ASD_Manager_Dashboard.jpg"),
    ("UI Mock Design - Tenant Profile", DIAGRAMS_DIR / "UI_MOCK_DESIGNS" / "ASD_Tenant_Profile.jpg"),
]

PAGE_SIZE = landscape(A4)
PAGE_WIDTH, PAGE_HEIGHT = PAGE_SIZE
MARGIN = 15 * mm
TITLE_AREA_HEIGHT = 25 * mm


def draw_page(pdf: canvas.Canvas, title: str, image_path: Path) -> None:
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(
        PAGE_WIDTH / 2,
        PAGE_HEIGHT - MARGIN - 5 * mm,
        title,
    )

    with Image.open(image_path) as img:
        img_w, img_h = img.size

    available_w = PAGE_WIDTH - 2 * MARGIN
    available_h = PAGE_HEIGHT - 2 * MARGIN - TITLE_AREA_HEIGHT
    scale = min(available_w / img_w, available_h / img_h)
    draw_w = img_w * scale
    draw_h = img_h * scale
    x = (PAGE_WIDTH - draw_w) / 2
    y = MARGIN + (available_h - draw_h) / 2

    pdf.drawImage(
        str(image_path),
        x,
        y,
        width=draw_w,
        height=draw_h,
        preserveAspectRatio=True,
        mask="auto",
    )


def main() -> None:
    pdf = canvas.Canvas(str(OUTPUT_PDF), pagesize=PAGE_SIZE)
    for title, image_path in PAGES:
        if not image_path.exists():
            raise FileNotFoundError(f"Missing diagram image: {image_path}")
        draw_page(pdf, title, image_path)
        pdf.showPage()
    pdf.save()
    print(f"Wrote {OUTPUT_PDF} ({len(PAGES)} pages)")


if __name__ == "__main__":
    main()
