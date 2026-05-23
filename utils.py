"""
utils.py — Skill normalization, scoring, resume parsing helpers
"""

import re
from typing import List, Tuple, Dict


def normalize_skills(skills_text: str) -> List[str]:
    """Converts comma/newline/semicolon-separated skills string into a clean list."""
    raw = re.split(r"[,;\n\r•·\-]+", skills_text)
    cleaned = []
    for s in raw:
        s = s.strip()
        if s and len(s) > 1:
            cleaned.append(s)
    return cleaned


def calculate_match_score(
    user_skills: List[str],
    required_skills: List[str]
) -> Tuple[List[str], List[str]]:
    """Compares user skills against required skills (case-insensitive). Returns (matched, missing)."""
    user_lower = {s.lower().strip() for s in user_skills}
    matched, missing = [], []
    for req in required_skills:
        req_lower = req.lower().strip()
        found = (
            req_lower in user_lower
            or any(req_lower in u or u in req_lower for u in user_lower)
        )
        if found:
            matched.append(req)
        else:
            missing.append(req)
    return matched, missing


def get_skill_categories(skills: List[str]) -> Dict[str, List[str]]:
    """Rough categorization of skills into buckets."""
    categories = {
        "Languages":    [],
        "Frameworks":   [],
        "Cloud/DevOps": [],
        "Data/ML":      [],
        "AI/LLM":       [],
        "Soft Skills":  [],
        "Other":        [],
    }
    lang_kw   = {"python","java","javascript","typescript","kotlin","swift","go","rust","c++","c#","r","scala","sql","html","css","solidity","c"}
    fw_kw     = {"react","django","fastapi","flask","node","spring","vue","angular","express","rails","laravel","pytorch","tensorflow"}
    cloud_kw  = {"aws","azure","gcp","docker","kubernetes","terraform","ci/cd","linux","git","jenkins","ansible"}
    data_kw   = {"machine learning","deep learning","pandas","numpy","scikit","spark","mlops","airflow","etl","tableau","power bi","statistics"}
    ai_kw     = {"llm","langchain","llama","openai","groq","prompt","rag","vector","hugging face","embeddings","fine-tun","agent","langchain"}
    soft_kw   = {"agile","communication","leadership","problem solving","teamwork","stakeholder","product strategy","user research"}

    for skill in skills:
        s = skill.lower()
        if any(k in s for k in ai_kw):
            categories["AI/LLM"].append(skill)
        elif any(k in s for k in lang_kw):
            categories["Languages"].append(skill)
        elif any(k in s for k in fw_kw):
            categories["Frameworks"].append(skill)
        elif any(k in s for k in cloud_kw):
            categories["Cloud/DevOps"].append(skill)
        elif any(k in s for k in data_kw):
            categories["Data/ML"].append(skill)
        elif any(k in s for k in soft_kw):
            categories["Soft Skills"].append(skill)
        else:
            categories["Other"].append(skill)

    return {k: v for k, v in categories.items() if v}


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF bytes using pdfplumber."""
    import io
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception:
        pass
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    except Exception as e:
        return f"ERROR reading PDF: {e}"


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from DOCX bytes."""
    import io
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        return f"ERROR reading DOCX: {e}"


def get_match_level(score: int) -> Tuple[str, str, str]:
    if score >= 85:
        return "Strong Match", "#22C55E", "🏆"
    elif score >= 60:
        return "Good Match", "#3B82F6", "👍"
    elif score >= 40:
        return "Partial Match", "#F59E0B", "📈"
    else:
        return "Needs Work", "#EF4444", "🎯"
