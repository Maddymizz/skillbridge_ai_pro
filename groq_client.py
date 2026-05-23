"""
groq_client.py — All Groq LLaMA API calls for SkillBridge AI Pro
Features: Resume parser, Skill analysis, Career trajectory, Course agent,
          Job search from resume, Market intelligence
"""

import json
import requests
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_FAST   = "llama-3.1-8b-instant"     # Speed tasks
MODEL_SMART  = "llama-3.3-70b-versatile"  # Deep analysis


def _call_groq(prompt: str, system: str, max_tokens: int = 2000,
               model: str = None, temperature: float = 0.4) -> str:
    if not GROQ_API_KEY:
        return "ERROR: GROQ_API_KEY not found in .env file"

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type":  "application/json"
    }
    payload = {
        "model":    model or MODEL_SMART,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user",   "content": prompt}
        ],
        "max_tokens":  max_tokens,
        "temperature": temperature
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError:
        return f"ERROR: HTTP {resp.status_code} - {resp.text}"
    except Exception as e:
        return f"ERROR: {str(e)}"


def _parse_json_response(raw: str, fallback: dict) -> dict:
    """Safely parse JSON from LLM response, stripping markdown fences."""
    try:
        clean = raw.strip()
        # Strip markdown fences
        for fence in ["```json", "```JSON", "```"]:
            clean = clean.replace(fence, "")
        clean = clean.strip()
        # Find first { or [
        start = min(
            (clean.find("{") if clean.find("{") != -1 else len(clean)),
            (clean.find("[") if clean.find("[") != -1 else len(clean))
        )
        clean = clean[start:]
        return json.loads(clean)
    except Exception:
        return fallback


# ═══════════════════════════════════════════════════════════════════════════════
#  🌟 AI Resume Parser
# ═══════════════════════════════════════════════════════════════════════════════

def parse_resume_with_groq(resume_text: str) -> Dict:
    """
    Fully parses a resume using AI. Returns:
    - skills: comma-separated string
    - profile: name, title, experience_years, education, summary
    - suggested_roles: list of job roles
    """
    system = (
        "You are an expert technical recruiter and resume parser. "
        "Respond ONLY in valid JSON. No markdown, no explanation outside JSON."
    )

    prompt = f"""
Parse this resume and extract all information.

Resume text:
\"\"\"
{resume_text[:4000]}
\"\"\"

Return JSON with EXACTLY these keys:
{{
  "skills": "Skill1, Skill2, Skill3",
  "name": "<candidate name or 'Not found'>",
  "title": "<current/target job title>",
  "experience_years": "<e.g. 3 years or Fresher>",
  "education": "<highest degree + field>",
  "summary": "<2 sentence professional summary>",
  "suggested_roles": ["<role1>", "<role2>", "<role3>"]
}}

For skills: include ALL technical and professional skills (programming languages, frameworks,
tools, platforms, databases, methodologies, certifications).
Be specific (e.g. "React.js" not just "JavaScript frameworks").
For suggested_roles: suggest 3 best-fit job roles from the resume content.
"""

    raw = _call_groq(prompt, system, max_tokens=800, model=MODEL_FAST)
    if raw.startswith("ERROR"):
        return {"skills": "", "name": "", "title": "", "experience_years": "",
                "education": "", "summary": "", "suggested_roles": []}

    return _parse_json_response(raw, {
        "skills": raw.strip(), "name": "", "title": "", "experience_years": "",
        "education": "", "summary": "", "suggested_roles": []
    })


# ═══════════════════════════════════════════════════════════════════════════════
#  🤖 AI Job Search Agent — Find jobs from resume
# ═══════════════════════════════════════════════════════════════════════════════

def search_jobs_from_resume(resume_text: str, location: str = "India",
                             experience: str = "Any") -> Dict:
    """
    AI agent that analyzes a resume and returns curated job recommendations
    with real job search query suggestions, salary expectations, and fit scores.
    """
    system = (
        "You are an elite AI job search agent with deep knowledge of the global job market. "
        "Respond ONLY in valid JSON. No markdown, no explanation outside JSON."
    )

    prompt = f"""
You are a job search AI agent. Analyze this resume and generate targeted job recommendations.

Resume text:
\"\"\"
{resume_text[:3000]}
\"\"\"

Candidate preferences:
- Location: {location}
- Experience level: {experience}

Return a JSON object with EXACTLY these keys:
{{
  "candidate_profile": {{
    "strengths": ["<strength1>", "<strength2>", "<strength3>"],
    "experience_level": "<Junior/Mid/Senior/Lead>",
    "primary_domain": "<e.g. AI/ML, Full Stack, Data>",
    "market_value": "<salary range e.g. ₹8-15 LPA>"
  }},
  "job_recommendations": [
    {{
      "title": "<exact job title>",
      "company_types": ["<startup>", "<MNC>", "<product company>"],
      "fit_score": <integer 0-100>,
      "why_fit": "<one sentence>",
      "search_query": "<exact LinkedIn/Naukri search query>",
      "platforms": ["LinkedIn", "Naukri", "AngelList"],
      "salary_range": "<₹X–Y LPA>",
      "skills_to_highlight": ["<skill1>", "<skill2>", "<skill3>"]
    }}
  ],
  "job_search_strategy": {{
    "immediate_apply": "<1-2 sentence strategy for roles to apply to now>",
    "upskill_first": "<1-2 sentence strategy for roles after upskilling>",
    "networking_tip": "<actionable tip for this specific profile>",
    "resume_tip": "<one specific improvement for this resume>"
  }},
  "top_platforms": [
    {{"name": "<platform>", "reason": "<why this platform suits this profile>", "url": "<base URL>"}}
  ]
}}

Include exactly 5 job recommendations sorted by fit_score descending.
"""

    raw = _call_groq(prompt, system, max_tokens=2000, model=MODEL_SMART)
    if raw.startswith("ERROR"):
        return {}
    return _parse_json_response(raw, {})


# ═══════════════════════════════════════════════════════════════════════════════
#  📚 AI Course Agent — Fetch real course recommendations
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_courses_with_ai_agent(
    missing_skills: List[str],
    target_role: str,
    experience_level: str = "Mid",
    learning_style: str = "Video + Hands-on"
) -> Dict:
    """
    AI agent that acts like a course counselor — returns curated,
    real course recommendations for each missing skill with platform details,
    duration, difficulty, and a personalized learning roadmap.
    """
    system = (
        "You are an expert AI learning path advisor with knowledge of all major online learning platforms "
        "(Coursera, Udemy, edX, YouTube, freeCodeCamp, fast.ai, DeepLearning.ai, Pluralsight, LinkedIn Learning, etc.). "
        "Respond ONLY in valid JSON. No markdown, no explanation outside JSON."
    )

    prompt = f"""
You are an AI course recommendation agent. Generate a complete learning plan.

Target Role: {target_role}
Experience Level: {experience_level}
Missing Skills: {json.dumps(missing_skills)}
Learning Style: {learning_style}

Return JSON with EXACTLY these keys:
{{
  "learning_roadmap": {{
    "total_duration": "<e.g. 3-4 months>",
    "weekly_hours": "<e.g. 10-15 hours/week>",
    "priority_order": ["<skill1>", "<skill2>", ...],
    "milestone_1": "<what to achieve in month 1>",
    "milestone_2": "<what to achieve by month 2-3>",
    "milestone_3": "<what to achieve by month 4+>"
  }},
  "courses": [
    {{
      "skill": "<skill name>",
      "priority": "<High|Medium|Low>",
      "courses": [
        {{
          "title": "<exact course title>",
          "platform": "<platform name>",
          "instructor": "<instructor name>",
          "duration": "<e.g. 20 hours>",
          "difficulty": "<Beginner|Intermediate|Advanced>",
          "price": "<Free|₹X|$X>",
          "rating": "<e.g. 4.7/5>",
          "url_hint": "<search this on the platform>",
          "why_recommended": "<one sentence>"
        }}
      ],
      "free_resource": {{
        "title": "<free alternative>",
        "platform": "YouTube/freeCodeCamp/etc",
        "url_hint": "<search query>"
      }},
      "practice_project": "<hands-on project idea to solidify this skill>"
    }}
  ],
  "certification_path": [
    {{
      "certification": "<cert name>",
      "provider": "<e.g. Google, AWS, Meta>",
      "relevance": "<why this cert matters for the target role>",
      "estimated_prep": "<time to prepare>"
    }}
  ],
  "quick_wins": [
    "<actionable task completable in 1-2 days to start momentum>"
  ]
}}

Provide courses for ALL {len(missing_skills)} missing skills. 
Include 2 course options per skill (1 premium + 1 budget/free).
Certifications should be role-specific and from reputable providers.
Include 3 quick wins.
"""

    raw = _call_groq(prompt, system, max_tokens=3000, model=MODEL_SMART, temperature=0.3)
    if raw.startswith("ERROR"):
        return {}
    return _parse_json_response(raw, {})


# ═══════════════════════════════════════════════════════════════════════════════
#  🔍 Main Skill Gap Analysis
# ═══════════════════════════════════════════════════════════════════════════════

def analyze_skills_with_groq(
    user_skills:    List[str],
    target_role:    str,
    matched_skills: List[str],
    missing_skills: List[str],
    experience:     str,
    education:      str,
    all_roles:      List[str],
    job_db:         Dict
) -> Dict:
    """
    Runs parallel Groq calls:
    1. Skill insights + learning path (JSON)
    2. Career trajectory predictor (JSON)
    3. Full written career report
    Returns combined result dict.
    """
    result = {}

    # ── Call 1: Skill Insights + Learning Path ────────────────────────────────
    system1 = (
        "You are an expert career coach and technical recruiter. "
        "Respond ONLY in valid JSON. No markdown, no explanation outside JSON."
    )
    prompt1 = f"""
Analyze this job seeker's profile:

Target Role: {target_role}
Experience: {experience}
Education: {education}
User Skills: {json.dumps(user_skills)}
Matched Skills: {json.dumps(matched_skills)}
Missing Skills: {json.dumps(missing_skills)}

Return a JSON object with these EXACT keys:
{{
  "skill_insights": "<2-3 sentence analysis of the candidate's readiness>",
  "readiness_verdict": "<Ready to Apply|Almost There|Needs 3-6 months|Major Gap>",
  "top_strength": "<the candidate's single biggest strength>",
  "critical_gap": "<the single most important skill to learn first>",
  "learning_path": [
    {{
      "skill": "<skill name>",
      "resource": "<specific course, book, or platform>",
      "priority": "<High | Medium | Low>",
      "duration": "<estimated time e.g. 2 weeks>",
      "why": "<one sentence why this skill matters for the role>"
    }}
  ]
}}
"""
    raw1 = _call_groq(prompt1, system1, max_tokens=1800)
    data1 = _parse_json_response(raw1, {
        "skill_insights": raw1.replace("ERROR:", "⚠️"),
        "readiness_verdict": "Analysis unavailable",
        "top_strength": "",
        "critical_gap": "",
        "learning_path": []
    })
    result.update({
        "skill_insights":     data1.get("skill_insights", ""),
        "readiness_verdict":  data1.get("readiness_verdict", ""),
        "top_strength":       data1.get("top_strength", ""),
        "critical_gap":       data1.get("critical_gap", ""),
        "learning_path":      data1.get("learning_path", [])
    })

    # ── Call 2: Career Trajectory ─────────────────────────────────────────────
    system2 = "You are a career trajectory AI. Respond ONLY in valid JSON. No markdown."

    role_scores = {}
    for role, data in job_db.items():
        req = set(s.lower() for s in data.get("required_skills", []))
        usr = set(s.lower() for s in user_skills)
        if req:
            role_scores[role] = round(len(req & usr) / len(req) * 100)

    # Top 10 roles only to save tokens
    top_roles = dict(sorted(role_scores.items(), key=lambda x: x[1], reverse=True)[:10])

    prompt2 = f"""
Career profile:
User Skills: {json.dumps(user_skills)}
Experience: {experience}
Education: {education}
Target Role: {target_role}
Top Role Match Scores: {json.dumps(top_roles)}

Return JSON with these EXACT keys:
{{
  "immediate_roles": [
    {{"role": "<role name>", "reason": "<one sentence why>", "match_score": <integer>}}
  ],
  "roadmap": [
    {{"step": "<action step>", "timeline": "<e.g. 1-2 months>", "outcome": "<what this unlocks>"}}
  ],
  "predicted_score_in_6months": <integer 0-100>,
  "salary_trajectory": {{
    "current": "<current expected salary range>",
    "in_6_months": "<after upskilling>",
    "in_1_year": "<after 1 year of growth>"
  }}
}}
"""
    raw2 = _call_groq(prompt2, system2, max_tokens=1200)
    result["career_trajectory"] = _parse_json_response(raw2, {
        "immediate_roles": [], "roadmap": [],
        "predicted_score_in_6months": None,
        "salary_trajectory": {}
    })

    # ── Call 3: Full Report ───────────────────────────────────────────────────
    system3 = "You are a professional career counselor writing a structured report. Be specific and encouraging."
    prompt3 = f"""
Write a 350-word professional skill gap analysis report.

Target Role: {target_role}
Experience: {experience}
Education: {education}
Matched Skills: {', '.join(matched_skills) or 'None'}
Missing Skills: {', '.join(missing_skills) or 'None'}
Readiness: {result.get('readiness_verdict', '')}

Structure with these sections (use plain text, no markdown symbols):
EXECUTIVE SUMMARY
STRENGTHS & ADVANTAGES
SKILL GAPS TO BRIDGE
90-DAY ACTION PLAN
MOTIVATION & OUTLOOK

Be specific — mention actual skills and concrete steps.
"""
    raw3 = _call_groq(prompt3, system3, max_tokens=900)
    result["full_report"] = (
        raw3 if not raw3.startswith("ERROR")
        else "Report generation failed. Please check your API key."
    )

    return result


# ═══════════════════════════════════════════════════════════════════════════════
#  🌐 Market Intelligence Agent
# ═══════════════════════════════════════════════════════════════════════════════

def get_market_intelligence(role: str, location: str = "India") -> Dict:
    """AI agent that provides real-time market intelligence for a given role."""
    system = (
        "You are a tech job market intelligence AI with deep knowledge of hiring trends, "
        "salaries, and in-demand skills. Respond ONLY in valid JSON."
    )

    prompt = f"""
Provide comprehensive market intelligence for:
Role: {role}
Location: {location}

Return JSON with EXACTLY these keys:
{{
  "market_summary": "<2 sentence overview of demand>",
  "hiring_companies": [
    {{"name": "<company>", "type": "<startup|MNC|product>", "hiring_intensity": "<High|Medium|Low>"}}
  ],
  "trending_skills": ["<skill in high demand for this role>"],
  "declining_skills": ["<skill becoming less relevant>"],
  "interview_topics": ["<common interview topic/question area>"],
  "salary_bands": {{
    "junior": "<0-2 yrs range>",
    "mid": "<2-5 yrs range>",
    "senior": "<5+ yrs range>",
    "lead": "<8+ yrs range>"
  }},
  "job_boards": [
    {{"platform": "<name>", "search_tip": "<specific search tip for this role>", "url": "<URL>"}}
  ],
  "market_outlook": "<6-12 month outlook for this role>"
}}

hiring_companies: list 5 real companies known to hire for this role.
trending_skills: list 5-6 skills currently in high demand for this role.
interview_topics: list 5 common interview topics.
job_boards: list 4 platforms with specific search tips.
"""

    raw = _call_groq(prompt, system, max_tokens=1500, model=MODEL_FAST)
    if raw.startswith("ERROR"):
        return {}
    return _parse_json_response(raw, {})
