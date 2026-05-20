import os
import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
from docx import Document
import re

# -----------------------------
# PAGE CONFIG
# -----------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="centered"
)

# -----------------------------
# GEMINI API CONFIGURATION
# -----------------------------

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------------
# SIDEBAR
# -----------------------------

with st.sidebar:

    st.header("About")

    st.write("""
    AI-powered Resume Analyzer designed to evaluate resumes against job descriptions and provide ATS-based analysis.
    """)

    st.markdown("---")
    st.subheader("Features")

    st.markdown("""
    🔹ATS Compatibility Analysis    
    🔹Resume & Job Description Matching 
    🔹Missing Skills Detection  
    🔹Missing Keywords Identification 
    🔹Resume Improvement Suggestions  
    """)
    

    st.markdown("---")
    st.write("Developed by Shikhin G S")
    

# -----------------------------
# PAGE TITLE
# -----------------------------

st.title("📄 AI Resume Analyzer")

st.markdown("""Upload your resume and compare it with job descriptions to receive ATS-based analysis and improvement suggestions.""")

# -----------------------------
# FILE UPLOAD
# -----------------------------

uploaded_file = st.file_uploader(
    "Upload Resume",
    type=["pdf", "docx"]
)

# -----------------------------
# JOB DESCRIPTION INPUT
# -----------------------------

job_description = st.text_area(
    "Paste Job Description",
    height=180
)

# -----------------------------
# FUNCTION TO READ PDF
# -----------------------------

def extract_text_from_pdf(pdf_file):

    reader = PdfReader(pdf_file)

    text = ""

    for page in reader.pages:

        extracted = page.extract_text()

        if extracted:
            text += extracted

    return text

# -----------------------------
# FUNCTION TO READ WORD FILE
# -----------------------------

def extract_text_from_docx(docx_file):

    doc = Document(docx_file)

    text = ""

    for para in doc.paragraphs:
        text += para.text + "\n"

    return text

# -----------------------------
# ANALYZE BUTTON
# -----------------------------

if st.button("Analyze Resume"):

    # CHECK FILE + JD
    if uploaded_file and job_description:

        # GET FILE NAME
        file_name = uploaded_file.name

        # -----------------------------
        # PDF FILE
        # -----------------------------

        if file_name.endswith(".pdf"):

            resume_text = extract_text_from_pdf(
                uploaded_file
            )

        # -----------------------------
        # WORD FILE
        # -----------------------------

        elif file_name.endswith(".docx"):

            resume_text = extract_text_from_docx(
                uploaded_file
            )

        else:

            st.error("Unsupported File Format")
            st.stop()

        # -----------------------------
        # AI PROMPT
        # -----------------------------

        prompt = f"""
        You are an ATS Resume Analyzer.

        Compare the resume with the job description.

        Provide:

        1. ATS Score out of 100
        2. Missing Skills
        3. Missing Keywords
        4. Resume Strengths
        5. Resume Weaknesses
        6. Suggestions to Improve

        Return ATS Score in this format:
        ATS Score: XX

        Resume:
        {resume_text}

        Job Description:
        {job_description}
        """

        # -----------------------------
        # GEMINI RESPONSE
        # -----------------------------

        try:

            with st.spinner("Analyzing Resume..."):
                
                model = genai.GenerativeModel("gemini-2.5-flash")
                response = model.generate_content(prompt)
                result = response.text

            # -----------------------------
            # SUCCESS MESSAGE
            # -----------------------------

            st.success(
                "Analysis Completed Successfully ✅"
            )

            # -----------------------------
            # ATS SCORE EXTRACTION
            # -----------------------------

            score_match = re.search(
                r"ATS Score:\s*(\d+)",
                result
            )

            if score_match:

                ats_score = int(
                    score_match.group(1)
                )

                st.subheader("📊 ATS Score")

                st.progress(ats_score)

                st.write(f"{ats_score}% Match")

            # -----------------------------
            # DISPLAY RESULT
            # -----------------------------

            st.subheader("📄 Analysis Result")

            st.markdown(result)

            # -----------------------------
            # DOWNLOAD BUTTON
            # -----------------------------

            st.download_button(
                label="Download Report",
                data=result,
                file_name="resume_analysis.txt",
                mime="text/plain"
            )

        # -----------------------------
        # ERROR HANDLING
        # -----------------------------

        except Exception as e:

                st.error(f"Error: {str(e)}")

    else:

        st.warning(
            "Please upload resume and paste job description"
        )
