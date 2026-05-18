import streamlit as st
import sys
import pdfplumber
import io
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.agent import run_agent

st.set_page_config(layout="wide", page_title="ATS Gap Analyser")

st.title("ATS Gap Analyser")
st.markdown("Paste your CV and a job description to see how well you match and get specific improvement suggestions.")
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Your CV")
    
    # PDF upload option
    uploaded_file = st.file_uploader("Upload CV as PDF", type="pdf")
    
    if uploaded_file:
        with pdfplumber.open(io.BytesIO(uploaded_file.read())) as pdf:
            cv_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        st.success(f"PDF uploaded — {len(cv_text)} characters extracted")
        st.text_area("Extracted CV text", value=cv_text, height=250, disabled=True, label_visibility="visible")
    else:
        cv_text = st.text_area(
            "CV",
            placeholder="Or paste your CV text here...",
            height=350,
            label_visibility="collapsed"
        )

with col2:
    st.subheader("Job Description")
    jd_text = st.text_area(
        "JD",
        placeholder="Paste the job description here...",
        height=350,
        label_visibility="collapsed"
    )

st.divider()

analyse_button = st.button("🔍 Analyse My CV", type="primary", use_container_width=True)

if analyse_button:
    if not cv_text or not jd_text:
        st.warning("Please provide both your CV and the job description.")
    else:
        try:
            with st.spinner("Analysing your CV against the job description..."):
                result = run_agent(
                    f"Analyse my CV against this job description.\nCV:\n{cv_text}\nJD:\n{jd_text}"
                )
            st.divider()
            st.subheader("Results")
            st.markdown(result)
        except Exception as e:
            if '429' in str(e):
                st.error("Rate limit reached — please try again in a few minutes.")
            else:
                st.error(f"Something went wrong: {str(e)}")

with st.sidebar:
    st.header("How to use")
    st.markdown("""
1. Upload your CV as a PDF or paste the text
2. Paste the job description
3. Click **Analyse My CV**
4. Get your match score, gaps, and a tailored cover letter
    """)
    st.divider()
    st.caption("Built with Groq + llama-3.3-70b-versatile")