"""AI Cover Letter Generator - Streamlit app powered by Google Gemini Flash."""

import io
import os
import re

import streamlit as st
from docx import Document
from google import genai
from google.genai import types
from pypdf import PdfReader

# Default Gemini Flash model. Override with a GEMINI_MODEL secret or env variable
# if Google renames or retires it (see https://ai.google.dev/gemini-api/docs/models).
DEFAULT_MODEL = "gemini-3.8-flash"
MAX_RESUME_CHARS = 20000
MAX_JD_CHARS = 8000
TONES = ["Professional", "Enthusiastic", "Confident", "Friendly", "Formal"]
LENGTHS = {"Short (~200 words)": 200, "Standard (~300 words)": 300, "Detailed (~400 words)": 400}

SYSTEM_PROMPT = """You are an expert career coach and professional cover letter writer.
Write a personalized cover letter using ONLY facts found in the candidate's resume.
Match the resume's real skills, projects and experience to the job description and
use its important keywords naturally. Never invent employers, degrees, tools, numbers
or achievements that are not in the resume. If the candidate is entry-level, highlight
education, projects, internships and willingness to learn.
Rules:
- Output only the letter text, no commentary and no markdown formatting.
- Start with a greeting, then 3-4 short paragraphs, then a polite closing and the candidate's name.
- Do not use placeholders like [Company Name]; if a detail is unknown, write around it.
- Avoid clichés and filler. Be specific and concise."""


# ---------- Helpers ----------

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception:
            raise ValueError("This PDF is password protected.")
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    parts = [p.text for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    parts.append(cell.text)
    return "\n".join(parts)


def extract_resume_text(filename: str, file_bytes: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        text = extract_text_from_docx(file_bytes)
    elif name.endswith(".txt"):
        text = file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError("Unsupported file type. Upload a PDF, DOCX or TXT file.")
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def get_setting(name: str, default: str = "") -> str:
    """Read a setting from Streamlit secrets first, then environment variables."""
    try:
        value = st.secrets.get(name, "")
    except Exception:
        value = ""
    return value or os.environ.get(name, "") or default


def build_prompt(resume_text, job_description, tone, target_words, company="", role="", name=""):
    details = []
    if name.strip():
        details.append(f"Candidate name: {name.strip()}")
    if role.strip():
        details.append(f"Job title: {role.strip()}")
    if company.strip():
        details.append(f"Company: {company.strip()}")
    details.append(f"Tone: {tone}")
    details.append(f"Target length: about {target_words} words")
    return (
        "\n".join(details)
        + f"\n\nRESUME:\n{resume_text[:MAX_RESUME_CHARS]}"
        + f"\n\nJOB DESCRIPTION:\n{job_description[:MAX_JD_CHARS]}\n"
    )


def clean_letter(text: str) -> str:
    """Strip markdown fences/bold markers the model may add despite instructions."""
    text = (text or "").strip()
    text = re.sub(r"^```[a-z]*\s*|\s*```$", "", text, flags=re.IGNORECASE)
    text = text.replace("**", "")
    return text.strip()


def generate_cover_letter(api_key, resume_text, job_description, tone="Professional",
                          target_words=300, company="", role="", name=""):
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=get_setting("GEMINI_MODEL", DEFAULT_MODEL),
        contents=build_prompt(resume_text, job_description, tone, target_words, company, role, name),
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, temperature=0.7),
    )
    letter = clean_letter(response.text)
    if not letter:
        raise ValueError("The AI returned an empty response. Please try again.")
    return letter


def letter_to_docx_bytes(letter: str) -> bytes:
    doc = Document()
    for para in re.split(r"\n\s*\n", letter):
        doc.add_paragraph(para.strip())
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


# ---------- UI ----------

def main() -> None:
    st.set_page_config(page_title="Cover Letter Generator", page_icon="✉️", layout="wide")
    st.title("✉️ AI Cover Letter Generator")
    st.caption("Upload your resume, paste the job description, and get a tailored cover letter.")

    api_key = get_setting("GEMINI_API_KEY")
    if not api_key:
        with st.sidebar:
            st.header("Settings")
            api_key = st.text_input(
                "Gemini API key", type="password",
                help="Get a free key at https://aistudio.google.com/apikey",
            )
    if not api_key:
        st.info("Add your Gemini API key in the sidebar to begin.")

    left, right = st.columns(2)
    with left:
        uploaded = st.file_uploader("Upload resume (PDF, DOCX or TXT)", type=["pdf", "docx", "txt"])
        name = st.text_input("Your name (optional)")
        role = st.text_input("Job title (optional)")
        company = st.text_input("Company name (optional)")
    with right:
        job_description = st.text_area("Job description", height=250,
                                       placeholder="Paste the full job posting here...")
        c1, c2 = st.columns(2)
        tone = c1.selectbox("Tone", TONES)
        length = c2.selectbox("Length", list(LENGTHS), index=1)

    ready = uploaded is not None and bool(job_description.strip()) and bool(api_key)
    if st.button("Generate Cover Letter", type="primary", disabled=not ready):
        try:
            with st.spinner("Reading your resume..."):
                text = extract_resume_text(uploaded.name, uploaded.getvalue())
            if len(text) < 50:
                st.error("Could not read enough text from the resume. If it is a scanned "
                         "or image-based PDF, export a text-based PDF or DOCX instead.")
                return
            with st.spinner("Writing your cover letter..."):
                st.session_state["letter"] = generate_cover_letter(
                    api_key, text, job_description, tone, LENGTHS[length], company, role, name)
        except ValueError as e:
            st.error(str(e))
            return
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            return

    if "letter" in st.session_state:
        st.subheader("Your Cover Letter")
        edited = st.text_area("You can edit the letter below", st.session_state["letter"], height=420)
        d1, d2 = st.columns(2)
        d1.download_button("Download as TXT", edited, file_name="cover_letter.txt", mime="text/plain")
        d2.download_button(
            "Download as DOCX", letter_to_docx_bytes(edited), file_name="cover_letter.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.caption("Always review the letter and check every detail before sending it.")


if __name__ == "__main__":
    main()
