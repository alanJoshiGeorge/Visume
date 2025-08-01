from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pdfplumber
import io
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

app = FastAPI()

# CORS config for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resume parser
def parse_resume_sections(text: str):
    sections = {
        "Name": "",
        "Summary": "",
        "Experience": "",
        "Education": "",
        "Skills": ""
    }

    current_section = "Summary"
    lines = text.splitlines()

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue
        elif re.search(r"\b(experience|work)\b", clean_line, re.I):
            current_section = "Experience"
        elif re.search(r"\b(education|qualification)\b", clean_line, re.I):
            current_section = "Education"
        elif re.search(r"\b(skill)\b", clean_line, re.I):
            current_section = "Skills"
        elif not sections["Name"]:
            sections["Name"] = clean_line
        else:
            sections[current_section] += clean_line + "\n"

    return sections

# ReportLab PDF generator
def generate_styled_pdf(sections) -> io.BytesIO:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    story = []

    # Name as header
    name = sections.get("Name", "Resume")
    story.append(Paragraph(f"<b><font size=18>{name}</font></b>", styles["Title"]))
    story.append(Spacer(1, 0.2 * inch))

    # Loop through sections
    for title in ["Summary", "Experience", "Education", "Skills"]:
        content = sections.get(title, "").strip()
        if content:
            story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
            for line in content.splitlines():
                story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 0.2 * inch))

    doc.build(story)
    buffer.seek(0)
    return buffer

# Endpoint
@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"message": "Please upload a PDF file."}

    contents = await file.read()

    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return {"message": "PDF has no readable text."}

        sections = parse_resume_sections(text)
        modified_pdf = generate_styled_pdf(sections)

        return StreamingResponse(
            modified_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=ATS_Resume.pdf"}
        )

    except Exception as e:
        return {"message": f"Failed to process PDF: {str(e)}"}



'''
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pdfplumber
import io
from fpdf import FPDF

app = FastAPI()

# Allow frontend access (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Clean and format resume text
def make_ats_friendly(text: str) -> str:
    lines = text.strip().splitlines()
    clean_lines = [line.strip() for line in lines if line.strip()]
    return "\n".join(clean_lines)

# Remove unsupported characters for PDF output
def clean_text_latin1(text: str) -> str:
    return text.encode("latin-1", errors="ignore").decode("latin-1")

# Generate a new PDF in memory
def generate_pdf(text: str) -> io.BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for line in text.split("\n"):
        pdf.multi_cell(0, 10, line)

    pdf_bytes = pdf.output(dest="S").encode("latin-1")
    output = io.BytesIO(pdf_bytes)
    output.seek(0)
    return output

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"message": "Please upload a PDF file."}

    try:
        contents = await file.read()
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        if not text.strip():
            return {"message": "PDF has no readable text."}

        ats_text = make_ats_friendly(text)
        safe_text = clean_text_latin1(ats_text)
        modified_pdf = generate_pdf(safe_text)
        print(modified_pdf)  
        return StreamingResponse(
            modified_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=ATS_Resume.pdf"}
        )

    except Exception as e:
        return {"message": f"Failed to process PDF: {str(e)}"}
'''