"""Script to generate test data files for parser tests."""

from pathlib import Path
from docx import Document

# Create test data directory
data_dir = Path(__file__).parent / "data"
data_dir.mkdir(exist_ok=True)


# Create a simple valid DOCX file
def create_simple_docx():
    doc = Document()
    doc.add_heading("Test Resume", 0)
    doc.add_paragraph("John Doe")
    doc.add_paragraph("Email: john.doe@example.com")
    doc.add_paragraph("Phone: +1-234-567-8900")

    doc.add_heading("Experience", level=1)
    doc.add_paragraph("Software Engineer at Tech Company")
    doc.add_paragraph("Worked on various projects using Python, Java, and JavaScript.")

    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Java, JavaScript, SQL, Git")

    # Save the document
    doc.save(str(data_dir / "valid_resume.docx"))
    print(f"Created valid_resume.docx")


# Create a DOCX with tables
def create_docx_with_tables():
    doc = Document()
    doc.add_heading("Resume with Tables", 0)

    # Add a table
    table = doc.add_table(rows=3, cols=2)
    table.style = "Light Grid Accent 1"

    # Fill the table
    cells = [
        ("Name", "Jane Smith"),
        ("Email", "jane@example.com"),
        ("Phone", "+1-987-654-3210"),
    ]

    for i, (label, value) in enumerate(cells):
        table.rows[i].cells[0].text = label
        table.rows[i].cells[1].text = value

    doc.add_paragraph()
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Data Analysis, Machine Learning")

    doc.save(str(data_dir / "with_tables.docx"))
    print(f"Created with_tables.docx")


# Create a DOCX with only whitespace/empty paragraphs
def create_empty_content_docx():
    doc = Document()
    doc.add_paragraph("")
    doc.add_paragraph("   ")
    doc.add_paragraph("\n")
    doc.save(str(data_dir / "empty_content.docx"))
    print(f"Created empty_content.docx")


def create_formatted_docx():
    """Create a DOCX with bold, italic, and underlined text."""
    doc = Document()
    doc.add_heading("Formatted Resume", 0)

    p = doc.add_paragraph()
    run = p.add_run("John Bold")
    run.bold = True

    p2 = doc.add_paragraph()
    run2 = p2.add_run("Senior Software Engineer")
    run2.italic = True

    p3 = doc.add_paragraph()
    run3 = p3.add_run("Contact: john@example.com")
    run3.underline = True

    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Java, Go, Kubernetes")

    doc.save(str(data_dir / "formatted.docx"))
    print("Created formatted.docx")


def create_images_only_docx():
    """Create a DOCX whose paragraphs contain only whitespace.

    The parser strips every paragraph; finding no text it raises
    FileParsingError("No text content found in document.").
    """
    doc = Document()
    for _ in range(5):
        doc.add_paragraph("")
    doc.add_paragraph("   ")
    doc.save(str(data_dir / "images_only.docx"))
    print("Created images_only.docx")


def create_special_chars_docx():
    """Create a DOCX with international and special characters."""
    doc = Document()
    doc.add_heading("Résumé — Special Characters", 0)
    doc.add_paragraph("Name: José García-Müller")
    doc.add_paragraph("Email: josé.garcía@example.com")
    doc.add_paragraph("Skills: C++, C#, Python, Rust")
    doc.add_paragraph("Languages: English, Español, Français, 中文")
    doc.add_paragraph("Note: Salary expectation €75,000–€90,000")

    doc.save(str(data_dir / "special_chars.docx"))
    print("Created special_chars.docx")


def create_headers_docx():
    """Create a DOCX with a document header and footer."""
    doc = Document()

    section = doc.sections[0]
    header = section.header
    header.paragraphs[0].text = "Confidential Resume — Jane Smith"

    footer = section.footer
    footer.paragraphs[0].text = "Page 1"

    doc.add_heading("Jane Smith", 0)
    doc.add_paragraph("Software Engineer | jane@example.com")
    doc.add_heading("Experience", level=1)
    doc.add_paragraph("Lead Engineer at Acme Corp, 2020–present")

    doc.save(str(data_dir / "with_headers.docx"))
    print("Created with_headers.docx")


def create_lists_docx():
    """Create a DOCX with bullet-point and numbered-list paragraphs."""
    doc = Document()
    doc.add_heading("Resume with Lists", 0)

    doc.add_heading("Skills", level=1)
    for skill in ["Python", "Java", "Docker", "Kubernetes", "PostgreSQL"]:
        doc.add_paragraph(skill, style="List Bullet")

    doc.add_heading("Achievements", level=1)
    for i, achievement in enumerate(
        ["Reduced latency by 40%", "Led team of 8 engineers", "Shipped 3 major releases"],
        start=1,
    ):
        doc.add_paragraph(achievement, style="List Number")

    doc.save(str(data_dir / "with_lists.docx"))
    print("Created with_lists.docx")


def create_large_docx():
    """Create a DOCX with substantial text content (>1000 chars)."""
    doc = Document()
    doc.add_heading("Large Resume Document", 0)

    for i in range(1, 51):
        doc.add_paragraph(
            f"Section {i}: Experienced engineer with deep expertise in distributed "
            f"systems, cloud infrastructure, and high-performance data pipelines. "
            f"Delivered projects serving millions of users across multiple regions."
        )

    doc.save(str(data_dir / "large.docx"))
    print("Created large.docx")


def create_empty_paragraphs_docx():
    """Create a DOCX with many empty paragraphs interspersed with real content."""
    doc = Document()
    doc.add_heading("Resume", 0)
    doc.add_paragraph("")  # empty
    doc.add_paragraph("   ")  # whitespace only
    doc.add_paragraph("John Doe — Software Engineer")
    doc.add_paragraph("")
    doc.add_paragraph("john.doe@example.com | +1-555-000-1234")
    doc.add_paragraph("   ")
    doc.add_paragraph("")
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("")
    doc.add_paragraph("Python, SQL, Docker")

    doc.save(str(data_dir / "empty_paragraphs.docx"))
    print("Created empty_paragraphs.docx")


def create_nested_tables_docx():
    """Create a DOCX with a table containing multiple rows and columns."""
    doc = Document()
    doc.add_heading("Resume with Nested Tables", 0)

    # Outer table representing work history
    table = doc.add_table(rows=3, cols=3)
    headers = ["Company", "Role", "Duration"]
    for j, h in enumerate(headers):
        table.rows[0].cells[j].text = h

    rows_data = [
        ("Acme Corp", "Senior Engineer", "2020–present"),
        ("Beta Inc", "Software Engineer", "2017–2020"),
    ]
    for i, (company, role, duration) in enumerate(rows_data, start=1):
        table.rows[i].cells[0].text = company
        table.rows[i].cells[1].text = role
        table.rows[i].cells[2].text = duration

    doc.add_paragraph()
    doc.add_heading("Skills", level=1)
    doc.add_paragraph("Python, Java, Kubernetes")

    doc.save(str(data_dir / "nested_tables.docx"))
    print("Created nested_tables.docx")


def create_legacy_doc():
    """Create a stub .doc file that python-docx cannot parse.

    python-docx requires a ZIP-format container (.docx); a .doc file in
    legacy binary format causes Document() to raise BadZipFile, which the
    word parser wraps as FileParsingError("Error parsing Word document.").
    """
    # Write an OLE2 compound-document magic header followed by zeroed bytes.
    # This is recognisable as a legacy Word binary file but python-docx will
    # reject it, satisfying the test's error-handling assertion.
    ole2_magic = b"\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1"
    (data_dir / "sample.doc").write_bytes(ole2_magic + b"\x00" * 504)
    print("Created sample.doc")


if __name__ == "__main__":
    try:
        create_simple_docx()
        create_docx_with_tables()
        create_empty_content_docx()
        create_formatted_docx()
        create_images_only_docx()
        create_special_chars_docx()
        create_headers_docx()
        create_lists_docx()
        create_large_docx()
        create_empty_paragraphs_docx()
        create_nested_tables_docx()
        create_legacy_doc()
        print("\nAll test DOCX files created successfully!")
    except Exception as e:
        print(f"Error creating test files: {e}")
