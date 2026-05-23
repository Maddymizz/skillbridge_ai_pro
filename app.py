"""
SkillBridge AI Pro — Enhanced Edition
Powered by Groq LLaMA-3.3-70b
Features:
  - Resume Upload (PDF/DOCX) → AI Parser
  - Manual skill entry
  - Job Search → REAL links (LinkedIn, Naukri, Indeed, Internshala, Glassdoor)
  - Skill Gap Analysis (Groq)
  - AI Course Recommendations → REAL links (Udemy, Coursera, Internshala, YouTube, edX)
  - Career Trajectory Predictor
  - Role Compare
  - Career Map (all roles)
  - Market Intelligence Agent

BUG FIXES applied (from patch):
  1. Removed key= from skills display text_area so value=session_state always wins after rerun.
  2. Added OR-chain fallback in return so skills are never empty on first render tick.
  3. Manual tab now calls st.rerun() after writing to session_state so the display area updates immediately.
"""

import streamlit as st
import json
import os
import urllib.parse

from groq_client import (
    analyze_skills_with_groq,
    parse_resume_with_groq,
    fetch_courses_with_ai_agent,
    search_jobs_from_resume,
    get_market_intelligence,
)
from job_database import JOB_SKILL_DATABASE, ROLE_META, get_all_roles
from utils import (
    normalize_skills,
    calculate_match_score,
    get_skill_categories,
    extract_text_from_pdf,
    extract_text_from_docx,
    get_match_level,
)

# ─── Real Platform URL Builders ───────────────────────────────────────────────

COURSE_PLATFORMS = {
    "Udemy": {
        "base": "https://www.udemy.com/courses/search/?q={query}&sort=relevance&price=price-paid",
        "free_base": "https://www.udemy.com/courses/search/?q={query}&sort=relevance&price=price-free",
        "icon": "🎓",
        "color": "#a435f0",
        "badge": "UDEMY",
    },
    "Coursera": {
        "base": "https://www.coursera.org/search?query={query}",
        "icon": "🎓",
        "color": "#0056d2",
        "badge": "COURSERA",
    },
    "Internshala": {
        "base": "https://trainings.internshala.com/search-trainings/{query}/",
        "icon": "🎓",
        "color": "#006bff",
        "badge": "INTERNSHALA",
    },
    "edX": {
        "base": "https://www.edx.org/search?q={query}",
        "icon": "🎓",
        "color": "#02262b",
        "badge": "EDX",
    },
    "YouTube": {
        "base": "https://www.youtube.com/results?search_query={query}+tutorial+full+course",
        "icon": "▶️",
        "color": "#ff0000",
        "badge": "YOUTUBE FREE",
    },
    "LinkedIn Learning": {
        "base": "https://www.linkedin.com/learning/search?keywords={query}",
        "icon": "🎓",
        "color": "#0a66c2",
        "badge": "LINKEDIN",
    },
    "NPTEL": {
        "base": "https://nptel.ac.in/course.html#searchText={query}",
        "icon": "🎓",
        "color": "#f7941d",
        "badge": "NPTEL FREE",
    },
    "Great Learning": {
        "base": "https://www.mygreatlearning.com/academy/search?q={query}",
        "icon": "🎓",
        "color": "#1a3c5e",
        "badge": "GREAT LEARNING",
    },
    "Simplilearn": {
        "base": "https://www.simplilearn.com/search#q={query}",
        "icon": "🎓",
        "color": "#ff6b35",
        "badge": "SIMPLILEARN",
    },
}

JOB_PLATFORMS = {
    "LinkedIn": {
        "base": "https://www.linkedin.com/jobs/search/?keywords={query}&location={location}",
        "icon": "💼",
        "color": "#0a66c2",
        "badge": "LINKEDIN",
    },
    "Naukri": {
        "base": "https://www.naukri.com/{query_slug}-jobs?k={query}&l={location}",
        "icon": "🔍",
        "color": "#ff7555",
        "badge": "NAUKRI",
    },
    "Indeed": {
        "base": "https://in.indeed.com/jobs?q={query}&l={location}",
        "icon": "🔎",
        "color": "#003A9B",
        "badge": "INDEED",
    },
    "Internshala": {
        "base": "https://internshala.com/jobs/keywords-{query_slug}/",
        "icon": "🎯",
        "color": "#006bff",
        "badge": "INTERNSHALA",
    },
    "Glassdoor": {
        "base": "https://www.glassdoor.co.in/Job/jobs.htm?sc.keyword={query}&locT=C&locId=3&locKeyword={location}",
        "icon": "🏢",
        "color": "#0caa41",
        "badge": "GLASSDOOR",
    },
    "Shine": {
        "base": "https://www.shine.com/job-search/{query_slug}-jobs/",
        "icon": "✨",
        "color": "#f05a28",
        "badge": "SHINE",
    },
    "Instahyre": {
        "base": "https://www.instahyre.com/search-jobs/?job_role={query}",
        "icon": "⚡",
        "color": "#5b3cc4",
        "badge": "INSTAHYRE",
    },
    "AngelList": {
        "base": "https://wellfound.com/jobs?q={query}&l={location}",
        "icon": "🚀",
        "color": "#000000",
        "badge": "WELLFOUND",
    },
    "Cutshort": {
        "base": "https://cutshort.io/jobs?skills={query}",
        "icon": "✂️",
        "color": "#ff4f4f",
        "badge": "CUTSHORT",
    },
    "Foundit": {
        "base": "https://www.foundit.in/srp/results?query={query}&location={location}",
        "icon": "🔦",
        "color": "#e84646",
        "badge": "FOUNDIT",
    },
}


def build_course_url(platform: str, skill: str, free: bool = False) -> str:
    """Build a real search URL for a course platform."""
    p = COURSE_PLATFORMS.get(platform)
    if not p:
        return f"https://www.google.com/search?q={urllib.parse.quote(skill + ' course ' + platform)}"
    query = urllib.parse.quote(skill)
    base = p.get("free_base", p["base"]) if free else p["base"]
    return base.format(query=query)


def build_job_url(platform: str, role: str, location: str = "India") -> str:
    """Build a real search URL for a job platform."""
    p = JOB_PLATFORMS.get(platform)
    if not p:
        return f"https://www.google.com/search?q={urllib.parse.quote(role + ' jobs ' + location)}"
    query = urllib.parse.quote(role)
    query_slug = role.lower().replace(" ", "-").replace("/", "-")
    loc = urllib.parse.quote(location)
    return p["base"].format(query=query, query_slug=query_slug, location=loc)


def render_course_platform_buttons(skill: str, free_only: bool = False):
    """Render clickable platform buttons for a given skill."""
    paid_platforms   = ["Udemy", "Coursera", "Internshala", "LinkedIn Learning", "edX", "Simplilearn", "Great Learning"]
    free_platforms   = ["YouTube", "NPTEL", "Coursera", "edX", "Great Learning"]
    platforms_to_show = free_platforms if free_only else paid_platforms

    buttons_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:6px;'>"
    for pl in platforms_to_show:
        cfg = COURSE_PLATFORMS.get(pl, {})
        url = build_course_url(pl, skill, free=free_only)
        color = cfg.get("color", "#555")
        badge = cfg.get("badge", pl.upper())
        buttons_html += f"""
        <a href="{url}" target="_blank" style="
          text-decoration:none;
          padding:4px 10px;
          background:rgba(255,255,255,0.05);
          border:1px solid {color}55;
          border-radius:20px;
          font-size:0.68rem;
          font-weight:700;
          color:{color};
          letter-spacing:0.04em;
          transition:all 0.2s;
          white-space:nowrap;
        ">🔗 {badge}</a>"""
    buttons_html += "</div>"
    return buttons_html


def render_job_platform_buttons(role: str, location: str = "India"):
    """Render real job search buttons for all major platforms."""
    platforms = list(JOB_PLATFORMS.keys())
    buttons_html = "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;'>"
    for pl in platforms:
        cfg = JOB_PLATFORMS.get(pl, {})
        url = build_job_url(pl, role, location)
        color = cfg.get("color", "#555")
        badge = cfg.get("badge", pl.upper())
        icon  = cfg.get("icon", "🔗")
        buttons_html += f"""
        <a href="{url}" target="_blank" style="
          text-decoration:none;
          padding:5px 12px;
          background:rgba(255,255,255,0.04);
          border:1px solid {color}66;
          border-radius:20px;
          font-size:0.7rem;
          font-weight:700;
          color:{color};
          letter-spacing:0.04em;
          white-space:nowrap;
        ">{icon} {badge}</a>"""
    buttons_html += "</div>"
    return buttons_html


# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkillBridge AI Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Extra CSS for real link buttons ─────────────────────────────────────────
st.markdown("""
<style>
.platform-btn-group { display:flex; flex-wrap:wrap; gap:6px; margin:8px 0; }
.real-link-badge {
  display:inline-flex; align-items:center; gap:4px;
  padding:5px 12px;
  border-radius:20px;
  font-size:0.69rem; font-weight:700;
  text-decoration:none;
  letter-spacing:0.04em;
  transition: filter 0.2s, transform 0.15s;
  white-space:nowrap;
}
.real-link-badge:hover { filter:brightness(1.25); transform:translateY(-1px); }
.course-platform-row {
  display:flex; align-items:flex-start; gap:12px;
  padding:12px 0; border-bottom:1px solid var(--border);
}
.job-card-enhanced {
  background: rgba(255,255,255,0.025);
  border:1px solid var(--border);
  border-radius:12px;
  padding:16px 18px;
  margin-bottom:12px;
  transition: border-color 0.2s;
}
.job-card-enhanced:hover { border-color: rgba(99,179,237,0.4); }
.job-search-links { margin-top:10px; padding-top:10px; border-top:1px solid var(--border); }
</style>
""", unsafe_allow_html=True)

# ─── API Key Check ────────────────────────────────────────────────────────────
if not os.getenv("GROQ_API_KEY"):
    st.error("⚠️  GROQ_API_KEY not found in .env file. Please add it and restart.")
    st.code("GROQ_API_KEY=your_key_here", language="bash")
    st.markdown("Get your free key at [console.groq.com](https://console.groq.com)")
    st.stop()

# ─── Session State ────────────────────────────────────────────────────────────
for key, default in {
    "mode": "Analyze",
    "analysis_result": None,
    "history": [],
    "parsed_skills": "",
    "parsed_profile": {},
    "resume_text": "",
    "course_result": None,
    "job_result": None,
    "market_result": None,
    "job_location": "India",
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sb-header">
  <div class="sb-badge">✦ AI-Powered Career Intelligence — Groq LLaMA-3.3-70b</div>
  <h1 class="sb-title">
    Skill<span class="accent-cyan">Bridge</span>
    <span class="accent-purple">AI Pro</span>
  </h1>
  <p class="sb-subtitle">
    Upload Resume · AI Skill Gap Analysis · Real Courses · Live Job Links · Career Trajectory
  </p>
</div>
""", unsafe_allow_html=True)

# ─── Workflow Bar ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="wf-bar">
  <div class="wf-step"><span class="wf-num">1</span> Upload/Input</div>
  <div class="wf-arrow">›</div>
  <div class="wf-step"><span class="wf-num">2</span> AI Parse</div>
  <div class="wf-arrow">›</div>
  <div class="wf-step"><span class="wf-num">3</span> Gap Detect</div>
  <div class="wf-arrow">›</div>
  <div class="wf-step"><span class="wf-num">4</span> Real Courses</div>
  <div class="wf-arrow">›</div>
  <div class="wf-step"><span class="wf-num">5</span> Live Jobs</div>
  <div class="wf-arrow">›</div>
  <div class="wf-step"><span class="wf-num">6</span> Report</div>
</div>
""", unsafe_allow_html=True)

# ─── Mode Switcher ────────────────────────────────────────────────────────────
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns([1, 1, 1, 1, 1])
modes = [
    ("🔍 Analyze",      "Analyze"),
    ("💼 Job Search",   "Jobs"),
    ("⚖️ Compare",      "Compare"),
    ("🗺️ Career Map",   "Career Map"),
    ("📡 Market Intel", "Market"),
]
for col, (label, mode_key) in zip([col_m1, col_m2, col_m3, col_m4, col_m5], modes):
    with col:
        if st.button(label, use_container_width=True):
            st.session_state.mode = mode_key

current_mode = st.session_state.mode
st.markdown(
    f"<p style='color:var(--text-muted);font-size:0.72rem;margin-top:-0.4rem;'>"
    f"Mode: <span style='color:var(--accent-cyan)'>{current_mode}</span></p>",
    unsafe_allow_html=True
)
st.markdown("---")


# ═══════════════════════════════════════════════════════════════════════════════
#  SHARED: Resume Upload + Skills Input Panel
#  ── BUG FIXES APPLIED (3 fixes from patch) ──────────────────────────────────
#  Fix 1: skills display text_area has NO key= → value= always wins after rerun
#  Fix 2: manual tab now calls st.rerun() so display area updates immediately
#  Fix 3: return OR-chains skills_raw with session_state fallback (never empty)
# ═══════════════════════════════════════════════════════════════════════════════

def render_input_panel(show_role=True, role_key="role_main"):
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown(
        '<div class="card-title"><span class="icon icon-blue">📄</span> Resume & Skills Input</div>',
        unsafe_allow_html=True,
    )

    input_tab1, input_tab2 = st.tabs(["📎 Upload Resume (PDF/DOCX)", "✏️ Type Skills Manually"])

    with input_tab1:
        uploaded = st.file_uploader(
            "Upload your resume",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            key=f"uploader_{role_key}",  # keep key here so Streamlit deduplicates the widget
        )
        if uploaded:
            file_bytes = uploaded.read()
            ext = uploaded.name.split(".")[-1].lower()
            with st.spinner("🤖 Extracting text from resume..."):
                raw_text = extract_text_from_pdf(file_bytes) if ext == "pdf" else extract_text_from_docx(file_bytes)

            if raw_text.startswith("ERROR"):
                st.error(raw_text)
            else:
                if st.session_state.resume_text != raw_text:
                    st.session_state.resume_text = raw_text
                    with st.spinner("🧠 AI is parsing your resume..."):
                        profile = parse_resume_with_groq(raw_text)
                        st.session_state.parsed_profile = profile
                        # FIX 1: write directly into session_state — the unkeyed
                        # text_area below picks this up on the rerun.
                        st.session_state.parsed_skills = profile.get("skills", "")
                        st.session_state.input_experience = profile.get("experience_years", "")
                        st.session_state.input_education  = profile.get("education", "")
                    st.rerun()

                prof = st.session_state.parsed_profile
                if prof:
                    st.markdown(
                        f"""
                        <div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:0.8rem;'>
                          <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;color:var(--accent-cyan)'>{prof.get("name","—")}</span><span class='stat-label'>Name</span></div>
                          <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;'>{prof.get("title","—")}</span><span class='stat-label'>Title</span></div>
                          <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;color:var(--accent-green)'>{prof.get("experience_years","—")}</span><span class='stat-label'>Experience</span></div>
                          <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;'>{prof.get("education","—")}</span><span class='stat-label'>Education</span></div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if prof.get("summary"):
                        st.markdown(
                            f"<div style='font-size:0.78rem;color:var(--text-secondary);padding:8px 12px;"
                            f"background:rgba(99,179,237,0.04);border-left:2px solid var(--accent-cyan);"
                            f"border-radius:0 6px 6px 0;margin-top:0.6rem;'>{prof['summary']}</div>",
                            unsafe_allow_html=True,
                        )
                    st.success(
                        f"✅ Extracted {len(normalize_skills(st.session_state.parsed_skills))} skills from resume"
                    )
                    if st.button("🔄 Re-extract Skills", key=f"reextract_{role_key}"):
                        st.session_state.resume_text = ""  # force re-parse on next run
                        st.rerun()

    with input_tab2:
        manual = st.text_area(
            "Enter your skills (comma-separated)",
            placeholder="Python, React.js, Machine Learning, Docker, SQL, AWS...",
            height=80,
            label_visibility="collapsed",
            key=f"manual_skills_{role_key}",
        )
        if manual.strip() and manual.strip() != st.session_state.parsed_skills:
            # FIX 2: write to session_state AND rerun so the main textarea reflects it immediately
            st.session_state.parsed_skills = manual.strip()
            st.rerun()

    # ── Skills display textarea ───────────────────────────────────────────────
    # FIX 1 (continued): NO key= here. Without a key, Streamlit re-evaluates
    # value= on every run, so after st.rerun() the updated session_state value
    # is shown immediately. A keyed widget would cache the old empty value.
    skills_raw = st.text_area(
        "🔧 Skills (auto-filled from resume, or edit manually)",
        value=st.session_state.parsed_skills,   # always reflects latest state
        height=70,
        # ← intentionally no key= here
    )

    # If the user edits the display textarea directly, sync back to session_state
    if skills_raw != st.session_state.parsed_skills:
        st.session_state.parsed_skills = skills_raw

    if show_role:
        all_roles = get_all_roles()
        suggested = st.session_state.parsed_profile.get("suggested_roles", [])
        default_idx = 0
        if suggested:
            for i, r in enumerate(all_roles):
                if r in suggested:
                    default_idx = i
                    break
        target_role = st.selectbox("🎯 Target Job Role", all_roles, index=default_idx, key=role_key)
        if suggested:
            st.markdown(
                f"<div style='font-size:0.72rem;color:var(--text-muted);margin-top:-6px;'>"
                f"AI suggested: {', '.join(suggested[:3])}</div>",
                unsafe_allow_html=True,
            )
    else:
        target_role = None

    prof = st.session_state.parsed_profile
    exp_col, edu_col = st.columns(2)
    with exp_col:
        experience = st.text_input(
            "Experience",
            value=prof.get("experience_years", ""),
            placeholder="e.g. 2 years",
            key=f"input_experience",
        )
    with edu_col:
        education = st.text_input(
            "Education",
            value=prof.get("education", ""),
            placeholder="e.g. B.Tech CS",
            key=f"input_education",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # FIX 3: OR-chain so we never return an empty list when session_state has skills.
    # Guards against the edge case where skills_raw is empty on the very first
    # render tick after a rerun (before the unkeyed widget value propagates).
    user_skills = normalize_skills(skills_raw) or normalize_skills(st.session_state.parsed_skills)
    return user_skills, target_role, experience, education


# ═══════════════════════════════════════════════════════════════════════════════
#  SHARED: Role Preview
# ═══════════════════════════════════════════════════════════════════════════════

def render_role_preview(role: str, matched_skills: list = None):
    role_data   = JOB_SKILL_DATABASE.get(role, {})
    required    = role_data.get("required_skills", [])
    nice        = role_data.get("nice_to_have", [])
    meta        = ROLE_META.get(role, {"salary": "Varies", "demand": 75, "growth": "+10%", "icon": "💼"})
    matched_set = set(s.lower() for s in (matched_skills or []))

    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:12px;margin-bottom:1rem;'>
      <div style='font-size:2.2rem'>{meta['icon']}</div>
      <div>
        <div style='font-family:var(--font-display);font-size:1.1rem;font-weight:700;'>{role}</div>
        <div class='glow-pill'>India Market 2025</div>
      </div>
    </div>
    <div class='stats-row'>
      <div class='stat-chip'><span class='stat-value'>{meta['salary']}</span><span class='stat-label'>Salary Range</span></div>
      <div class='stat-chip'><span class='stat-value' style='color:var(--accent-green)'>{meta['growth']}</span><span class='stat-label'>YoY Growth</span></div>
      <div class='stat-chip'><span class='stat-value'>{len(required)}</span><span class='stat-label'>Core Skills</span></div>
    </div>
    <div class='demand-meter'>
      <div class='demand-label'><span>Market Demand</span><span style='color:var(--accent-cyan)'>{meta['demand']}%</span></div>
      <div class='demand-track'><div class='demand-fill' style='width:{meta["demand"]}%'></div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size:0.75rem;color:var(--text-muted);font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin:1rem 0 6px;'>Required Skills</div>", unsafe_allow_html=True)
    tags_html = "<div class='skill-tags'>"
    for s in required:
        if matched_set and s.lower() in matched_set:
            tags_html += f"<span class='skill-tag tag-matched'>✓ {s}</span>"
        else:
            tags_html += f"<span class='skill-tag tag-required' style='background:rgba(252,129,129,0.1);border:1px solid rgba(252,129,129,0.25);color:var(--accent-red);'>{s}</span>"
    tags_html += "</div>"
    st.markdown(tags_html, unsafe_allow_html=True)

    if nice:
        st.markdown("<div style='font-size:0.75rem;color:var(--text-muted);font-weight:600;letter-spacing:0.06em;text-transform:uppercase;margin:0.8rem 0 6px;'>Nice to Have</div>", unsafe_allow_html=True)
        nice_html = "<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-nice'>{s}</span>" for s in nice) + "</div>"
        st.markdown(nice_html, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENHANCED: Course Card Renderer with REAL links
# ═══════════════════════════════════════════════════════════════════════════════

def render_course_card_with_real_links(c: dict, skill: str, is_free: bool = False):
    """Render a course card with real clickable platform links."""
    price   = c.get("price", "")
    is_free = is_free or ("free" in price.lower() if price else False)
    card_cls= "course-free" if is_free else "course-premium"
    platform= c.get("platform", "")
    title   = c.get("title", "—")
    url_hint= c.get("url_hint", skill)

    real_url = build_course_url(platform, url_hint or skill, free=is_free)
    cfg      = COURSE_PLATFORMS.get(platform, {})
    p_color  = cfg.get("color", "#63b3ed")
    p_badge  = cfg.get("badge", platform.upper())

    all_links_html = render_course_platform_buttons(skill, free_only=False)

    st.markdown(f"""
    <div class='course-card {card_cls}' style='position:relative;'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
        <div style='flex:1;'>
          <a href="{real_url}" target="_blank" style='
            font-size:0.88rem;font-weight:700;
            color:var(--text-primary);text-decoration:none;
            display:block;margin-bottom:4px;
            transition:color 0.2s;
          ' onmouseover="this.style.color='var(--accent-cyan)'" onmouseout="this.style.color='var(--text-primary)'">
            {title} ↗
          </a>
          <div style='font-size:0.76rem;color:var(--text-secondary);'>{c.get('why_recommended','')}</div>
        </div>
        <a href="{real_url}" target="_blank" style='
          text-decoration:none;padding:4px 10px;
          background:{p_color}22;border:1px solid {p_color}55;
          border-radius:20px;font-size:0.65rem;font-weight:800;
          color:{p_color};white-space:nowrap;margin-left:10px;letter-spacing:0.05em;
        '>{p_badge}</a>
      </div>
      <div class='course-meta' style='margin-top:8px;'>
        <span>👤 {c.get('instructor','')}</span>
        <span>⏱️ {c.get('duration','')}</span>
        <span>📊 {c.get('difficulty','')}</span>
        <span style='color:{"var(--accent-green)" if is_free else "var(--accent-orange)"};font-weight:700;'>
          💰 {price}
        </span>
        <span>⭐ {c.get('rating','')}</span>
      </div>
      <div style='margin-top:10px;'>
        <div style='font-size:0.68rem;color:var(--text-muted);margin-bottom:4px;font-weight:600;text-transform:uppercase;letter-spacing:0.06em;'>
          🔗 Also find on:
        </div>
        {all_links_html}
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_free_resource_with_links(free: dict, skill: str):
    """Render a free resource card with real links."""
    title    = free.get("title", "Free Alternative")
    platform = free.get("platform", "YouTube")
    url_hint = free.get("url_hint", skill)
    real_url = build_course_url(platform, url_hint or skill, free=True)
    cfg      = COURSE_PLATFORMS.get(platform, {})
    p_color  = cfg.get("color", "#ff0000")
    p_badge  = cfg.get("badge", platform.upper())

    free_links = render_course_platform_buttons(skill, free_only=True)

    st.markdown(f"""
    <div class='course-card course-free' style='opacity:0.9;'>
      <div style='display:flex;align-items:center;gap:8px;'>
        <span style='font-size:0.75rem;font-weight:800;color:var(--accent-green);background:rgba(104,211,145,0.1);
          padding:2px 8px;border-radius:10px;border:1px solid rgba(104,211,145,0.3);'>🆓 FREE</span>
        <a href="{real_url}" target="_blank" style='
          font-size:0.85rem;font-weight:700;
          color:var(--text-primary);text-decoration:none;
        '>{title} ↗</a>
        <a href="{real_url}" target="_blank" style='
          text-decoration:none;padding:2px 8px;
          background:{p_color}22;border:1px solid {p_color}55;
          border-radius:10px;font-size:0.62rem;font-weight:800;
          color:{p_color};letter-spacing:0.05em;
        '>{p_badge}</a>
      </div>
      <div style='margin-top:8px;'>
        <div style='font-size:0.68rem;color:var(--text-muted);margin-bottom:4px;'>Free alternatives:</div>
        {free_links}
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  ENHANCED: Job Card Renderer with REAL links
# ═══════════════════════════════════════════════════════════════════════════════

def render_job_card_with_real_links(job: dict, index: int, location: str = "India"):
    """Render a job recommendation card with real platform search links."""
    fit       = job.get("fit_score", 0)
    fit_color = "var(--accent-green)" if fit >= 80 else "var(--accent-cyan)" if fit >= 60 else "var(--accent-orange)"
    title     = job.get("title", "—")
    company_types = " · ".join(job.get("company_types", []))
    skills_hl = job.get("skills_to_highlight", [])
    salary    = job.get("salary_range", "—")
    why_fit   = job.get("why_fit", "")

    job_links_html = render_job_platform_buttons(title, location)

    search_q  = job.get("search_query", title)
    google_url= f"https://www.google.com/search?q={urllib.parse.quote(search_q + ' jobs ' + location)}"

    st.markdown(f"""
    <div class='job-card-enhanced'>
      <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
        <div style='flex:1;'>
          <div style='font-family:var(--font-display);font-size:1rem;font-weight:700;margin-bottom:4px;'>
            {index}. {title}
          </div>
          <div style='font-size:0.78rem;color:var(--text-muted);'>{why_fit}</div>
        </div>
        <div style='
          font-family:var(--font-mono);font-size:1.1rem;font-weight:800;
          color:{fit_color};text-align:center;min-width:60px;
        '>{fit}%<div style='font-size:0.6rem;color:var(--text-muted);font-weight:400;'>fit score</div></div>
      </div>
      <div class='stats-row' style='gap:8px;margin-top:10px;'>
        <div class='stat-chip' style='padding:0.4rem;'>
          <span class='stat-value' style='font-size:0.8rem;color:var(--accent-green)'>{salary}</span>
          <span class='stat-label'>Salary (India)</span>
        </div>
        <div class='stat-chip' style='padding:0.4rem;'>
          <span class='stat-value' style='font-size:0.75rem;'>{company_types}</span>
          <span class='stat-label'>Company Type</span>
        </div>
      </div>
      <div style='margin-top:8px;'>
        <div class='skill-tags'>
          {"".join(f"<span class='skill-tag tag-matched'>★ {s}</span>" for s in skills_hl)}
        </div>
      </div>
      <div class='job-search-links'>
        <div style='font-size:0.7rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>
          🔍 Apply on these platforms:
        </div>
        {job_links_html}
        <div style='margin-top:6px;'>
          <a href="{google_url}" target="_blank" style='
            font-size:0.68rem;color:var(--text-muted);text-decoration:none;
          '>📋 Search query: <code style="color:var(--accent-cyan);">{search_q}</code> ↗</a>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE 1: ANALYZE
# ═══════════════════════════════════════════════════════════════════════════════

if current_mode == "Analyze":
    st.markdown('<div class="section-heading">🔍 AI Skill Gap Analysis</div>', unsafe_allow_html=True)

    user_skills, target_role, experience, education = render_input_panel(role_key="analyze_role")
    # Fallback: if widget returned empty but session has skills (e.g. first render after upload)
    if not user_skills and st.session_state.parsed_skills:
        user_skills = normalize_skills(st.session_state.parsed_skills)

    analyze_col, _ = st.columns([1, 3])
    with analyze_col:
        analyze_btn = st.button("🚀 Run AI Analysis", use_container_width=True, type="primary")

    if analyze_btn and user_skills and target_role:
        with st.spinner("🤖 Groq LLaMA analyzing your profile... (3 AI calls)"):
            req_skills = JOB_SKILL_DATABASE.get(target_role, {}).get("required_skills", [])
            matched, missing = calculate_match_score(user_skills, req_skills)
            match_pct = round(len(matched) / len(req_skills) * 100) if req_skills else 0

            result = analyze_skills_with_groq(
                user_skills=user_skills,
                target_role=target_role,
                matched_skills=matched,
                missing_skills=missing,
                experience=experience,
                education=education,
                all_roles=get_all_roles(),
                job_db=JOB_SKILL_DATABASE
            )
            result["match_pct"] = match_pct
            result["matched"]   = matched
            result["missing"]   = missing
            result["role"]      = target_role
            st.session_state.analysis_result = result
            st.session_state.history.append({"role": target_role, "score": match_pct})

    elif analyze_btn:
        st.warning("Please enter your skills and select a target role.")

    # ── Results ──────────────────────────────────────────────────────────────
    if st.session_state.analysis_result:
        res = st.session_state.analysis_result
        match_pct = res["match_pct"]
        matched   = res["matched"]
        missing   = res["missing"]
        role      = res["role"]
        _, color, emoji = get_match_level(match_pct)

        st.markdown("---")
        sc1, sc2, sc3 = st.columns([1, 1.5, 1.5])

        with sc1:
            st.markdown('<div class="glass-card" style="text-align:center;height:100%">', unsafe_allow_html=True)
            circumference = 2 * 3.14159 * 40
            dash = circumference * match_pct / 100
            st.markdown(f"""
            <div class="score-ring-wrap">
              <svg class="score-ring-svg" width="100" height="100" viewBox="0 0 100 100">
                <circle class="score-ring-bg" cx="50" cy="50" r="40"/>
                <circle class="score-ring-fill" cx="50" cy="50" r="40"
                  stroke="{color}"
                  stroke-dasharray="{circumference}"
                  stroke-dashoffset="{circumference - dash}"/>
              </svg>
              <div class="score-center">
                <span class="score-pct" style="color:{color}">{match_pct}%</span>
                <span class="score-sub">Match</span>
              </div>
            </div>
            <div style='text-align:center;margin-top:0.5rem;'>
              <div style='font-family:var(--font-display);font-weight:700;font-size:0.85rem;'>{role}</div>
            </div>
            """, unsafe_allow_html=True)

            verdict = res.get("readiness_verdict", "")
            v_class = {
                "Ready to Apply": "verdict-ready",
                "Almost There":   "verdict-close",
                "Needs 3-6 months": "verdict-soon",
                "Major Gap":      "verdict-gap"
            }.get(verdict, "verdict-close")
            if verdict:
                st.markdown(f"<div style='text-align:center;margin-top:8px;'><span class='verdict-badge {v_class}'>{verdict}</span></div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='font-size:0.68rem;color:var(--text-muted);margin-bottom:6px;font-weight:600;text-transform:uppercase;'>Quick Apply:</div>
            {render_job_platform_buttons(role, st.session_state.get("job_location","India"))}
            """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with sc2:
            st.markdown('<div class="glass-card" style="height:100%">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon icon-green">✅</span> Matched Skills</div>', unsafe_allow_html=True)
            if matched:
                tags = "<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-matched'>✓ {s}</span>" for s in matched) + "</div>"
            else:
                tags = "<p style='color:var(--text-muted);font-size:0.8rem;'>No matches found</p>"
            st.markdown(tags, unsafe_allow_html=True)
            if res.get("top_strength"):
                st.markdown(f"<div style='margin-top:1rem;font-size:0.78rem;padding:8px 12px;background:rgba(104,211,145,0.06);border-left:2px solid var(--accent-green);border-radius:0 6px 6px 0;color:var(--text-secondary);'>💪 {res['top_strength']}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with sc3:
            st.markdown('<div class="glass-card" style="height:100%">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon icon-blue">❌</span> Missing Skills</div>', unsafe_allow_html=True)
            if missing:
                tags = "<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-missing'>✗ {s}</span>" for s in missing) + "</div>"
                st.markdown(tags, unsafe_allow_html=True)
                st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
                st.markdown("<div style='font-size:0.68rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>Learn missing skills:</div>", unsafe_allow_html=True)
                for ms in missing[:4]:
                    ms_url = build_course_url("Udemy", ms)
                    yt_url = build_course_url("YouTube", ms, free=True)
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:6px;margin-bottom:4px;'>
                      <span style='font-size:0.72rem;color:var(--text-secondary);flex:1;'>{ms}</span>
                      <a href="{ms_url}" target="_blank" class='real-link-badge' style='background:#a435f022;border:1px solid #a435f055;color:#a435f0;'>Udemy</a>
                      <a href="{yt_url}" target="_blank" class='real-link-badge' style='background:#ff000022;border:1px solid #ff000055;color:#ff4444;'>YouTube</a>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:var(--accent-green);font-size:0.8rem;'>✨ All required skills matched!</p>", unsafe_allow_html=True)
            if res.get("critical_gap"):
                st.markdown(f"<div style='margin-top:1rem;font-size:0.78rem;padding:8px 12px;background:rgba(252,129,129,0.06);border-left:2px solid var(--accent-red);border-radius:0 6px 6px 0;color:var(--text-secondary);'>🎯 Learn first: {res['critical_gap']}</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── Role Preview ─────────────────────────────────────────────────────
        with st.expander(f"📋 {role} — Full Job Requirements"):
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            render_role_preview(role, matched)
            st.markdown('</div>', unsafe_allow_html=True)

        # ── AI Tabs ──────────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        tab1, tab2, tab3, tab4 = st.tabs(["💡 Insights & Path", "📚 AI Course Agent", "🗺️ Career Trajectory", "📄 Full Report"])

        with tab1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            insights = res.get("skill_insights", "")
            if insights:
                st.markdown(f"""
                <div style='padding:1rem;background:rgba(99,179,237,0.05);border-left:2px solid var(--accent-cyan);
                  border-radius:0 var(--radius-sm) var(--radius-sm) 0;margin-bottom:1.2rem;
                  font-size:0.88rem;line-height:1.7;color:var(--text-secondary);'>
                  {insights}
                </div>
                """, unsafe_allow_html=True)

            lp = res.get("learning_path", [])
            if lp:
                st.markdown('<div class="card-title"><span class="icon icon-purple">📚</span> AI Learning Path</div>', unsafe_allow_html=True)
                for item in lp:
                    pri     = item.get("priority", "Medium")
                    pri_cls = {"High": "pri-high", "Medium": "pri-medium", "Low": "pri-low"}.get(pri, "pri-medium")
                    why     = item.get("why", "")
                    skill_name = item.get('skill','')
                    udemy_url  = build_course_url("Udemy", skill_name)
                    coursera_url = build_course_url("Coursera", skill_name)
                    yt_url     = build_course_url("YouTube", skill_name, free=True)
                    st.markdown(f"""
                    <div class='lp-row'>
                      <span class='lp-priority {pri_cls}'>{pri}</span>
                      <span class='lp-skill'>{skill_name}</span>
                      <span class='lp-resource'>{item.get('resource','')}</span>
                      <span class='lp-duration'>{item.get('duration','')}</span>
                    </div>
                    <div style='padding:2px 12px 8px 12px;display:flex;gap:6px;flex-wrap:wrap;align-items:center;'>
                      {f"<span style='font-size:0.72rem;color:var(--text-muted);flex:1;'>{why}</span>" if why else ""}
                      <a href="{udemy_url}" target="_blank" class='real-link-badge' style='background:#a435f022;border:1px solid #a435f055;color:#a435f0;font-size:0.62rem;padding:2px 8px;'>Udemy ↗</a>
                      <a href="{coursera_url}" target="_blank" class='real-link-badge' style='background:#0056d222;border:1px solid #0056d255;color:#0056d2;font-size:0.62rem;padding:2px 8px;'>Coursera ↗</a>
                      <a href="{yt_url}" target="_blank" class='real-link-badge' style='background:#ff000022;border:1px solid #ff000055;color:#ff4444;font-size:0.62rem;padding:2px 8px;'>YouTube ↗</a>
                    </div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon icon-purple">🤖</span> AI Course Recommendation Agent</div>', unsafe_allow_html=True)

            if missing:
                exp_level = experience or "Mid"
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    learn_style = st.selectbox("Learning Style", ["Video + Hands-on", "Reading + Projects", "Bootcamp Style", "Self-paced"], key="learn_style")
                with c2:
                    st.markdown(f"<div style='padding-top:1.8rem;font-size:0.8rem;color:var(--text-muted);'>Missing: <b style='color:var(--accent-red)'>{len(missing)} skills</b></div>", unsafe_allow_html=True)
                with c3:
                    fetch_btn = st.button("🤖 Fetch AI Courses", use_container_width=True)

                st.markdown("""
                <div style='padding:12px 16px;background:rgba(99,179,237,0.05);border:1px solid rgba(99,179,237,0.15);
                  border-radius:10px;margin:12px 0;'>
                  <div style='font-size:0.72rem;color:var(--accent-cyan);font-weight:700;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:8px;'>
                    ⚡ Browse Courses Instantly — No AI needed
                  </div>
                """, unsafe_allow_html=True)
                for ms in missing:
                    st.markdown(f"<div style='margin-bottom:6px;'><span style='font-size:0.78rem;font-weight:600;color:var(--text-secondary);display:inline-block;min-width:160px;'>{ms}</span>", unsafe_allow_html=True)
                    st.markdown(render_course_platform_buttons(ms, free_only=False), unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                if fetch_btn:
                    with st.spinner(f"🧠 AI agent fetching personalized course picks for {len(missing)} skills..."):
                        st.session_state.course_result = fetch_courses_with_ai_agent(
                            missing_skills=missing,
                            target_role=role,
                            experience_level=exp_level,
                            learning_style=learn_style
                        )

                cr = st.session_state.course_result
                if cr:
                    roadmap = cr.get("learning_roadmap", {})
                    if roadmap:
                        st.markdown("<div style='margin:1rem 0 0.5rem;font-size:0.8rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;'>Learning Roadmap</div>", unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class='stats-row'>
                          <div class='stat-chip'><span class='stat-value' style='font-size:0.9rem;color:var(--accent-cyan)'>{roadmap.get('total_duration','—')}</span><span class='stat-label'>Total Duration</span></div>
                          <div class='stat-chip'><span class='stat-value' style='font-size:0.9rem;'>{roadmap.get('weekly_hours','—')}</span><span class='stat-label'>Weekly Hours</span></div>
                        </div>
                        """, unsafe_allow_html=True)
                        for i, ms in enumerate(["milestone_1", "milestone_2", "milestone_3"], 1):
                            if roadmap.get(ms):
                                st.markdown(f"<div style='font-size:0.78rem;padding:6px 12px;background:rgba(183,148,244,0.05);border-left:2px solid var(--accent-purple);border-radius:0 6px 6px 0;margin-bottom:4px;color:var(--text-secondary);'><b style='color:var(--accent-purple);'>Month {i}:</b> {roadmap[ms]}</div>", unsafe_allow_html=True)

                    courses_list = cr.get("courses", [])
                    for skill_entry in courses_list:
                        skill_name = skill_entry.get("skill", "Unknown")
                        priority   = skill_entry.get("priority", "Medium")
                        p_cls      = {"High": "pri-high", "Medium": "pri-medium", "Low": "pri-low"}.get(priority, "pri-medium")

                        st.markdown(f"""
                        <div style='display:flex;align-items:center;gap:8px;margin:1.2rem 0 0.6rem;'>
                          <span class='lp-priority {p_cls}'>{priority}</span>
                          <span style='font-family:var(--font-display);font-weight:700;font-size:0.95rem;'>{skill_name}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        for c in skill_entry.get("courses", []):
                            render_course_card_with_real_links(c, skill_name)

                        free = skill_entry.get("free_resource", {})
                        if free:
                            render_free_resource_with_links(free, skill_name)

                        project = skill_entry.get("practice_project", "")
                        if project:
                            st.markdown(f"<div style='font-size:0.78rem;padding:6px 12px;background:rgba(104,211,145,0.05);border:1px dashed rgba(104,211,145,0.2);border-radius:6px;color:var(--text-secondary);margin-bottom:0.5rem;'>🛠️ <b>Practice Project:</b> {project}</div>", unsafe_allow_html=True)

                    certs = cr.get("certification_path", [])
                    if certs:
                        st.markdown("<div style='margin:1rem 0 0.5rem;font-size:0.8rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;'>Recommended Certifications</div>", unsafe_allow_html=True)
                        for cert in certs:
                            cert_name = cert.get('certification','—')
                            provider  = cert.get('provider','')
                            cert_url  = f"https://www.google.com/search?q={urllib.parse.quote(cert_name + ' ' + provider + ' certification')}"
                            st.markdown(f"""
                            <div class='traj-card'>
                              <div class='traj-role'>
                                🏅 <a href="{cert_url}" target="_blank" style='color:var(--accent-cyan);text-decoration:none;'>{cert_name}</a>
                                — <span style='color:var(--text-muted);font-weight:400;'>{provider}</span>
                              </div>
                              <div class='traj-note'>{cert.get('relevance','')} · Prep: {cert.get('estimated_prep','')}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    qw = cr.get("quick_wins", [])
                    if qw:
                        st.markdown("<div style='margin:1rem 0 0.5rem;font-size:0.8rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;'>⚡ Quick Wins — Start Today</div>", unsafe_allow_html=True)
                        for i, win in enumerate(qw, 1):
                            st.markdown(f"<div class='quick-win'><div class='quick-win-num'>{i}</div><div>{win}</div></div>", unsafe_allow_html=True)

                else:
                    st.info("Click 'Fetch AI Courses' above to get personalized AI course picks, or use the instant browse links above right now.")
            else:
                st.success("🎉 No missing skills! You're fully qualified for this role.")

            st.markdown('</div>', unsafe_allow_html=True)

        with tab3:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            ct   = res.get("career_trajectory", {})
            pred = ct.get("predicted_score_in_6months")

            if pred:
                sal = ct.get("salary_trajectory", {})
                st.markdown(f"""
                <div class='stats-row'>
                  <div class='stat-chip'><span class='stat-value'>{match_pct}%</span><span class='stat-label'>Today</span></div>
                  <div class='stat-chip' style='font-size:1.5rem;color:var(--accent-green);display:flex;align-items:center;justify-content:center;'>→</div>
                  <div class='stat-chip'><span class='stat-value' style='color:var(--accent-green)'>{pred}%</span><span class='stat-label'>In 6 Months</span></div>
                </div>
                """, unsafe_allow_html=True)
                if sal:
                    st.markdown('<div class="card-title" style="margin-top:1rem"><span class="icon icon-orange">💰</span> Salary Trajectory</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='stats-row'>
                      <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;'>{sal.get('current','—')}</span><span class='stat-label'>Current</span></div>
                      <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;color:var(--accent-cyan);'>{sal.get('in_6_months','—')}</span><span class='stat-label'>In 6 Months</span></div>
                      <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;color:var(--accent-green);'>{sal.get('in_1_year','—')}</span><span class='stat-label'>In 1 Year</span></div>
                    </div>
                    """, unsafe_allow_html=True)

            imm = ct.get("immediate_roles", [])
            if imm:
                st.markdown('<div class="card-title" style="margin-top:1rem"><span class="icon icon-blue">🚀</span> Roles You Can Apply to Now</div>', unsafe_allow_html=True)
                for item in imm:
                    name  = item.get("role", str(item)) if isinstance(item, dict) else str(item)
                    note  = item.get("reason", "") if isinstance(item, dict) else ""
                    score = item.get("match_score", "") if isinstance(item, dict) else ""
                    score_str = f" · {score}% match" if score else ""
                    st.markdown(f"""
                    <div class='traj-card'>
                      <div class='traj-role'>🎯 {name}{score_str}</div>
                      <div class='traj-note'>{note}</div>
                      <div style='margin-top:6px;'>{render_job_platform_buttons(name, st.session_state.get("job_location","India"))}</div>
                    </div>
                    """, unsafe_allow_html=True)

            roadmap = ct.get("roadmap", [])
            if roadmap:
                st.markdown('<div class="card-title" style="margin-top:1rem"><span class="icon icon-purple">🗺️</span> Roadmap</div>', unsafe_allow_html=True)
                for step in roadmap:
                    text     = step.get("step", str(step))    if isinstance(step, dict) else str(step)
                    timeline = step.get("timeline", "")        if isinstance(step, dict) else ""
                    outcome  = step.get("outcome", "")         if isinstance(step, dict) else ""
                    st.markdown(f"""
                    <div class='traj-card'>
                      <div class='traj-role'>📍 {text}</div>
                      <div class='traj-note'>{timeline}{' · ' + outcome if outcome else ''}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        with tab4:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            report = res.get("full_report", "Report unavailable.")
            st.markdown(f"<div class='report-body'>{report}</div>", unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Report",
                data=report,
                file_name=f"skillbridge_{role.replace(' ','_')}.txt",
                mime="text/plain"
            )
            st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE 2: JOB SEARCH FROM RESUME
# ═══════════════════════════════════════════════════════════════════════════════

elif current_mode == "Jobs":
    st.markdown('<div class="section-heading">💼 AI Job Search Agent</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);font-size:0.82rem;'>Upload your resume → AI matches roles → click real job platform links to apply instantly.</p>", unsafe_allow_html=True)

    user_skills, _, experience, education = render_input_panel(show_role=False, role_key="jobs_input")
    if not user_skills and st.session_state.parsed_skills:
        user_skills = normalize_skills(st.session_state.parsed_skills)

    j1, j2, j3 = st.columns([1, 1, 2])
    with j1:
        location = st.text_input("Location Preference", value="India", placeholder="India / Remote / Bangalore")
        st.session_state.job_location = location
    with j2:
        exp_pref = st.selectbox("Experience Level", ["Any", "Fresher (0-1 yr)", "Junior (1-3 yr)", "Mid (3-5 yr)", "Senior (5+ yr)"])

    search_btn = st.button("🤖 Run AI Job Search Agent", use_container_width=False, type="primary")

    st.markdown("""
    <div style='padding:14px 16px;background:rgba(99,179,237,0.04);border:1px solid rgba(99,179,237,0.15);
      border-radius:10px;margin:12px 0;'>
      <div style='font-size:0.72rem;color:var(--accent-cyan);font-weight:700;text-transform:uppercase;
        letter-spacing:0.06em;margin-bottom:8px;'>⚡ Browse Jobs Instantly on All Platforms</div>
    """, unsafe_allow_html=True)

    if user_skills:
        skills_as_role = " ".join(user_skills[:3])
        st.markdown(f"<div style='font-size:0.75rem;color:var(--text-muted);margin-bottom:8px;'>Based on your skills: <b style='color:var(--text-secondary);'>{skills_as_role}</b></div>", unsafe_allow_html=True)
        st.markdown(render_job_platform_buttons(skills_as_role, location), unsafe_allow_html=True)
    else:
        st.markdown(render_job_platform_buttons("software engineer", location), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if search_btn:
        resume_text = st.session_state.resume_text
        if not resume_text and user_skills:
            resume_text = "Skills: " + ", ".join(user_skills)
        if not resume_text:
            st.warning("Please upload a resume or enter skills first.")
        else:
            with st.spinner("🧠 AI Job Search Agent working..."):
                st.session_state.job_result = search_jobs_from_resume(
                    resume_text=resume_text,
                    location=location,
                    experience=exp_pref
                )

    jr = st.session_state.job_result
    if jr:
        profile = jr.get("candidate_profile", {})
        if profile:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon icon-cyan">👤</span> Your Candidate Profile</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class='stats-row'>
              <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;color:var(--accent-cyan)'>{profile.get('experience_level','—')}</span><span class='stat-label'>Level</span></div>
              <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;'>{profile.get('primary_domain','—')}</span><span class='stat-label'>Domain</span></div>
              <div class='stat-chip'><span class='stat-value' style='font-size:0.85rem;color:var(--accent-green)'>{profile.get('market_value','—')}</span><span class='stat-label'>Market Value</span></div>
            </div>
            """, unsafe_allow_html=True)
            strengths = profile.get("strengths", [])
            if strengths:
                st.markdown("<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-matched'>💪 {s}</span>" for s in strengths) + "</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        jobs = jr.get("job_recommendations", [])
        if jobs:
            st.markdown('<div class="section-heading">🎯 AI-Matched Job Recommendations</div>', unsafe_allow_html=True)
            for i, job in enumerate(jobs):
                render_job_card_with_real_links(job, i + 1, location)

        strategy = jr.get("job_search_strategy", {})
        if strategy:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon icon-orange">⚡</span> AI Job Search Strategy</div>', unsafe_allow_html=True)
            for key, label in [("immediate_apply","🚀 Apply Now"), ("upskill_first","📚 After Upskilling"),
                                ("networking_tip","🤝 Networking"), ("resume_tip","📄 Resume Tip")]:
                if strategy.get(key):
                    st.markdown(f"<div style='padding:8px 12px;background:rgba(99,179,237,0.04);border-left:2px solid var(--accent-cyan);border-radius:0 6px 6px 0;margin-bottom:8px;font-size:0.82rem;'><b style='color:var(--accent-cyan);'>{label}:</b> <span style='color:var(--text-secondary);'>{strategy[key]}</span></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="icon icon-purple">🌐</span> All Job Platforms — Direct Links</div>', unsafe_allow_html=True)

        domain = profile.get("primary_domain", "software engineer") if profile else "software engineer"
        for pl_name, pl_cfg in JOB_PLATFORMS.items():
            url   = build_job_url(pl_name, domain, location)
            color = pl_cfg.get("color", "#555")
            icon  = pl_cfg.get("icon", "🔗")
            badge = pl_cfg.get("badge", pl_name)
            reason_map = {
                "LinkedIn":    "Best for referrals & networking. Premium jobs visible.",
                "Naukri":      "India's largest job board. Huge volume of listings.",
                "Indeed":      "Aggregates listings from multiple Indian job boards.",
                "Internshala": "Top for freshers, internships & entry-level roles.",
                "Glassdoor":   "Company reviews + salary insights alongside listings.",
                "Shine":       "Strong in IT/tech roles across India.",
                "Instahyre":   "AI-matched jobs. Popular with funded startups.",
                "AngelList":   "Startup jobs with equity. Great for early-stage roles.",
                "Cutshort":    "Skills-based matching. High signal-to-noise ratio.",
                "Foundit":     "Formerly Monster India. Good for mid-senior roles.",
            }
            reason = reason_map.get(pl_name, "")
            st.markdown(f"""
            <div class='traj-card'>
              <div class='traj-role' style='display:flex;align-items:center;gap:10px;'>
                <a href='{url}' target='_blank' style='
                  text-decoration:none;padding:5px 14px;
                  background:{color}18;border:1px solid {color}55;
                  border-radius:20px;font-size:0.72rem;font-weight:800;
                  color:{color};letter-spacing:0.04em;white-space:nowrap;
                '>{icon} {badge} ↗</a>
                <span style='font-size:0.78rem;color:var(--text-secondary);'>{reason}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        platforms_list = jr.get("top_platforms", [])
        if platforms_list:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown('<div class="card-title"><span class="icon icon-cyan">🌟</span> AI-Picked Best Platforms for Your Profile</div>', unsafe_allow_html=True)
            for pl in platforms_list:
                pl_name  = pl.get("name", "")
                pl_url   = pl.get("url", "#")
                pl_reason= pl.get("reason", "")
                if pl_name in JOB_PLATFORMS:
                    pl_url = build_job_url(pl_name, domain, location)
                st.markdown(f"""
                <div class='traj-card'>
                  <div class='traj-role'><a href='{pl_url}' target='_blank' style='color:var(--accent-cyan);text-decoration:none;'>🔗 {pl_name} ↗</a></div>
                  <div class='traj-note'>{pl_reason}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE 3: COMPARE ROLES
# ═══════════════════════════════════════════════════════════════════════════════

elif current_mode == "Compare":
    st.markdown('<div class="section-heading">⚖️ Compare Two Roles Side by Side</div>', unsafe_allow_html=True)

    all_roles = get_all_roles()
    cmp1, cmp2 = st.columns(2, gap="large")
    with cmp1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="icon icon-blue">🅰</span> Role A</div>', unsafe_allow_html=True)
        role_a = st.selectbox("Select Role A", all_roles, key="role_a")
        st.markdown('</div>', unsafe_allow_html=True)
    with cmp2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="icon icon-purple">🅱</span> Role B</div>', unsafe_allow_html=True)
        role_b = st.selectbox("Select Role B", all_roles, key="role_b", index=1)
        st.markdown('</div>', unsafe_allow_html=True)

    skills_cmp = st.text_area(
        "Your Skills",
        value=st.session_state.parsed_skills,
        placeholder="Python, SQL, TensorFlow...", height=70
    )

    if skills_cmp.strip() and role_a and role_b:
        user_skills_cmp = normalize_skills(skills_cmp)
        data_a = JOB_SKILL_DATABASE.get(role_a, {})
        data_b = JOB_SKILL_DATABASE.get(role_b, {})
        req_a  = data_a.get("required_skills", [])
        req_b  = data_b.get("required_skills", [])
        matched_a, missing_a = calculate_match_score(user_skills_cmp, req_a)
        matched_b, missing_b = calculate_match_score(user_skills_cmp, req_b)
        pct_a = round(len(matched_a) / len(req_a) * 100) if req_a else 0
        pct_b = round(len(matched_b) / len(req_b) * 100) if req_b else 0

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📊 Match Score Comparison</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class='compare-bar-wrap'>
          <div class='compare-bar-label'>
            <span style='color:var(--accent-cyan)'>🅰 {role_a}</span>
            <span style='color:var(--accent-cyan)'>{pct_a}%</span>
          </div>
          <div class='compare-bar-track'><div class='compare-bar-fill-a' style='width:{pct_a}%'></div></div>
        </div>
        <div class='compare-bar-wrap' style='margin-top:12px;'>
          <div class='compare-bar-label'>
            <span style='color:var(--accent-purple)'>🅱 {role_b}</span>
            <span style='color:var(--accent-purple)'>{pct_b}%</span>
          </div>
          <div class='compare-bar-track'><div class='compare-bar-fill-b' style='width:{pct_b}%'></div></div>
        </div>
        """, unsafe_allow_html=True)
        winner     = role_a if pct_a >= pct_b else role_b
        winner_pct = max(pct_a, pct_b)
        st.markdown(f"""
        <div style='margin-top:1.2rem;padding:1rem;background:rgba(104,211,145,0.06);border:1px solid rgba(104,211,145,0.2);
          border-radius:var(--radius-md);text-align:center;'>
          <span style='font-size:1.2rem;'>🏆</span>
          <span style='font-family:var(--font-display);font-weight:700;margin-left:8px;color:var(--accent-green);'>
            Better fit: {winner} ({winner_pct}%)
          </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.68rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>Apply for {winner}:</div>", unsafe_allow_html=True)
        st.markdown(render_job_platform_buttons(winner, "India"), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        pr1, pr2 = st.columns(2, gap="large")
        with pr1:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            render_role_preview(role_a, matched_a)
            st.markdown("---")
            st.markdown("<div style='font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;'>Missing</div>", unsafe_allow_html=True)
            st.markdown("<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-missing'>✗ {s}</span>" for s in missing_a) + "</div>", unsafe_allow_html=True)
            if missing_a:
                st.markdown("<div style='margin-top:8px;font-size:0.68rem;color:var(--text-muted);margin-bottom:4px;'>Learn these skills:</div>", unsafe_allow_html=True)
                for ms in missing_a[:3]:
                    st.markdown(f"<div style='margin-bottom:4px;font-size:0.72rem;'><b>{ms}:</b> " + render_course_platform_buttons(ms) + "</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with pr2:
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            render_role_preview(role_b, matched_b)
            st.markdown("---")
            st.markdown("<div style='font-size:0.75rem;color:var(--text-muted);margin-bottom:4px;'>Missing</div>", unsafe_allow_html=True)
            st.markdown("<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-missing'>✗ {s}</span>" for s in missing_b) + "</div>", unsafe_allow_html=True)
            if missing_b:
                st.markdown("<div style='margin-top:8px;font-size:0.68rem;color:var(--text-muted);margin-bottom:4px;'>Learn these skills:</div>", unsafe_allow_html=True)
                for ms in missing_b[:3]:
                    st.markdown(f"<div style='margin-bottom:4px;font-size:0.72rem;'><b>{ms}:</b> " + render_course_platform_buttons(ms) + "</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Enter your skills above to see the comparison.")


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE 4: CAREER MAP
# ═══════════════════════════════════════════════════════════════════════════════

elif current_mode == "Career Map":
    st.markdown('<div class="section-heading">🗺️ Your Career Score Across All 35+ Roles</div>', unsafe_allow_html=True)

    skills_map = st.text_area(
        "Your Skills",
        value=st.session_state.parsed_skills,
        placeholder="Python, SQL, Docker...", height=70
    )

    if skills_map.strip():
        user_skills_map = normalize_skills(skills_map)
        role_scores = {}
        for role, data in JOB_SKILL_DATABASE.items():
            req = data.get("required_skills", [])
            if req:
                matched_count = sum(1 for s in req if s.lower() in [x.lower() for x in user_skills_map])
                role_scores[role] = round(matched_count / len(req) * 100)

        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1], reverse=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">🏆 Fit Ranking — All Roles</div>', unsafe_allow_html=True)
        for i, (role, score) in enumerate(sorted_roles):
            meta      = ROLE_META.get(role, {"icon": "💼"})
            bar_color = "#68d391" if score >= 70 else "#f6ad55" if score >= 40 else "#fc8181"
            medal     = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"#{i+1}"
            meta_row  = ROLE_META.get(role, {})
            growth    = meta_row.get("growth", "")
            salary    = meta_row.get("salary", "")
            ln_url    = build_job_url("LinkedIn", role, "India")
            naukri_url= build_job_url("Naukri", role, "India")
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid var(--border);'>
              <span style='font-size:1rem;width:28px;text-align:center;'>{medal}</span>
              <span style='font-size:1.1rem'>{meta['icon']}</span>
              <span style='flex:1;font-weight:600;font-size:0.85rem;'>{role}</span>
              <span style='font-size:0.72rem;color:var(--accent-green);white-space:nowrap;'>{growth}</span>
              <span style='font-size:0.72rem;color:var(--text-muted);white-space:nowrap;min-width:80px;text-align:right;'>{salary}</span>
              <a href="{ln_url}" target="_blank" style='font-size:0.62rem;padding:2px 7px;background:#0a66c222;border:1px solid #0a66c255;border-radius:10px;color:#0a66c2;text-decoration:none;font-weight:700;white-space:nowrap;'>LI ↗</a>
              <a href="{naukri_url}" target="_blank" style='font-size:0.62rem;padding:2px 7px;background:#ff755522;border:1px solid #ff755555;border-radius:10px;color:#ff7555;text-decoration:none;font-weight:700;white-space:nowrap;'>Naukri ↗</a>
              <div style='width:120px;'>
                <div style='height:5px;background:rgba(255,255,255,0.06);border-radius:100px;overflow:hidden;'>
                  <div style='height:100%;width:{score}%;background:{bar_color};border-radius:100px;'></div>
                </div>
              </div>
              <span style='font-family:var(--font-mono);font-size:0.78rem;color:{bar_color};width:36px;text-align:right;'>{score}%</span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if sorted_roles:
            top_role = sorted_roles[0][0]
            st.markdown(f'<div class="section-heading">🎯 Best Match: {top_role}</div>', unsafe_allow_html=True)
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            render_role_preview(top_role, user_skills_map)
            st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
            st.markdown(f"<div style='font-size:0.68rem;color:var(--text-muted);font-weight:600;text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;'>Apply for {top_role}:</div>", unsafe_allow_html=True)
            st.markdown(render_job_platform_buttons(top_role, "India"), unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Enter your skills to generate your career map.")


# ═══════════════════════════════════════════════════════════════════════════════
#  MODE 5: MARKET INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════════════════

elif current_mode == "Market":
    st.markdown('<div class="section-heading">📡 AI Market Intelligence Agent</div>', unsafe_allow_html=True)
    st.markdown("<p style='color:var(--text-muted);font-size:0.82rem;'>Real-time market insights, salary bands, trending skills, top hiring companies with live job links.</p>", unsafe_allow_html=True)

    m1, m2, m3 = st.columns([2, 1, 1])
    with m1:
        market_role = st.selectbox("Select Role", get_all_roles(), key="market_role")
    with m2:
        market_loc  = st.text_input("Location", value="India")
    with m3:
        st.markdown("<div style='padding-top:1.8rem;'>", unsafe_allow_html=True)
        market_btn  = st.button("📡 Fetch Market Intel", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    if market_btn and market_role:
        with st.spinner(f"🤖 AI agent fetching market data for {market_role}..."):
            st.session_state.market_result = get_market_intelligence(market_role, market_loc)

    mr = st.session_state.market_result
    if mr:
        if mr.get("market_summary"):
            st.markdown(f"<div style='padding:1rem;background:rgba(99,179,237,0.05);border-left:3px solid var(--accent-cyan);border-radius:0 var(--radius-md) var(--radius-md) 0;margin-bottom:1rem;font-size:0.88rem;color:var(--text-secondary);'>{mr['market_summary']}</div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap="large")

        with col1:
            sal = mr.get("salary_bands", {})
            if sal:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="icon icon-orange">💰</span> Salary Bands</div>', unsafe_allow_html=True)
                for level, label in [("junior","Junior (0-2 yr)"),("mid","Mid (2-5 yr)"),("senior","Senior (5+ yr)"),("lead","Lead (8+ yr)")]:
                    if sal.get(level):
                        color = {"junior":"var(--text-secondary)","mid":"var(--accent-cyan)","senior":"var(--accent-green)","lead":"var(--accent-orange)"}.get(level)
                        st.markdown(f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border);font-size:0.82rem;'><span style='color:var(--text-muted);'>{label}</span><span style='color:{color};font-weight:700;font-family:var(--font-mono);'>{sal[level]}</span></div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            trending = mr.get("trending_skills", [])
            if trending:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="icon icon-green">📈</span> Trending Skills — Learn Now</div>', unsafe_allow_html=True)
                for ts in trending:
                    ts_udemy = build_course_url("Udemy", ts)
                    ts_yt    = build_course_url("YouTube", ts, free=True)
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:8px;padding:5px 0;border-bottom:1px solid var(--border);'>
                      <span style='font-size:0.78rem;color:var(--accent-green);font-weight:600;flex:1;'>↑ {ts}</span>
                      <a href="{ts_udemy}" target="_blank" class='real-link-badge' style='background:#a435f022;border:1px solid #a435f055;color:#a435f0;font-size:0.6rem;padding:2px 7px;'>Udemy</a>
                      <a href="{ts_yt}" target="_blank" class='real-link-badge' style='background:#ff000022;border:1px solid #ff000055;color:#ff4444;font-size:0.6rem;padding:2px 7px;'>YT Free</a>
                    </div>
                    """, unsafe_allow_html=True)

                declining = mr.get("declining_skills", [])
                if declining:
                    st.markdown("<div style='margin-top:0.8rem;font-size:0.75rem;color:var(--text-muted);'>Declining:</div>", unsafe_allow_html=True)
                    st.markdown("<div class='skill-tags'>" + "".join(f"<span class='skill-tag tag-missing'>↓ {s}</span>" for s in declining) + "</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            companies = mr.get("hiring_companies", [])
            if companies:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="icon icon-blue">🏢</span> Top Hiring Companies</div>', unsafe_allow_html=True)
                for co in companies:
                    intensity = co.get("hiring_intensity","Medium")
                    i_color   = {"High":"var(--accent-green)","Medium":"var(--accent-cyan)","Low":"var(--accent-orange)"}.get(intensity,"var(--text-muted)")
                    co_name   = co.get("name","")
                    co_ln_url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(market_role)}&f_C={urllib.parse.quote(co_name)}"
                    co_naukri = f"https://www.naukri.com/{market_role.lower().replace(' ','-')}-jobs-in-{co_name.lower().replace(' ','-')}"
                    st.markdown(f"""
                    <div style='padding:8px 0;border-bottom:1px solid var(--border);'>
                      <div style='display:flex;justify-content:space-between;align-items:center;font-size:0.82rem;margin-bottom:4px;'>
                        <span style='font-weight:600;'>{co_name}</span>
                        <span style='font-size:0.72rem;'>
                          <span style='color:var(--text-muted);'>{co.get('type','')}</span> ·
                          <span style='color:{i_color};'>{intensity}</span>
                        </span>
                      </div>
                      <div style='display:flex;gap:6px;'>
                        <a href="{co_ln_url}" target="_blank" class='real-link-badge' style='background:#0a66c222;border:1px solid #0a66c255;color:#0a66c2;font-size:0.6rem;padding:2px 8px;'>LinkedIn ↗</a>
                        <a href="{co_naukri}" target="_blank" class='real-link-badge' style='background:#ff755522;border:1px solid #ff755555;color:#ff7555;font-size:0.6rem;padding:2px 8px;'>Naukri ↗</a>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            topics = mr.get("interview_topics", [])
            if topics:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown('<div class="card-title"><span class="icon icon-purple">🎯</span> Common Interview Topics</div>', unsafe_allow_html=True)
                for i, t in enumerate(topics, 1):
                    t_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(t + ' interview questions')}"
                    st.markdown(f"""
                    <div style='display:flex;align-items:center;gap:8px;font-size:0.82rem;padding:6px 0;border-bottom:1px solid var(--border);color:var(--text-secondary);'>
                      <span style='color:var(--accent-purple);font-weight:700;'>{i}.</span>
                      <span style='flex:1;'>{t}</span>
                      <a href="{t_url}" target="_blank" class='real-link-badge' style='background:#ff000022;border:1px solid #ff000055;color:#ff4444;font-size:0.6rem;padding:2px 7px;'>Prep YT ↗</a>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # ── Live Job Board Links ──────────────────────────────────────────────
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="icon icon-cyan">🌐</span> Apply Now — All Job Platforms</div>', unsafe_allow_html=True)
        st.markdown(render_job_platform_buttons(market_role, market_loc), unsafe_allow_html=True)

        jbs = mr.get("job_boards", [])
        if jbs:
            st.markdown("<div style='margin-top:10px;'>", unsafe_allow_html=True)
            for jb in jbs:
                pl_name  = jb.get("platform","")
                real_url = build_job_url(pl_name, market_role, market_loc) if pl_name in JOB_PLATFORMS else jb.get("url","#")
                tip      = jb.get("search_tip","")
                st.markdown(f"<div style='font-size:0.75rem;color:var(--text-muted);padding:4px 0;'><a href='{real_url}' target='_blank' style='color:var(--accent-cyan);text-decoration:none;font-weight:600;'>↗ {pl_name}</a> · {tip}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if mr.get("market_outlook"):
            st.markdown(f"<div style='padding:1rem;background:rgba(104,211,145,0.05);border:1px solid rgba(104,211,145,0.15);border-radius:var(--radius-md);font-size:0.85rem;color:var(--text-secondary);'><b style='color:var(--accent-green);'>📊 6-12 Month Outlook:</b> {mr['market_outlook']}</div>", unsafe_allow_html=True)


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧠 SkillBridge AI Pro")
    st.markdown(f"""
    <div style='padding:0.8rem;background:rgba(255,255,255,0.03);border:1px solid var(--border);border-radius:12px;'>
      <div style='font-size:0.72rem;color:var(--text-muted);margin-bottom:4px;'>Active Mode</div>
      <div style='font-family:var(--font-display);font-weight:700;color:var(--accent-cyan);'>{current_mode}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🔗 Quick Links")
    quick_links = [
        ("LinkedIn Jobs", "https://www.linkedin.com/jobs/", "#0a66c2"),
        ("Naukri", "https://www.naukri.com/", "#ff7555"),
        ("Indeed India", "https://in.indeed.com/", "#003A9B"),
        ("Internshala", "https://internshala.com/jobs/", "#006bff"),
        ("Udemy", "https://www.udemy.com/", "#a435f0"),
        ("Coursera", "https://www.coursera.org/", "#0056d2"),
        ("YouTube Learn", "https://www.youtube.com/", "#ff0000"),
    ]
    for name, url, color in quick_links:
        st.markdown(f"<a href='{url}' target='_blank' style='display:block;padding:5px 8px;margin-bottom:4px;border-radius:8px;background:rgba(255,255,255,0.03);border:1px solid {color}33;color:{color};font-size:0.75rem;font-weight:600;text-decoration:none;'>↗ {name}</a>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚙️ About")
    st.markdown("""
**SkillBridge AI Pro** is powered by **Groq LLaMA-3.3-70b**.

**Real Links:**
- 🎓 Udemy, Coursera, Internshala, edX, YouTube, NPTEL, LinkedIn Learning
- 💼 LinkedIn, Naukri, Indeed, Glassdoor, Internshala, Shine, Instahyre, AngelList, Cutshort, Foundit

**Modes:**
- 🔍 **Analyze** — Gap analysis + real course links
- 💼 **Job Search** — Resume → live job links
- ⚖️ **Compare** — Role A vs B + apply links
- 🗺️ **Career Map** — All-role ranking + quick apply
- 📡 **Market Intel** — Salary, trends & live roles
""")

    if st.session_state.history:
        st.markdown("---")
        st.markdown("### 🕑 History")
        for h in reversed(st.session_state.history[-5:]):
            color = "#68d391" if h["score"] >= 70 else "#f6ad55" if h["score"] >= 40 else "#fc8181"
            ln_url = build_job_url("LinkedIn", h["role"], "India")
            st.markdown(f"<div style='font-size:0.75rem;padding:5px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;'><span><span style='color:{color};font-weight:700;'>{h['score']}%</span> · {h['role']}</span><a href='{ln_url}' target='_blank' style='color:#0a66c2;font-size:0.65rem;text-decoration:none;'>Apply ↗</a></div>", unsafe_allow_html=True)

    st.markdown("---")
    model_used = "llama-3.3-70b-versatile"
    st.markdown(f"<div style='font-size:0.68rem;color:var(--text-muted);'>Model: {model_used}</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.68rem;color:var(--text-muted);'>35+ roles · 10 job platforms · 9 course platforms</div>", unsafe_allow_html=True)