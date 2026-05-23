"""
job_database.py — 35+ job roles covering traditional + AI-era specializations
Categories: Core Dev | AI/ML/GenAI | Data | Cloud/DevOps | Design | Emerging
"""

JOB_SKILL_DATABASE = {

    # ─── CORE DEVELOPMENT ────────────────────────────────────────────────────

    "Backend Developer": {
        "required_skills": ["Python", "REST APIs", "SQL", "Git", "Linux", "Django", "FastAPI", "Databases"],
        "nice_to_have":    ["Redis", "Celery", "Kafka", "GraphQL", "PostgreSQL", "MongoDB"]
    },
    "Frontend Developer": {
        "required_skills": ["JavaScript", "React.js", "HTML", "CSS", "Git", "Responsive Design", "TypeScript"],
        "nice_to_have":    ["Next.js", "Vue.js", "Tailwind CSS", "Redux", "Testing", "Figma"]
    },
    "Full Stack Developer": {
        "required_skills": ["JavaScript", "React.js", "Node.js", "SQL", "REST APIs", "Git", "HTML", "CSS"],
        "nice_to_have":    ["TypeScript", "MongoDB", "Docker", "AWS", "GraphQL", "Redis"]
    },
    "Android Developer": {
        "required_skills": ["Kotlin", "Android SDK", "REST APIs", "Git", "Java", "XML Layouts", "MVVM"],
        "nice_to_have":    ["Jetpack Compose", "Firebase", "Room Database", "Coroutines", "Unit Testing"]
    },
    "iOS Developer": {
        "required_skills": ["Swift", "Xcode", "iOS SDK", "REST APIs", "Git", "Auto Layout", "UIKit"],
        "nice_to_have":    ["SwiftUI", "Core Data", "Combine", "CocoaPods", "TestFlight", "Firebase"]
    },
    "Blockchain Developer": {
        "required_skills": ["Solidity", "Smart Contracts", "Ethereum", "Web3.js", "JavaScript", "Cryptography", "Git"],
        "nice_to_have":    ["Hardhat", "Truffle", "IPFS", "DeFi Protocols", "Rust", "Layer 2 Solutions"]
    },
    "Embedded Systems Engineer": {
        "required_skills": ["C", "C++", "Microcontrollers", "RTOS", "Circuit Design", "Linux Kernel", "Git"],
        "nice_to_have":    ["Python", "ARM Architecture", "CAN Bus", "MQTT", "Firmware OTA", "FreeRTOS"]
    },

    # ─── AI / ML / GENERATIVE AI ─────────────────────────────────────────────

    "ML Engineer": {
        "required_skills": ["Python", "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "MLOps", "Docker", "REST APIs"],
        "nice_to_have":    ["Kubernetes", "AWS SageMaker", "Kubeflow", "FastAPI", "ONNX", "Feature Stores"]
    },
    "AI Agent Developer": {
        "required_skills": ["Python", "LangChain", "LLM APIs", "Prompt Engineering", "REST APIs", "Tool Use / Function Calling", "Vector Databases", "Git"],
        "nice_to_have":    ["AutoGen", "CrewAI", "LlamaIndex", "OpenAI API", "Groq API", "Memory Systems", "Agent Orchestration"]
    },
    "Generative AI Engineer": {
        "required_skills": ["Python", "LLMs", "Prompt Engineering", "OpenAI API", "Hugging Face", "Fine-tuning", "RAG", "Vector Databases"],
        "nice_to_have":    ["LangChain", "LlamaIndex", "Stable Diffusion", "LoRA", "PEFT", "Embeddings", "Pinecone"]
    },
    "AI Product Manager": {
        "required_skills": ["Product Strategy", "AI/ML Fundamentals", "User Research", "Roadmapping", "Prompt Engineering", "Data Analysis", "Stakeholder Management"],
        "nice_to_have":    ["LLM APIs", "A/B Testing", "Agile", "JIRA", "SQL", "UX Research", "Competitive Analysis"]
    },
    "Frontend AI Developer": {
        "required_skills": ["JavaScript", "React.js", "TypeScript", "LLM APIs", "REST APIs", "Streaming UI", "Git", "Tailwind CSS"],
        "nice_to_have":    ["Next.js", "Vercel AI SDK", "OpenAI API", "WebSockets", "LangChain.js", "Voice UI", "Figma"]
    },
    "AI Data Analyst": {
        "required_skills": ["Python", "SQL", "Pandas", "Data Visualization", "Statistics", "LLM Tools", "Excel", "Prompt Engineering"],
        "nice_to_have":    ["Power BI", "Tableau", "LangChain", "AutoML", "Jupyter", "dbt", "Google Colab"]
    },
    "Computer Vision Engineer": {
        "required_skills": ["Python", "OpenCV", "PyTorch", "Deep Learning", "CNNs", "Image Processing", "TensorFlow", "Git"],
        "nice_to_have":    ["YOLO", "Object Detection", "Segmentation", "ONNX", "TensorRT", "Mediapipe", "3D Vision"]
    },
    "NLP Engineer": {
        "required_skills": ["Python", "NLP", "Transformers", "Hugging Face", "PyTorch", "Text Classification", "Named Entity Recognition", "Git"],
        "nice_to_have":    ["BERT", "GPT Fine-tuning", "spaCy", "NLTK", "Embeddings", "LangChain", "RAG"]
    },
    "MLOps Engineer": {
        "required_skills": ["Python", "Docker", "Kubernetes", "CI/CD", "MLflow", "Model Serving", "Cloud Platforms", "Git"],
        "nice_to_have":    ["Kubeflow", "Airflow", "Feature Stores", "DVC", "Prometheus", "Grafana", "AWS SageMaker"]
    },
    "AI Research Scientist": {
        "required_skills": ["Python", "Deep Learning", "PyTorch", "Mathematics", "Statistics", "Research Papers", "Experimentation", "Linear Algebra"],
        "nice_to_have":    ["Reinforcement Learning", "GANs", "Diffusion Models", "LaTeX", "CUDA", "Distributed Training", "JAX"]
    },
    "Prompt Engineer": {
        "required_skills": ["Prompt Engineering", "LLM APIs", "Python", "Chain-of-Thought", "Few-Shot Learning", "OpenAI API", "Technical Writing"],
        "nice_to_have":    ["LangChain", "RAG", "Evaluation Frameworks", "Fine-tuning", "Anthropic Claude", "Groq API", "Structured Outputs"]
    },
    "AI/ML Product Developer": {
        "required_skills": ["Python", "LLM APIs", "FastAPI", "Docker", "Prompt Engineering", "REST APIs", "Product Thinking", "Git"],
        "nice_to_have":    ["Streamlit", "Gradio", "LangChain", "Vector Databases", "React.js", "AWS", "CI/CD"]
    },
    "Reinforcement Learning Engineer": {
        "required_skills": ["Python", "PyTorch", "Reinforcement Learning", "OpenAI Gym", "Deep Learning", "Mathematics", "Statistics"],
        "nice_to_have":    ["Ray RLlib", "Stable Baselines", "RLHF", "Simulation Environments", "Multi-agent Systems", "JAX"]
    },

    # ─── DATA ────────────────────────────────────────────────────────────────

    "Data Scientist": {
        "required_skills": ["Python", "Machine Learning", "Statistics", "Pandas", "NumPy", "SQL", "Data Visualization", "Scikit-learn"],
        "nice_to_have":    ["Deep Learning", "TensorFlow", "PyTorch", "Spark", "Tableau", "R", "Experiment Design"]
    },
    "Data Analyst": {
        "required_skills": ["SQL", "Python", "Excel", "Data Visualization", "Statistics", "Pandas", "Tableau"],
        "nice_to_have":    ["Power BI", "R", "A/B Testing", "Google Analytics", "Looker", "dbt"]
    },
    "Data Engineer": {
        "required_skills": ["Python", "SQL", "Apache Spark", "ETL Pipelines", "Airflow", "AWS", "Data Warehousing"],
        "nice_to_have":    ["Kafka", "dbt", "Snowflake", "Databricks", "BigQuery", "Scala"]
    },
    "Business Intelligence Developer": {
        "required_skills": ["SQL", "Power BI", "Tableau", "Data Modeling", "DAX", "Excel", "ETL", "Data Warehousing"],
        "nice_to_have":    ["Python", "Looker", "Azure Synapse", "Snowflake", "SSRS", "Stakeholder Communication"]
    },
    "Analytics Engineer": {
        "required_skills": ["SQL", "dbt", "Python", "Data Modeling", "Git", "Data Warehousing", "Tableau", "Airflow"],
        "nice_to_have":    ["Snowflake", "BigQuery", "Redshift", "Looker", "Dagster", "Data Quality Testing"]
    },

    # ─── CLOUD / DEVOPS / SECURITY ───────────────────────────────────────────

    "DevOps Engineer": {
        "required_skills": ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS", "Terraform", "Git", "Shell Scripting"],
        "nice_to_have":    ["Ansible", "Jenkins", "Prometheus", "Grafana", "Azure", "GCP"]
    },
    "Cloud Architect": {
        "required_skills": ["AWS", "Azure", "GCP", "Kubernetes", "Terraform", "Networking", "Security", "System Design"],
        "nice_to_have":    ["Cost Optimization", "Multi-cloud", "Serverless", "CloudFormation", "Service Mesh"]
    },
    "Cybersecurity Analyst": {
        "required_skills": ["Network Security", "Linux", "Python", "SIEM", "Vulnerability Assessment", "Incident Response", "Firewalls"],
        "nice_to_have":    ["CEH", "CISSP", "Penetration Testing", "Splunk", "Wireshark", "OSINT"]
    },
    "Site Reliability Engineer": {
        "required_skills": ["Linux", "Python", "Kubernetes", "Monitoring", "Incident Management", "CI/CD", "Cloud Platforms", "Git"],
        "nice_to_have":    ["Prometheus", "Grafana", "Terraform", "Chaos Engineering", "SLO/SLA Design", "Go"]
    },

    # ─── DESIGN & PRODUCT ─────────────────────────────────────────────────────

    "UI/UX Designer": {
        "required_skills": ["Figma", "User Research", "Wireframing", "Prototyping", "Design Systems", "Usability Testing", "Adobe XD"],
        "nice_to_have":    ["Motion Design", "HTML/CSS", "Accessibility", "Sketch", "Information Architecture"]
    },
    "Product Manager": {
        "required_skills": ["Product Strategy", "Agile", "User Research", "Data Analysis", "Roadmapping", "Stakeholder Management", "SQL"],
        "nice_to_have":    ["A/B Testing", "Figma", "JIRA", "OKRs", "Growth Hacking", "Competitive Analysis"]
    },
    "Product Designer": {
        "required_skills": ["Figma", "User Research", "Interaction Design", "Prototyping", "Design Systems", "Visual Design", "Accessibility"],
        "nice_to_have":    ["Motion Design", "Framer", "HTML/CSS", "Data-driven Design", "AI Tools", "Component Libraries"]
    },

    # ─── QUALITY & TESTING ───────────────────────────────────────────────────

    "QA Engineer": {
        "required_skills": ["Manual Testing", "Test Cases", "SQL", "API Testing", "Bug Reporting", "Selenium", "Git"],
        "nice_to_have":    ["Cypress", "JIRA", "Performance Testing", "Python", "Postman", "CI/CD"]
    },
    "SDET (Software Dev Engineer in Test)": {
        "required_skills": ["Python", "Selenium", "API Testing", "CI/CD", "Git", "Test Automation Frameworks", "SQL"],
        "nice_to_have":    ["Playwright", "Cypress", "Docker", "Performance Testing", "BDD/TDD", "Postman"]
    },

    # ─── EMERGING / SPECIALIST ────────────────────────────────────────────────

    "AR/VR Developer": {
        "required_skills": ["Unity", "C#", "3D Modeling", "Spatial Computing", "Git", "XR Development", "Shader Programming"],
        "nice_to_have":    ["Unreal Engine", "WebXR", "ARKit", "ARCore", "Blender", "OpenXR", "Hand Tracking"]
    },
    "Robotics Engineer": {
        "required_skills": ["Python", "ROS", "C++", "Computer Vision", "Control Systems", "Kinematics", "Embedded Systems"],
        "nice_to_have":    ["Gazebo", "SLAM", "Reinforcement Learning", "PyBullet", "Motion Planning", "Sensor Fusion"]
    },
}

ROLE_META = {
    "Backend Developer":                    {"salary": "₹6–22 LPA",  "demand": 88, "growth": "+18%", "icon": "⚙️"},
    "Frontend Developer":                   {"salary": "₹5–20 LPA",  "demand": 85, "growth": "+15%", "icon": "🎨"},
    "Full Stack Developer":                 {"salary": "₹6–24 LPA",  "demand": 89, "growth": "+22%", "icon": "💻"},
    "Android Developer":                    {"salary": "₹5–20 LPA",  "demand": 83, "growth": "+12%", "icon": "📱"},
    "iOS Developer":                        {"salary": "₹6–22 LPA",  "demand": 81, "growth": "+11%", "icon": "🍎"},
    "Blockchain Developer":                 {"salary": "₹10–35 LPA", "demand": 78, "growth": "+25%", "icon": "⛓️"},
    "Embedded Systems Engineer":            {"salary": "₹6–20 LPA",  "demand": 80, "growth": "+14%", "icon": "🔌"},
    "ML Engineer":                          {"salary": "₹10–30 LPA", "demand": 95, "growth": "+35%", "icon": "🤖"},
    "AI Agent Developer":                   {"salary": "₹12–40 LPA", "demand": 98, "growth": "+60%", "icon": "🧠"},
    "Generative AI Engineer":               {"salary": "₹14–45 LPA", "demand": 97, "growth": "+55%", "icon": "✨"},
    "AI Product Manager":                   {"salary": "₹18–55 LPA", "demand": 93, "growth": "+42%", "icon": "🎯"},
    "Frontend AI Developer":                {"salary": "₹8–28 LPA",  "demand": 91, "growth": "+38%", "icon": "🖥️"},
    "AI Data Analyst":                      {"salary": "₹5–18 LPA",  "demand": 90, "growth": "+30%", "icon": "🔍"},
    "Computer Vision Engineer":             {"salary": "₹10–32 LPA", "demand": 92, "growth": "+40%", "icon": "👁️"},
    "NLP Engineer":                         {"salary": "₹10–35 LPA", "demand": 93, "growth": "+44%", "icon": "💬"},
    "MLOps Engineer":                       {"salary": "₹10–30 LPA", "demand": 91, "growth": "+36%", "icon": "🔄"},
    "AI Research Scientist":                {"salary": "₹15–60 LPA", "demand": 89, "growth": "+32%", "icon": "🔬"},
    "Prompt Engineer":                      {"salary": "₹8–25 LPA",  "demand": 88, "growth": "+50%", "icon": "💡"},
    "AI/ML Product Developer":              {"salary": "₹10–35 LPA", "demand": 94, "growth": "+48%", "icon": "🚀"},
    "Reinforcement Learning Engineer":      {"salary": "₹14–50 LPA", "demand": 86, "growth": "+38%", "icon": "🎮"},
    "Data Scientist":                       {"salary": "₹8–25 LPA",  "demand": 92, "growth": "+22%", "icon": "📊"},
    "Data Analyst":                         {"salary": "₹4–15 LPA",  "demand": 86, "growth": "+16%", "icon": "📈"},
    "Data Engineer":                        {"salary": "₹8–28 LPA",  "demand": 90, "growth": "+26%", "icon": "🏗️"},
    "Business Intelligence Developer":      {"salary": "₹6–20 LPA",  "demand": 82, "growth": "+14%", "icon": "📉"},
    "Analytics Engineer":                   {"salary": "₹8–24 LPA",  "demand": 85, "growth": "+20%", "icon": "🧮"},
    "DevOps Engineer":                      {"salary": "₹8–28 LPA",  "demand": 90, "growth": "+28%", "icon": "🔧"},
    "Cloud Architect":                      {"salary": "₹15–50 LPA", "demand": 94, "growth": "+40%", "icon": "☁️"},
    "Cybersecurity Analyst":                {"salary": "₹7–24 LPA",  "demand": 93, "growth": "+32%", "icon": "🔒"},
    "Site Reliability Engineer":            {"salary": "₹10–32 LPA", "demand": 88, "growth": "+24%", "icon": "📡"},
    "UI/UX Designer":                       {"salary": "₹4–18 LPA",  "demand": 83, "growth": "+18%", "icon": "🎭"},
    "Product Manager":                      {"salary": "₹12–40 LPA", "demand": 87, "growth": "+20%", "icon": "📋"},
    "Product Designer":                     {"salary": "₹6–22 LPA",  "demand": 84, "growth": "+19%", "icon": "🖌️"},
    "QA Engineer":                          {"salary": "₹4–16 LPA",  "demand": 80, "growth": "+12%", "icon": "🧪"},
    "SDET (Software Dev Engineer in Test)": {"salary": "₹7–22 LPA",  "demand": 82, "growth": "+16%", "icon": "🔨"},
    "AR/VR Developer":                      {"salary": "₹8–28 LPA",  "demand": 79, "growth": "+30%", "icon": "🥽"},
    "Robotics Engineer":                    {"salary": "₹8–30 LPA",  "demand": 81, "growth": "+28%", "icon": "🦾"},
}


def get_all_roles():
    return sorted(JOB_SKILL_DATABASE.keys())
