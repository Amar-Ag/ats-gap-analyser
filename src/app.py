import streamlit as st
import sys
import pdfplumber
import io
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.agent.agent import run_agent

if 'analysis_count' not in st.session_state:
    st.session_state.analysis_count = 0

MAX_ANALYSES = 3

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
            height=250,  # reduced from 350
            label_visibility="collapsed"
        )

with col2:
    st.subheader("Job Description")
    
    # URL option
    jd_url = st.text_input(
        "Paste job posting URL (optional)",
        placeholder="https://company.com/careers/job-123"
    )
    
    if jd_url:
        if st.button("📥 Fetch from URL"):
            try:
                import requests
                from bs4 import BeautifulSoup
                
                with st.spinner("Fetching job description..."):
                    response = requests.get(jd_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # remove noise
                    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 
                                'iframe', 'img', 'button', 'form']):
                        tag.decompose()
                    
                    # try to find main content area first
                    main_content = (
                        soup.find('main') or 
                        soup.find('article') or
                        soup.find(attrs={'class': lambda x: x and any(
                            word in ' '.join(x).lower() 
                            for word in ['job', 'posting', 'description', 'content', 'detail']
                        ) if isinstance(x, list) else False}) or
                        soup.find('body')
                    )
                    
                    fetched_text = main_content.get_text(separator='\n', strip=True)[:5000]
                
                st.session_state.jd_text = fetched_text
                st.success(f"Fetched {len(fetched_text)} characters from URL")
            except Exception as e:
                st.error(f"Could not fetch URL: {str(e)}. Please paste the job description manually.")

    
    # JD column - reduce height  
    jd_height = 200 if jd_url else 250  # reduced from 300/350

    jd_text = st.text_area(
        "JD",
        value=st.session_state.get('jd_text', ''),
        placeholder="Or paste the job description here...",
        height=jd_height,
        label_visibility="collapsed"
    )

analyse_button = st.button("🔍 Analyse My CV", type="primary", use_container_width=True)

st.divider()
if analyse_button:
    if not cv_text or not jd_text:
        st.warning("Please provide both your CV and the job description.")
    elif st.session_state.analysis_count >= MAX_ANALYSES:
        st.error(f"You've reached the limit of {MAX_ANALYSES} analyses per session. Please refresh the page to start a new session.")
    else:
        try:
            with st.spinner("Analysing your CV..."):
                result = run_agent(
                    f"Analyse my CV against this job description.\nCV:\n{cv_text}\nJD:\n{jd_text}"
                )
            st.session_state.analysis_count += 1
            st.divider()
            st.subheader(f"Results (Analysis {st.session_state.analysis_count}/{MAX_ANALYSES})")
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
2. Paste the job description or fetch from URL
3. Click **Analyse My CV**
4. Get your match score, gaps, and a tailored cover letter
    """)
    st.divider()
    st.warning(f"⚠️ Demo limit: {MAX_ANALYSES} analyses per session")
    st.caption("Built with Groq + llama-3.3-70b-versatile")