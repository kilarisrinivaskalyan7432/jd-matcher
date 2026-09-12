import os
import tempfile
import streamlit as st

from utils.pdf_parser import extract_text_from_pdf
from utils.text_cleaner import clean_text
from utils.skill_extractor import load_skills_list, extract_skills
from utils.scorer import compute_similarity_score

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_PATH = os.path.join(BASE_DIR, "data", "skills_list.txt")

# Page config
st.set_page_config(
    page_title="Resume–JD Matcher",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for background and styling
st.markdown("""
<style>
/* Full page background */
.stApp {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #e2e8f0;
}

/* Make headings brighter */
h1, h2, h3 {
    color: #f1f5f9 !important;
}

/* Cards for sections */
div[data-testid="stMetric"], .stMarkdown, .stSubheader {
    color: #e2e8f0;
}

/* Input areas */
.stTextArea label, .stFileUploader label, .stSelectbox label {
    color: #cbd5e1;
}

/* Buttons */
.stButton > button {
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 0.4rem 1rem;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #2563eb;
}
</style>
""", unsafe_allow_html=True)

st.title("Smart Resume–JD Matcher (ATS-style Assistant)")
st.markdown("Upload your resume, paste a job description, and get **match score + tailored skill suggestions**.")

@st.cache_resource
def load_skills():
    return load_skills_list(SKILLS_PATH)

skills_list = load_skills()

# User inputs
col_a, col_b = st.columns(2)
with col_a:
    career_level = st.selectbox(
        "Career Level",
        ["Fresher (0–1 year)", "Early Career (1–3 years)", "Experienced (3+ years)"]
    )
with col_b:
    role_type = st.selectbox(
        "Target Role",
        ["SDE / Backend", "Frontend", "Full-Stack", "ML Engineer", "AI Engineer", "Data Engineer", "Data Analyst"]
    )

resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description (JD)", height=200)

analyze_clicked = st.button("Analyze Resume", type="primary")

if analyze_clicked:
    if not resume_file:
        st.warning("Please upload your resume (PDF).")
        st.stop()
    if not jd_text or len(jd_text.strip()) < 20:
        st.warning("Please paste a meaningful job description (at least ~20 characters).")
        st.stop()

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(resume_file.read())
        tmp_path = tmp.name

    resume_text_raw = extract_text_from_pdf(tmp_path)
    os.remove(tmp_path)

    if not resume_text_raw:
        st.error("Could not extract text from the PDF. Try another file.")
        st.stop()

    resume_text_clean = clean_text(resume_text_raw)
    jd_text_clean = clean_text(jd_text)

    # Extract skills
    resume_skills = extract_skills(resume_text_clean, skills_list)
    jd_skills = extract_skills(jd_text_clean, skills_list)

    # Similarity score
    sim_score = compute_similarity_score(resume_text_clean, jd_text_clean)
    match_percent = int(round(sim_score * 100))

    # Missing skills
    missing_skills = sorted(list(jd_skills - resume_skills))

    # Detect simple section presence (very basic)
    has_projects = "project" in resume_text_clean
    has_experience = any(k in resume_text_clean for k in ["experience", "internship", "work"])
    has_skills_section = "skill" in resume_text_clean
    has_education = any(k in resume_text_clean for k in ["education", "btech", "b.e", "b.tech", "degree"])

    # Display results
    st.subheader("Match Score")
    st.metric("Resume–JD Match", f"{match_percent}%")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Skills Detected in Resume")
        if resume_skills:
            st.write(", ".join(sorted(resume_skills)))
        else:
            st.warning("No known skills detected in resume.")

    with col2:
        st.subheader("Skills Detected in JD")
        if jd_skills:
            st.write(", ".join(sorted(jd_skills)))
        else:
            st.warning("No known skills detected in JD.")

    # Suggested skills to add
    st.subheader("Suggested Skills to Add in Your Resume")
    if missing_skills:
        st.markdown(
            "These skills appear in the JD but were not detected in your resume. "
            "Add the ones that truly apply to you."
        )
        # Priority: ML/AI roles → prioritize ML skills, SDE → prioritize CS core, etc.
        priority_order = []

        if "ML" in role_type or "AI" in role_type:
            ml_keywords = ["machine learning", "deep learning", "nlp", "computer vision",
                           "tensorflow", "pytorch", "scikit-learn", "llm", "generative ai"]
            priority_order += [k for k in missing_skills if any(pk in k for pk in ml_keywords)]

        if "SDE" in role_type or "Backend" in role_type or "Full-Stack" in role_type:
            cs_keywords = ["data structures", "algorithms", "dbms", "operating systems",
                           "computer networks", "system design", "rest api", "microservices"]
            priority_order += [k for k in missing_skills if any(pk in k for pk in cs_keywords)]

        # Add remaining
        priority_order += [k for k in missing_skills if k not in priority_order]

        if priority_order:
            st.markdown("**Top suggested skills to consider adding:**")
            st.write(", ".join(priority_order[:10]))  # show up to 10
        else:
            st.write(", ".join(missing_skills[:10]))
    else:
        st.success("No obvious skill gaps based on current skill list.")

    # Tailored suggestions
    st.subheader("Tailored Suggestions")

    level_key = "fresher" if "Fresher" in career_level else "early" if "1–3" in career_level else "experienced"

    suggestions = []

    # Generic suggestions based on match
    if match_percent < 50:
        suggestions.append(
            "Your resume is weakly aligned with this JD. "
            "Prioritize adding key missing skills (if true) into Skills, Projects, or Experience."
        )
    elif match_percent < 75:
        suggestions.append(
            "Moderate match. Adding a few relevant keywords from the missing skills "
            "may improve your ATS match and recruiter perception."
        )
    else:
        suggestions.append(
            "Strong match. Ensure the most important skills are clearly visible "
            "in your Skills and Projects/Experience sections."
        )

    # Level-specific suggestions
    if level_key == "fresher":
        if not has_projects:
            suggestions.append(
                "As a fresher, projects are critical. Add 2–4 solid projects with tech stack, "
                "problem statement, and your contribution."
            )
        if not has_skills_section:
            suggestions.append(
                "Add a dedicated 'Skills' section listing languages, frameworks, tools, and libraries."
            )
        suggestions.append(
            "Highlight internships, hackathons, coding profiles (LeetCode, Codeforces, GitHub) "
            "to show practical exposure."
        )
    elif level_key == "early":
        if not has_experience:
            suggestions.append(
                "For 1–3 years experience, clearly mention roles, duration, and key responsibilities. "
                "Use action verbs and quantify impact where possible."
            )
        suggestions.append(
            "Emphasize technologies used, scale of systems, and any ownership of features or modules."
        )
    else:  # experienced
        if not has_experience:
            suggestions.append(
                "For experienced profiles, ensure a strong 'Experience' section with company, role, "
                "duration, and measurable impact (e.g., 'reduced latency by 30%')."
            )
        suggestions.append(
            "Highlight system design, architecture decisions, leadership, mentoring, and cross-team work."
        )

    # Role-specific hints (simple)
    if "ML" in role_type or "AI" in role_type:
        if not any(k in resume_skills for k in ["machine learning", "deep learning", "nlp", "computer vision"]):
            suggestions.append(
                "For ML/AI roles, explicitly mention ML/AI projects, models, datasets, and metrics "
                "(accuracy, F1, latency, etc.)."
            )
    if "SDE" in role_type or "Backend" in role_type or "Full-Stack" in role_type:
        if not any(k in resume_skills for k in ["data structures", "algorithms", "dbms", "operating systems"]):
            suggestions.append(
                "For SDE/Backend roles, highlight core CS fundamentals (DSA, DBMS, OS, networks) "
                "through projects or coursework."
            )

    for s in suggestions:
        st.markdown(f"- {s}")

    # Profile strength indicator (simple)
    st.subheader("Profile Strength (Basic Heuristic)")

    strength_score = 0
    if has_projects:
        strength_score += 1
    if has_experience:
        strength_score += 1
    if has_skills_section:
        strength_score += 1
    if has_education:
        strength_score += 1
    if match_percent >= 60:
        strength_score += 1

    if strength_score <= 2:
        st.warning("Profile strength: Low–Moderate. Focus on adding projects, skills, and clear experience.")
    elif strength_score <= 4:
        st.info("Profile strength: Moderate–Good. Strengthen with more impactful bullet points and metrics.")
    else:
        st.success("Profile strength: Strong. Focus on tailoring for each JD and practicing interviews.")

    # Optional debug
    with st.expander("Show extracted resume text (debug)"):
        st.text(resume_text_raw)

elif not resume_file and not jd_text:
    st.info("Upload your resume (PDF) and paste a job description, then click **Analyze Resume**.")
else:
    st.info("Once ready, click **Analyze Resume** to get match score and suggestions.")