"""Script to generate test PDF files for parser tests."""

from pathlib import Path
from typing import Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# Create test data directory
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)


def create_simple_pdf():
    """Create a simple valid PDF file."""
    filename = data_dir / "valid_resume.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)

    # Container for the 'Flowable' object
    elements: List[Any] = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # Add content
    elements.append(Paragraph("Test Resume", title_style))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("John Doe", normal_style))
    elements.append(Paragraph("Email: john.doe@example.com", normal_style))
    elements.append(Paragraph("Phone: +1-234-567-8900", normal_style))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Experience", heading_style))
    elements.append(Paragraph("Software Engineer at Tech Company", normal_style))
    elements.append(
        Paragraph(
            "Worked on various projects using Python, Java, and JavaScript.",
            normal_style,
        )
    )
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Skills", heading_style))
    elements.append(Paragraph("Python, Java, JavaScript, SQL, Git", normal_style))

    # Build PDF
    doc.build(elements)
    print(f"Created {filename.name}")


def create_pdf_with_tables():
    """Create a PDF with tables."""
    filename = data_dir / "with_tables.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)

    elements: List[Any] = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Resume with Tables", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))

    # Create a table
    data = [
        ["Name", "Jane Smith"],
        ["Email", "jane@example.com"],
        ["Phone", "+1-987-654-3210"],
    ]

    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.beige),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Skills", styles["Heading2"]))
    elements.append(
        Paragraph("Python, Data Analysis, Machine Learning", styles["Normal"])
    )

    doc.build(elements)
    print(f"Created {filename.name}")


def create_multipage_pdf():
    """Create a multi-page PDF."""
    filename = data_dir / "multipage.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)

    elements: List[Any] = []
    styles = getSampleStyleSheet()

    # Page 1
    elements.append(Paragraph("Multi-Page Resume", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))

    for i in range(50):  # Add enough content for multiple pages
        elements.append(
            Paragraph(
                f"Line {i+1}: This is sample content to create a multi-page document.",
                styles["Normal"],
            )
        )
        if i % 10 == 9:
            elements.append(Spacer(1, 0.2 * inch))

    doc.build(elements)
    print(f"Created {filename.name}")


def create_pdf_with_special_chars():
    """Create a PDF with special characters."""
    filename = data_dir / "special_chars.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)

    elements: List[Any] = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Resume with Special Characters", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Name: José García-Müller", styles["Normal"]))
    elements.append(Paragraph("Email: josé@example.com", styles["Normal"]))
    elements.append(Paragraph("Skills: C++, C#, Python", styles["Normal"]))
    elements.append(
        Paragraph("Description: Expert in AI/ML & data science", styles["Normal"])
    )

    doc.build(elements)
    print(f"Created {filename.name}")


def create_images_only_pdf():
    """Create a PDF with only vector graphics and no extractable text.

    PDFMiner will return an empty string for this file, which causes the
    parser to raise FileParsingError("No text content found in PDF.").
    """
    from reportlab.pdfgen import canvas as rl_canvas

    filename = data_dir / "images_only.pdf"
    c = rl_canvas.Canvas(str(filename), pagesize=letter)
    # Draw shapes only — no text is added so PDFMiner extracts nothing.
    c.setFillColorRGB(0.8, 0.2, 0.2)
    c.rect(100, 400, 200, 200, fill=1)
    c.setFillColorRGB(0.2, 0.6, 0.9)
    c.circle(400, 500, 80, fill=1)
    c.setFillColorRGB(0.1, 0.7, 0.3)
    c.rect(150, 150, 300, 100, fill=1)
    c.save()
    print(f"Created {filename.name}")


def create_password_protected_pdf():
    """Create a minimal PDF whose Standard encryption dictionary causes
    pdfminer to raise PDFPasswordIncorrect, which the parser wraps as
    FileParsingError.
    """
    filename = data_dir / "password_protected.pdf"

    # Build each object as bytes and record the byte offset of each.
    obj1 = b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    obj2 = b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    obj3 = (
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 792] >>\nendobj\n"
    )
    # Standard security handler V=2 R=3 with 128-bit RC4.
    # The O/U values are intentionally invalid so pdfminer cannot decrypt.
    obj4 = (
        b"4 0 obj\n"
        b"<< /Filter /Standard /V 2 /R 3 /Length 128 /P -3904\n"
        b"   /O <28BF4E5E4E758A4164004E56FFFA01082E2E00B6D0683E802F0CA9FE6453697>\n"
        b"   /U <28BF4E5E4E758A4164004E56FFFA01082E2E00B6D0683E802F0CA9FE6453697>\n"
        b">>\nendobj\n"
    )

    header = b"%PDF-1.4\n"
    objects = [obj1, obj2, obj3, obj4]

    # Compute byte offsets for xref table.
    offsets: list[int] = []
    pos = len(header)
    for obj in objects:
        offsets.append(pos)
        pos += len(obj)

    xref_offset = pos
    xref = b"xref\n0 5\n0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode()

    trailer = (
        b"trailer\n<< /Size 5 /Root 1 0 R /Encrypt 4 0 R >>\n"
        b"startxref\n" + str(xref_offset).encode() + b"\n%%EOF\n"
    )

    filename.write_bytes(header + b"".join(objects) + xref + trailer)
    print(f"Created {filename.name}")


def create_large_pdf():
    """Create a multi-page PDF with substantial text content (>1000 chars)."""
    filename = data_dir / "large.pdf"
    doc = SimpleDocTemplate(str(filename), pagesize=letter)
    elements: List[Any] = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Large Resume Document", styles["Heading1"]))
    elements.append(Spacer(1, 0.2 * inch))

    for i in range(1, 101):
        elements.append(
            Paragraph(
                f"Section {i}: Experienced software engineer with expertise in "
                f"Python, Java, and distributed systems. Led cross-functional teams "
                f"to deliver scalable microservices handling millions of requests per day.",
                styles["Normal"],
            )
        )

    doc.build(elements)
    print(f"Created {filename.name}")


def create_multicolumn_pdf():
    """Create a two-column resume-style PDF.

    Left column contains "Left Column Content"; right column contains
    "Right Column Content".  Tests assert that both strings appear and
    that the left-column text comes before the right-column text in the
    parsed output (correct reading order).
    """
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import letter

    filename = data_dir / "multicolumn.pdf"
    width, height = letter
    c = rl_canvas.Canvas(str(filename), pagesize=letter)
    c.setFont("Helvetica", 11)

    # Left column (x ≈ 0–280)
    left_x = 72
    c.drawString(left_x, height - 100, "Left Column Content")
    c.drawString(left_x, height - 120, "Python Developer")
    c.drawString(left_x, height - 140, "San Francisco, CA")

    # Right column (x ≈ 310–540)
    right_x = 310
    c.drawString(right_x, height - 100, "Right Column Content")
    c.drawString(right_x, height - 120, "5 years experience")
    c.drawString(right_x, height - 140, "Open to remote")

    c.save()
    print(f"Created {filename.name}")


def create_pdf_with_header_footer():
    """Create a PDF with a repeating header and footer and distinct body text.

    Header: "Document Header"
    Footer: "Page 1 of 1"
    Body:   "Main Body Content" / "Experience" / "Education"
    """
    from reportlab.pdfgen import canvas as rl_canvas
    from reportlab.lib.pagesizes import letter

    filename = data_dir / "with_header_footer.pdf"
    width, height = letter
    c = rl_canvas.Canvas(str(filename), pagesize=letter)
    c.setFont("Helvetica", 11)

    # Header (top of page)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, height - 30, "Document Header")

    # Footer (bottom of page)
    c.setFont("Helvetica", 9)
    c.drawString(72, 20, "Page 1 of 1")

    # Body content (middle of page)
    c.setFont("Helvetica", 11)
    c.drawString(72, height - 120, "Main Body Content")
    c.drawString(72, height - 150, "Experience: 5 years in software engineering")
    c.drawString(72, height - 180, "Education: BSc Computer Science")

    c.save()
    print(f"Created {filename.name}")


if __name__ == "__main__":
    try:
        create_simple_pdf()
        create_pdf_with_tables()
        create_multipage_pdf()
        create_pdf_with_special_chars()
        create_images_only_pdf()
        create_password_protected_pdf()
        create_large_pdf()
        create_multicolumn_pdf()
        create_pdf_with_header_footer()
        print("\nAll test PDF files created successfully!")
    except Exception as e:
        print(f"Error creating test files: {e}")
        import traceback

        traceback.print_exc()
