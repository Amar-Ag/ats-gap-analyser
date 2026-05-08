import sys
import time
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(override=True)

from src.agent.agent import run_agent

sessions = [
    {
        "name": "strong_match",
        "cv": """
Sarah Chen | Data Analyst | sarah.chen@email.com | London, UK

EXPERIENCE
Senior Data Analyst - RetailCo (2021-Present, 3 years)
- Built complex SQL queries to analyse customer purchasing patterns across 50+ product categories
- Created Power BI dashboards tracking KPIs for operations and marketing teams
- Used Python and pandas for data cleaning and ETL pipeline maintenance
- Collaborated with data engineering team on dbt models for reporting layer

Data Analyst - FinanceCo (2019-2021)
- Developed Tableau dashboards for financial reporting
- Wrote Python scripts to automate monthly reporting processes
- Worked with AWS Redshift for data warehousing

SKILLS
SQL, Python, pandas, numpy, Power BI, Tableau, dbt, AWS, Excel, data visualisation

EDUCATION
BSc Computer Science - University of Bristol (2019)
""",
        "jd": """
Senior Data Analyst - E-commerce Company

We are looking for a Senior Data Analyst with 3+ years experience.

Required:
- Strong SQL skills for complex querying
- Python for data analysis (pandas, numpy)
- Power BI or Tableau for dashboards
- Experience with dbt for data transformation
- AWS or cloud platform experience

Nice to have:
- Retail or e-commerce domain knowledge
- Experience with data pipeline tools
- Strong communication skills

You will analyse customer behaviour, build dashboards for leadership,
and support product teams with data-driven insights.
"""
    },
    {
        "name": "weak_match",
        "cv": """
James Morrison | Marketing Manager | james.morrison@email.com | Manchester, UK

EXPERIENCE
Senior Marketing Manager - BrandCo (2020-Present, 4 years)
- Led digital marketing campaigns across social media and email channels
- Managed £500k annual marketing budget and reported ROI to leadership
- Coordinated with creative teams to produce campaign assets
- Used Google Analytics and HubSpot for campaign performance tracking

Marketing Executive - AgencyCo (2018-2020)
- Executed social media strategy for 10+ client accounts
- Wrote copy for email newsletters and landing pages
- Tracked campaign metrics using Excel and basic reporting tools

SKILLS
Google Analytics, HubSpot, Excel, Social Media, Copywriting, Campaign Management

EDUCATION
BA Marketing - Manchester Metropolitan University (2018)
""",
        "jd": """
Data Analyst - Logistics Company

We are looking for a Data Analyst with 3+ years experience.

Required:
- Strong SQL skills
- Python for data analysis (pandas, numpy)
- Power BI or Tableau for dashboards
- Experience with logistics or supply chain data
- Statistical analysis skills

Nice to have:
- dbt experience
- Azure or AWS
- Freight industry knowledge
"""
    },
    {
        "name": "career_changer",
        "cv": """
Priya Sharma | Finance Analyst | priya.sharma@email.com | Birmingham, UK

EXPERIENCE
Senior Finance Analyst - BankCo (2020-Present, 4 years)
- Built complex Excel financial models for forecasting and budgeting
- Used SQL to query financial databases for monthly reporting
- Created Power BI dashboards for finance leadership team
- Analysed large datasets to identify cost reduction opportunities

Finance Analyst - InsuranceCo (2018-2020)
- Produced monthly management accounts using SQL and Excel
- Automated reporting processes using Python scripts
- Supported audit team with data extraction and analysis

SKILLS
SQL, Python (basic), Excel, Power BI, Financial Modelling, Data Analysis

EDUCATION
BSc Finance and Accounting - Aston University (2018)
ACA Qualified Accountant (2021)
""",
        "jd": """
Data Analyst - Technology Company

We are looking for a Data Analyst to join our growing analytics team.

Required:
- 2+ years experience in data analysis
- Strong SQL skills
- Python for data manipulation
- Experience with BI tools (Power BI, Tableau, or Looker)
- Ability to communicate insights to non-technical stakeholders

Nice to have:
- Experience with cloud platforms (GCP, AWS, Azure)
- Knowledge of machine learning concepts
- dbt or data pipeline experience

You will work closely with product and engineering teams to drive
data-informed decisions across the business.
"""
    },
    {
        "name": "senior_cv_junior_role",
        "cv": """
David Okonkwo | Principal Data Scientist | david.okonkwo@email.com | London, UK

EXPERIENCE
Principal Data Scientist - TechCorp (2019-Present, 5 years)
- Led a team of 6 data scientists building ML models for fraud detection
- Designed and deployed machine learning pipelines using Python, Spark, and AWS SageMaker
- Built real-time dashboards using Tableau and Looker for C-suite stakeholders
- Architected data lake on AWS S3 with dbt transformation layer
- Published 2 internal research papers on anomaly detection

Senior Data Scientist - StartupCo (2016-2019)
- Built recommendation engine serving 2M+ users
- Used SQL, Python, and Spark for large-scale data processing
- Mentored junior data scientists

SKILLS
Python, SQL, Spark, AWS, dbt, Tableau, Looker, Machine Learning, TensorFlow, Kubernetes

EDUCATION
MSc Data Science - Imperial College London (2016)
BSc Mathematics - University of Warwick (2014)
""",
        "jd": """
Junior Data Analyst - Retail Company

We are looking for a Junior Data Analyst to join our team.

Required:
- 0-2 years experience in data analysis
- Basic SQL knowledge
- Familiarity with Excel or Google Sheets
- Eagerness to learn and grow

Nice to have:
- Some Python experience
- Exposure to BI tools
- Degree in a numerate subject

You will support the senior analytics team with reporting and ad-hoc analysis.
"""
    },
    {
        "name": "logistics_domain_match",
        "cv": """
Amar Agrawal | Data Analyst | amar@email.com | Indianapolis, IN

EXPERIENCE
Data Analyst - Freight Brokerage (2022-Present, 3 years)
- Built SQL Server queries to analyse lane profitability across 10,000+ freight lanes
- Created Power BI dashboards tracking dry van and reefer rate trends for operations teams
- Used Python and pandas to automate RFP pricing workflows saving 5 hours per week
- Analysed carrier performance data to support procurement decisions
- Built margin forecasting models using historical rate data

Data Analyst Intern - LogisticsCo (2021-2022)
- Supported freight rate analysis using Excel and SQL
- Produced weekly market reports on spot and contract rate trends

SKILLS
SQL, Python, pandas, Power BI, Excel, freight analytics, supply chain data,
rate analysis, logistics domain knowledge

EDUCATION
BSc Business Analytics - Indiana University (2021)
""",
        "jd": """
Freight Data Analyst - Logistics Technology Company

We are looking for a Data Analyst with logistics domain expertise.

Required:
- 2+ years experience in freight or logistics analytics
- Strong SQL skills
- Python for data analysis
- Power BI or Tableau for reporting
- Understanding of freight market dynamics (spot rates, contract rates, lanes)

Nice to have:
- Experience with TMS or freight brokerage systems
- dbt or data pipeline experience
- Azure or AWS cloud experience

You will analyse freight market trends, build rate forecasting models,
and support our carrier procurement team with data-driven insights.
"""
    }
]

def run_sessions():
    for i, session in enumerate(sessions, 1):
        print(f"\n--- Session {i}/{len(sessions)}: {session['name']} ---")
        
        result = run_agent(
            f"Analyse my CV against this job description.\nCV:\n{session['cv']}\nJD:\n{session['jd']}"
        )
        
        print(f"Result preview: {result[:150]}")
        print(f"Session {i} complete")
        
        if i < len(sessions):
            print("Waiting 5 seconds to avoid rate limiting...")
            time.sleep(5)

if __name__ == "__main__":
    print(f"Running {len(sessions)} sessions...")
    run_sessions()
    print("\nAll sessions complete. Check Logfire dashboard.")