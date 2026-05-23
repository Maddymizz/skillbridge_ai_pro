# 🧠 SkillBridge AI Pro

**AI-Powered Skill Gap Analysis Tool — Built with Groq LLaMA-3.3-70b**

> Merged from `skill_gap_tool` + `files(1)` with full AI upgrade

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 Resume Upload | PDF/DOCX → AI parser extracts skills, experience, education |
| 🔍 Skill Gap Analysis | Groq LLaMA analyzes missing skills with readiness verdict |
| 📚 AI Course Agent | Real course recommendations per skill (Coursera, Udemy, YouTube, etc.) |
| 💼 Job Search Agent | Resume → job matches with search queries & platform tips |
| 🗺️ Career Map | Match score against all 35+ roles |
| ⚖️ Role Compare | Side-by-side comparison of two roles |
| 📡 Market Intelligence | Salary bands, trending skills, hiring companies |
| 📊 Full Report | Downloadable 350-word career analysis |

---

## 🚀 Quick Setup (VS Code)

### 1. Get Groq API Key
```
https://console.groq.com  →  Create API Key (Free tier available)
```

### 2. Clone / Open in VS Code
```bash
cd skillbridge_ai
code .
```

### 3. Create virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Create .env file
```bash
cp .env.example .env
# Edit .env and paste your Groq API key:
# GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
```

### 6. Run the app
```bash
streamlit run app.py
```

App opens at: **http://localhost:8501**

---

## 📁 Project Structure

```
skillbridge_ai/
├── app.py              # Main Streamlit app (all 5 modes)
├── groq_client.py      # All Groq AI calls (5 agents)
├── job_database.py     # 35+ job roles with skills & market data
├── utils.py            # Skill matching, PDF/DOCX extraction
├── style.css           # Premium dark UI
├── requirements.txt
├── .env.example
└── .streamlit/
    └── config.toml
```

---

## 🤖 AI Models Used

| Model | Used For |
|-------|----------|
| `llama-3.3-70b-versatile` | Skill analysis, job search, course agent, market intel |
| `llama-3.1-8b-instant` | Resume parsing (fast), market data |

---

## 🔥 How Each Mode Works

### 🔍 Analyze Mode
1. Upload resume or type skills
2. AI parses resume → extracts skills + profile
3. Click "Run AI Analysis"
4. 3 parallel Groq calls:
   - Skill insights + learning path
   - Career trajectory + salary prediction
   - Full written report
5. Click "Fetch AI Courses" tab → AI course agent

### 💼 Job Search Mode
1. Upload resume
2. AI agent analyzes profile → finds best-matching roles
3. Returns: job titles, search queries, platforms, fit scores

### 📚 Course Agent
- Runs per missing skill
- Returns: premium course, free alternative, practice project
- Includes: certification path + quick wins

### 📡 Market Intelligence
- Role + location → AI fetches:
  - Salary bands by experience
  - Trending vs declining skills
  - Top hiring companies
  - Interview topics
  - Job board search tips

---

## 📦 Dependencies

```
streamlit>=1.32.0
requests>=2.31.0
python-dotenv>=1.0.0
pypdf2>=3.0.0
pdfplumber>=0.10.0
python-docx>=1.1.0
```

---

## 💡 Tips

- **Best results**: Upload full resume PDF
- **Manual mode**: Type skills comma-separated
- **Course Agent**: Works best with 3+ missing skills
- **Free Groq tier**: ~14,400 tokens/minute on LLaMA-3.1-8b, ~6,000 on 70b

---

Made with ❤️ using Groq + Streamlit
