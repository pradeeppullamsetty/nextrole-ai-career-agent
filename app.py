import io
import re
import html
from collections import Counter

import streamlit as st

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

try:
    from docx import Document
except Exception:
    Document = None

st.set_page_config(
    page_title="NextRole — Career Studio",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --ink:#f5f6fb; --muted:#a4a9bc; --line:rgba(255,255,255,.12); --glass:rgba(255,255,255,.055); }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp {
 background:
 radial-gradient(ellipse at 12% 0%, rgba(105,93,255,.22), transparent 38%),
 radial-gradient(ellipse at 92% 8%, rgba(74,194,255,.13), transparent 32%),
 radial-gradient(ellipse at 50% 100%, rgba(183,102,255,.11), transparent 45%),
 #080a11;
 color:var(--ink);
}
[data-testid="stHeader"] { background:rgba(8,10,17,.55); }
.block-container { max-width:1280px; padding-top:1.4rem; padding-bottom:4rem; }
h1,h2,h3 { font-family:'Manrope',sans-serif!important; letter-spacing:-.045em; }
h1 { font-size:clamp(2.6rem,5vw,4.8rem)!important; line-height:1.02!important; font-weight:800!important; }
p, label, .stMarkdown { color:#dfe2ef; }
[data-testid="stVerticalBlockBorderWrapper"] {
 border:1px solid var(--line); border-radius:24px;
 background:linear-gradient(145deg,rgba(255,255,255,.075),rgba(255,255,255,.025));
 box-shadow:0 18px 60px rgba(0,0,0,.16); backdrop-filter:blur(18px);
}
div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input {
 background:rgba(255,255,255,.045)!important; color:#f5f6fb!important;
 border:1px solid rgba(255,255,255,.14)!important; border-radius:15px!important;
}
.stButton>button, .stDownloadButton>button {
 border:1px solid rgba(255,255,255,.18); border-radius:999px; padding:.65rem 1.2rem;
 background:linear-gradient(115deg,#d9d8ff,#a8dfff); color:#10121b; font-weight:700;
 transition:all .22s ease; box-shadow:0 6px 26px rgba(127,130,255,.17);
}
.stButton>button:hover, .stDownloadButton>button:hover {
 transform:translateY(-2px); box-shadow:0 10px 34px rgba(127,130,255,.32);
 border-color:rgba(255,255,255,.6);
}
[data-testid="stFileUploader"] section { background:rgba(255,255,255,.035); border:1px dashed rgba(190,195,255,.3); border-radius:18px; }
[data-testid="stMetric"] { background:rgba(255,255,255,.04); border:1px solid var(--line); padding:18px; border-radius:18px; }
[data-testid="stMetricValue"] { font-family:'Manrope',sans-serif; letter-spacing:-.06em; }
hr { border-color:rgba(255,255,255,.1); }
.hero { position:relative; overflow:hidden; padding:3rem 0 2rem; }
.eyebrow { display:inline-flex; align-items:center; gap:8px; padding:7px 12px; border:1px solid rgba(255,255,255,.16); border-radius:999px; background:rgba(255,255,255,.055); color:#d6d8ff; font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; }
.spark { display:inline-block; background:linear-gradient(90deg,#fff,#b6b2ff,#9be2ff); -webkit-background-clip:text; background-clip:text; color:transparent; }
.subhead { color:#aeb4c9; font-size:1.08rem; max-width:680px; line-height:1.75; }
.glass-card { padding:22px; border:1px solid var(--line); border-radius:22px; background:linear-gradient(140deg,rgba(255,255,255,.075),rgba(255,255,255,.025)); height:100%; transition:transform .25s ease,border-color .25s ease; }
.glass-card:hover { transform:translateY(-4px); border-color:rgba(177,182,255,.45); }
.small-label { color:#9ea6c0; font-size:.76rem; text-transform:uppercase; letter-spacing:.12em; }
.pill { display:inline-block; padding:6px 10px; margin:4px 5px 2px 0; border-radius:999px; background:rgba(153,151,255,.12); border:1px solid rgba(153,151,255,.24); color:#dedcff; font-size:.82rem; }
.pill-missing { background:rgba(255,174,104,.09); border-color:rgba(255,174,104,.23); color:#ffd1a3; }
.score-ring { font-family:'Manrope',sans-serif; font-size:3.2rem; font-weight:800; letter-spacing:-.08em; }
.footer { color:#747d96; font-size:.82rem; text-align:center; padding-top:2.5rem; }
@media (prefers-reduced-motion: reduce) { * { animation:none!important; transition:none!important; } }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

SKILL_GROUPS = {
    "Programming": ["python", "java", "javascript", "typescript", "c++", "c#", "go", "rust", "sql", "r"],
    "AI & Data": ["machine learning", "deep learning", "artificial intelligence", "llm", "generative ai", "rag", "nlp", "pandas", "numpy", "pytorch", "tensorflow", "scikit-learn", "data analysis", "data science", "computer vision", "langchain"],
    "Web & APIs": ["html", "css", "react", "next.js", "node.js", "express", "fastapi", "flask", "django", "rest api", "graphql", "streamlit"],
    "Cloud & DevOps": ["aws", "azure", "gcp", "docker", "kubernetes", "linux", "git", "github actions", "ci/cd", "terraform"],
    "Databases": ["postgresql", "mysql", "mongodb", "redis", "sqlite", "firebase", "chroma"],
    "Professional": ["communication", "leadership", "problem solving", "teamwork", "agile", "project management", "presentation"],
}
ALL_SKILLS = sorted({s for group in SKILL_GROUPS.values() for s in group})

def extract_resume(upload):
    if upload is None:
        return ""
    raw = upload.getvalue()
    name = upload.name.lower()
    try:
        if name.endswith(".pdf"):
            if PdfReader is None:
                return ""
            reader = PdfReader(io.BytesIO(raw))
            return "\n".join(page.extract_text() or "" for page in reader.pages)
        if name.endswith(".docx"):
            if Document is None:
                return ""
            doc = Document(io.BytesIO(raw))
            return "\n".join(p.text for p in doc.paragraphs)
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def clean_text(text):
    return re.sub(r"\s+", " ", (text or "").lower()).strip()

def detect_skills(text):
    source = clean_text(text)
    found = []
    for skill in ALL_SKILLS:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, source):
            found.append(skill)
    return found

def score_match(resume_text, job_text):
    resume_skills = set(detect_skills(resume_text))
    job_skills = set(detect_skills(job_text))
    matched = sorted(resume_skills & job_skills)
    missing = sorted(job_skills - resume_skills)
    if job_skills:
        score = round(100 * len(matched) / len(job_skills))
    else:
        resume_words = set(re.findall(r"\b[a-z][a-z+#.]{2,}\b", clean_text(resume_text)))
        job_words = set(re.findall(r"\b[a-z][a-z+#.]{2,}\b", clean_text(job_text)))
        stop = {"the","and","for","with","you","our","are","will","this","that","from","have","has","your","job","role","work","years","year"}
        job_words -= stop
        score = round(100 * len(resume_words & job_words) / max(1, len(job_words)))
        matched = sorted(resume_words & job_words)[:30]
        missing = sorted(job_words - resume_words)[:30]
    return score, matched, missing, sorted(resume_skills), sorted(job_skills)

def make_questions(job_text, missing):
    role = "this role"
    lines = [x.strip(" •\t-") for x in (job_text or "").splitlines() if x.strip()]
    for line in lines[:8]:
        if len(line) > 12 and len(line) < 100:
            role = line
            break
    questions = [
        f"Walk me through your background and why it fits {role}.",
        "Describe a project where you solved a difficult technical problem. What trade-offs did you make?",
        "Tell me about a time you had to learn a new tool or concept quickly.",
        "How do you test your work and make sure the result is reliable?",
        "Describe a time you received critical feedback and how you responded.",
    ]
    for skill in missing[:3]:
        questions.append(f"What do you know about {skill}, and how would you apply it in a practical project?")
    return questions

def badge_list(items, missing=False):
    if not items:
        return '<span style="color:#8d95ad">No clear matches found yet.</span>'
    klass = "pill-missing" if missing else "pill"
    return "".join(f'<span class="{klass}">{html.escape(str(item))}</span>' for item in items)

st.markdown("""
<div class="hero">
  <div class="eyebrow">✦ NEXTROLE <span style="opacity:.5">/</span> CAREER STUDIO</div>
  <h1 style="margin-top:22px">Make your next move<br><span class="spark">feel inevitable.</span></h1>
  <p class="subhead">A calmer, smarter way to prepare for your next opportunity. Compare your resume with a job description, discover skill gaps, and walk into interviews with a plan.</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="glass-card"><div class="small-label">01 · Understand</div><h3>Resume intelligence</h3><p style="color:#aeb4c9">Extract the skills your resume actually communicates.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="glass-card"><div class="small-label">02 · Align</div><h3>Role fit analysis</h3><p style="color:#aeb4c9">See matching strengths and missing keywords at a glance.</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="glass-card"><div class="small-label">03 · Prepare</div><h3>Interview practice</h3><p style="color:#aeb4c9">Turn your gaps into focused practice questions.</p></div>', unsafe_allow_html=True)

st.markdown("## Your career workspace")
st.markdown("<p style='color:#9fa7c0'>Your text stays in this app session. No AI API key is required; analysis uses transparent local keyword matching, not a hosted LLM.</p>", unsafe_allow_html=True)

left, right = st.columns([0.9, 1.1], gap="large")
with left:
    with st.container(border=True):
        st.markdown("### Your resume")
        upload = st.file_uploader("Upload PDF, DOCX or TXT", type=["pdf", "docx", "txt"], help="For best results, use a text-based PDF rather than a scanned image.")
        resume_text = extract_resume(upload)
        if upload is not None and not resume_text.strip():
            st.warning("We couldn't extract text from that file. Try a text-based PDF, DOCX or TXT file.")
        resume_text = st.text_area("Or paste resume text", value=resume_text, height=250, placeholder="Paste your resume here: summary, skills, projects, education and experience...")
        st.caption("Tip: include project details and tools you used. Do not add skills you cannot discuss honestly.")
with right:
    with st.container(border=True):
        st.markdown("### Target opportunity")
        role_title = st.text_input("Role title (optional)", placeholder="e.g. Junior Python Developer")
        job_text = st.text_area("Job description", height=320, placeholder="Paste the complete job description here, including responsibilities and requirements...")
        st.caption("A detailed job description gives a more useful comparison.")

analyze = st.button("✦  Analyze my fit", type="primary", use_container_width=True)
if analyze:
    if len(resume_text.strip()) < 40:
        st.error("Add a little more resume text before analyzing.")
    elif len(job_text.strip()) < 40:
        st.error("Paste the job description so NextRole can compare both sides.")
    else:
        score, matched, missing, resume_skills, job_skills = score_match(resume_text, job_text)
        st.session_state["analysis"] = {
            "score": score, "matched": matched, "missing": missing,
            "resume_skills": resume_skills, "job_skills": job_skills,
            "questions": make_questions(job_text, missing),
            "role": role_title.strip() or "Target role",
        }

if "analysis" in st.session_state:
    data = st.session_state["analysis"]
    st.markdown("---")
    st.markdown("## Your fit snapshot")
    st.markdown(f"<p style='color:#aab1c7'>Analysis for <b>{html.escape(data['role'])}</b> · based on detected skills and text overlap</p>", unsafe_allow_html=True)
    a, b, c, d = st.columns(4)
    a.metric("Role match", f"{data['score']}%")
    b.metric("Skills matched", len(data["matched"]))
    c.metric("Potential gaps", len(data["missing"]))
    d.metric("Resume skills found", len(data["resume_skills"]))

    progress = max(0, min(100, data["score"]))
    st.markdown(f"""
    <div style="height:10px;border-radius:99px;background:rgba(255,255,255,.09);overflow:hidden;margin:14px 0 26px">
      <div style="height:100%;width:{progress}%;border-radius:99px;background:linear-gradient(90deg,#9b92ff,#9be7ff);box-shadow:0 0 24px rgba(153,151,255,.45);transition:width .8s ease"></div>
    </div>
    """, unsafe_allow_html=True)

    if data["score"] >= 75:
        st.success("Strong keyword alignment. Make sure your resume proves the skills with specific outcomes.")
    elif data["score"] >= 45:
        st.info("Some alignment is visible. Focus on relevant project evidence and the most important missing skills.")
    else:
        st.warning("The keyword overlap looks limited. Check whether this role is a fit and tailor your resume truthfully.")

    t1, t2, t3 = st.tabs(["✧ Strengths", "↗ Skill gaps", "◎ Interview prep"])
    with t1:
        st.markdown("### Skills already aligned")
        st.markdown(badge_list(data["matched"]), unsafe_allow_html=True)
        st.markdown("### Skills detected in your resume")
        st.markdown(badge_list(data["resume_skills"]), unsafe_allow_html=True)
    with t2:
        st.markdown("### Skills to investigate")
        st.markdown(badge_list(data["missing"], True), unsafe_allow_html=True)
        st.caption("A missing keyword does not prove you lack the skill. It may simply be described differently or omitted from your resume.")
        if data["missing"]:
            st.markdown("**A practical next step**")
            st.write("Choose one or two gaps that genuinely matter for the role. Learn the basics, build a small demonstrable project, and add evidence only after you have done the work.")
    with t3:
        st.markdown("### Questions to rehearse")
        for i, question in enumerate(data["questions"], 1):
            with st.container(border=True):
                st.markdown(f"**{i:02d}**  {question}")
        st.markdown("### Use the STAR structure")
        st.write("**Situation** — set the context. **Task** — explain your responsibility. **Action** — describe what you did. **Result** — share the outcome and what you learned.")

    report = [
        "NEXTROLE — CAREER FIT REPORT",
        f"Role: {data['role']}",
        f"Keyword alignment score: {data['score']}%",
        f"Matched skills: {', '.join(data['matched']) or 'None detected'}",
        f"Potential gaps: {', '.join(data['missing']) or 'None detected'}",
        "",
        "INTERVIEW PRACTICE",
        *[f"{i}. {q}" for i, q in enumerate(data["questions"], 1)],
        "",
        "Note: This is a local keyword heuristic, not an AI hiring decision or a prediction of interview success.",
    ]
    st.download_button("↓  Download my report", "\n".join(report), file_name="nextrole-career-report.txt", mime="text/plain")
    st.caption("Fairness note: this score is an approximate keyword signal only. It does not evaluate seniority, experience quality, communication, context, or real hiring decisions.")

st.markdown('<div class="footer">NEXTROLE · A focused space for your next chapter<br>Designed with a quiet, Apple-inspired aesthetic · No API key required</div>', unsafe_allow_html=True)
