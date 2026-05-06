from minsearch import Index

documents = [
    {"title": "ATS Keyword Matching", "category": "ats_basics", "content": "ATS systems scan CVs for exact keyword matches from the job description. If your CV uses 'managed projects' but the JD says 'project management', the ATS may not match them. Mirror the exact phrases used in the job description wherever possible."},
    {"title": "CV Formatting for ATS", "category": "formatting", "content": "ATS systems struggle with tables, columns, headers and footers, text boxes, and graphics. Use a single column layout with standard section headings like Experience, Education, and Skills. Save as a plain .docx or PDF without complex formatting."},
    {"title": "Skills Section Optimisation", "category": "keywords", "content": "Include a dedicated Skills section that lists your technical and soft skills as individual keywords. This is the easiest section for ATS to parse. Match skills terminology directly from the job description."},
    {"title": "Tailoring CV to Job Description", "category": "tailoring", "content": "A generic CV performs poorly in ATS screening. For each application, identify the top 5-10 keywords in the job description and ensure they appear naturally in your CV. Focus on the required qualifications section as it carries the most ATS weight."},
    {"title": "Action Verbs and Quantification", "category": "content_quality", "content": "Use strong action verbs at the start of each bullet point: led, built, improved, reduced, managed. Quantify achievements wherever possible: increased sales by 30%, reduced processing time by 2 hours per week. Numbers stand out to both ATS and human reviewers."},
    {"title": "Common ATS Rejection Reasons", "category": "ats_basics", "content": "The most common reasons CVs fail ATS screening are: missing keywords from the job description, unusual section headings the ATS cannot recognise, complex formatting that garbles the parsed text, and applying for roles where the experience level does not match."},
    {"title": "Cover Letter Best Practices", "category": "cover_letter", "content": "A strong cover letter opens with a specific reason you want this role at this company, not a generic introduction. The middle paragraph connects your top 2-3 achievements directly to the job requirements. Close with a clear call to action. Keep it to one page."},
    {"title": "Experience Level Matching", "category": "tailoring", "content": "Applying for roles above your experience level is a common reason for rejection. If a role requires 5 years of experience and you have 2, ATS may filter you out automatically. Focus applications on roles where you meet at least 70% of the requirements."},
    {"title": "Education and Certifications", "category": "keywords", "content": "List your highest qualification first. Include relevant certifications with the full name and abbreviation, for example Project Management Professional (PMP), so ATS can match either version. Include the awarding institution and year."},
    {"title": "File Format Recommendations", "category": "formatting", "content": "Submit CVs as .docx or PDF unless the application specifically requests otherwise. Avoid .pages, .odt, or image-based PDFs which many ATS systems cannot parse. If in doubt, .docx is the safest format for ATS compatibility."}
]

index = Index(
    text_fields=["title", "content"],
    keyword_fields=["category"]
)