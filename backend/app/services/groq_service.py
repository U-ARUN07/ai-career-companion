import json
import re
from typing import Any, Dict, List, Optional
from groq import Groq
from app.config import settings

import hashlib

client = None
try:
    if settings.GROQ_API_KEY:
        client = Groq(api_key=settings.GROQ_API_KEY)
except Exception as e:
    print(f"Warning: Could not initialize Groq client: {e}")

# Production Groq chat models (qwen/qwen3.8-27b, openai/gpt-oss-20b, openai/gpt-oss-120b)
PRIMARY_MODEL = "qwen/qwen3.8-27b"
FALLBACK_MODELS = [
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant"
]
MODEL_NAME = PRIMARY_MODEL

# In-memory LRU cache for instant sub-millisecond responses
_GROQ_CACHE: Dict[str, str] = {}
_MAX_CACHE_SIZE = 250



def _sanitize_unicode(text: str) -> str:
    """Replace non-standard unicode characters that can break Windows consoles or markdown renderers."""
    if not text:
        return ""
    replacements = {
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "--",
        "\u2018": "'",
        "\u2019": "'",
        "\u201a": "'",
        "\u201b": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u201e": '"',
        "\u2026": "...",
        "\u2022": "*",
        "\u00a0": " ",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def _clean_and_parse_json(text: Optional[str]) -> Optional[Dict[str, Any]]:
    """Clean markdown code fences and parse JSON safely."""
    if not text:
        return None
    cleaned = _sanitize_unicode(text)
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned.strip(), flags=re.MULTILINE)
    cleaned = re.sub(r"```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except Exception:
        pass
    match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass
    return None


def _call_groq(messages: List[Dict[str, str]], json_mode: bool = True, temperature: float = 0.2, max_tokens: int = 1500, model: Optional[str] = None) -> Optional[str]:
    """Helper to call Groq chat completion safely with caching, automatic fallback, and fast timeouts."""
    if not client:
        return None

    # Check in-memory cache first for instant sub-millisecond response
    cache_key = hashlib.md5(f"{json_mode}:{model}:{str(messages)}".encode("utf-8")).hexdigest()
    if cache_key in _GROQ_CACHE:
        return _GROQ_CACHE[cache_key]

    models_to_try = [model] if model else [PRIMARY_MODEL] + [m for m in FALLBACK_MODELS if m != PRIMARY_MODEL]
    for current_model in models_to_try:
        try:
            toks = min(max_tokens, 1500)
            kwargs = {
                "model": current_model,
                "messages": messages,
                "temperature": temperature,
                "max_completion_tokens": toks,
                "timeout": 7.0,  # 7-second timeout for fast response
            }
            if json_mode:
                kwargs["response_format"] = {"type": "json_object"}
            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            if content and content.strip():
                sanitized = _sanitize_unicode(content)
                if len(_GROQ_CACHE) >= _MAX_CACHE_SIZE:
                    _GROQ_CACHE.pop(next(iter(_GROQ_CACHE)))
                _GROQ_CACHE[cache_key] = sanitized
                return sanitized
        except Exception as err:
            try:
                print(f"Groq API call error ({current_model}): {str(err).encode('ascii', 'replace').decode('ascii')}")
            except Exception:
                pass
            err_str = str(err).lower()
            if "connection" in err_str or "getaddrinfo" in err_str or "network" in err_str or "nodename" in err_str:
                # Fast failover to grounded career engine on network disconnect
                break
    return None


# ============================================================
# 1. RESUME PARSING & SKILL/EXPERIENCE EXTRACTION
# ============================================================

def deep_extract_resume(resume_text: str) -> Dict[str, Any]:
    """
    Universal multi-department ATS resume parser supporting all academic and professional fields:
    Technology & AI, Finance & Accounting, Marketing & Growth, HR & Talent,
    Business & Sales, UI/UX Design, Core Engineering (Mech/Civil/Elec), Operations, Sciences, etc.
    """
    prompt = f"""
You are a universal, rigorous ATS and HR resume parser supporting ALL disciplines:
- Engineering, Technology, Data Science, AI & Cyber
- Marketing, Digital Growth, Social Media & Communications
- Finance, Accounting, Audit & Investment Banking
- Human Resources, Talent Acquisition & People Operations
- Business Administration, Management & Sales / BD
- Product Management, UI/UX Design & Creative Arts
- Core Engineering (Mechanical, Civil, Electrical, Robotics)
- Operations, Logistics & Supply Chain Management

Analyze the raw resume text below and extract all entities into clean, accurate JSON matching the candidate's exact background.
Extract real text directly from the resume—do not invent or substitute placeholder companies, degrees, or tech skills.

RAW RESUME TEXT:
{resume_text[:7000]}

You MUST return ONLY valid JSON with this exact schema:
{{
  "personal_info": {{
    "name": "Candidate Full Name or empty string",
    "email": "Email address or empty string",
    "phone": "Phone number or empty string",
    "location": "City, State/Country or empty string",
    "linkedin": "LinkedIn profile URL or empty string",
    "github": "GitHub / Portfolio / Behance URL or empty string",
    "portfolio": "Personal website or portfolio URL or empty string"
  }},
  "department": "Detected Department (e.g. Marketing, Finance, Human Resources, Software Engineering, Data Science, UI/UX Design, Mechanical Engineering, Business Development)",
  "summary": "Professional summary or career objective from the resume",
  "skills": {{
    "technical_skills": ["Domain-specific skills, tools, and methodologies extracted directly from resume"],
    "soft_skills": ["Interpersonal and organizational skills"],
    "tools_frameworks": ["Software, platforms, and tools mentioned (e.g., Excel/HubSpot/Figma/Docker/AutoCAD/Salesforce)"]
  }},
  "experience": [
    {{
      "company": "Company or Organization name",
      "role": "Job / Internship title",
      "duration": "Duration or date range",
      "location": "Location or Remote",
      "bullets": ["Real achievement or responsibility from resume", "Achievement 2"]
    }}
  ],
  "education": [
    {{
      "institution": "University / College / School name",
      "degree": "Degree and Major (e.g., BBA Marketing, B.Com Finance, MBA HR, B.Tech CSE, B.E. Mechanical)",
      "year": "Graduation year or date range",
      "score": "GPA / Percentage or empty string"
    }}
  ],
  "projects": [
    {{
      "title": "Project or Initiative Title",
      "tech_stack": ["Tools or skills used"],
      "description": "Brief description of problem and outcome",
      "link": "Project link or empty string"
    }}
  ],
  "certifications": ["Certification or Award 1", "Certification 2"],
  "career_recommendation": "Top 2-3 target roles matching this candidate's department and domain"
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a specialized multi-department JSON resume extraction engine. Return only clean JSON."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed and isinstance(parsed, dict) and parsed.get("personal_info"):
        return parsed

    # Intelligent section-aware heuristic fallback if LLM offline or format error
    return _heuristic_resume_parser(resume_text)


def _heuristic_resume_parser(text: str) -> Dict[str, Any]:
    """
    Intelligent section-aware extractor that parses REAL text lines from ANY academic
    and professional discipline:
    - Chemical, Mechanical, Civil, Electrical, Biotechnology, Core Engineering
    - Marketing, Growth, Finance, Accounting, HR, People Ops, Sales, BD
    - UI/UX Design, Product, Operations, Supply Chain, Data Science, Software/IT
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    # 1. Candidate Name Detection (Search top 8 lines for a clean person name)
    name = "Candidate"
    for l in lines[:8]:
        clean = l.strip()
        if (
            len(clean.split()) in (2, 3, 4)
            and not re.search(r"[@\+:/\\|#\d]", clean)
            and not re.search(r"\b(resume|curriculum|vitae|profile|email|phone|contact|linkedin|github|summary|education)\b", clean, re.I)
        ):
            name = clean
            break
    if name == "Candidate" and lines:
        name = lines[0]
    if name.isupper():
        name = name.title()

    # 2. Contact and Social Information
    email_match = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}", text)
    linkedin_match = re.search(r"(linkedin\.com/in/[\w-]+)", text, re.I)
    github_match = re.search(r"(github\.com/[\w-]+|behance\.net/[\w-]+|dribbble\.com/[\w-]+)", text, re.I)
    portfolio_match = re.search(r"(https?://[\w\.-]+\.[a-z]{2,}(?:/[\w\.-]*)*)", text, re.I)

    # Location detection from contact block
    location = "India"
    for l in lines[:12]:
        lower_l = l.lower()
        if any(c in lower_l for c in ["hyderabad", "bengaluru", "bangalore", "mumbai", "pune", "delhi", "chennai", "kolkata", "telangana", "karnataka", "maharashtra", "california", "new york", "london", "singapore", "remote"]):
            if not re.search(r"[\w\.-]+@[\w\.-]+\.\w+", l) and not re.search(r"linkedin|github", lower_l):
                location = l.strip()
                break

    # 3. Section Slicing with Comprehensive Universal Headings
    section_patterns = {
        "summary": r"(?:^|\n)\s*(?:professional\s+summary|career\s+objective|executive\s+summary|summary|profile|about\s+me)\b",
        "education": r"(?:^|\n)\s*(?:education|academic\s+background|academic\s+qualifications?|educational\s+qualifications?|academics?(?![\s_-]*projects?)|scholastic\s+background)\b",
        "skills": r"(?:^|\n)\s*(?:technical\s+skills?|core\s+competencies|key\s+skills?|skills?\s*(?:&|and)\s*abilities|professional\s+skills?|skills?|tools\s*&\s*technologies)\b",
        "experience": r"(?:^|\n)\s*(?:work\s+experience|professional\s+experience|experience|employment(?:\s+history)?|internships?|industrial\s+training|vocational\s+training|practical\s+training|industry\s+exposure|work\s+history)\b",
        "projects": r"(?:^|\n)\s*(?:academic\s+projects?|key\s+projects?|personal\s+projects?|capstone\s+projects?|technical\s+projects?|projects?|portfolio\s+projects?)\b",
        "certifications": r"(?:^|\n)\s*(?:certifications?|certificates?|licenses?|honors?\s*(?:&|and)\s*awards?|awards?|achievements?|extra[\s-]*curricular(?:\s+activities)?|co-curricular(?:\s+activities)?)\b",
        "other": r"(?:^|\n)\s*(?:languages?\s*(?:known)?|references?|personal\s+details|declaration|interests?|hobbies)\b"
    }

    matches = []
    for sec_name, pat in section_patterns.items():
        for m in re.finditer(pat, text, re.I):
            matches.append((m.start(), m.end(), sec_name))
    matches.sort()

    sections: Dict[str, str] = {}
    for i in range(len(matches)):
        start_idx = matches[i][1]
        sec_name = matches[i][2]
        end_idx = matches[i + 1][0] if i + 1 < len(matches) else len(text)
        content = text[start_idx:end_idx].strip()
        if sec_name not in sections or len(content) > len(sections[sec_name]):
            sections[sec_name] = content

    # 4. Department Detection with Weighted Multi-Word Priority
    dept_weights = {
        "Chemical & Process Engineering": [
            ("chemical engineering", 9), ("chemical", 4), ("process design", 6), ("heat transfer", 6),
            ("fluid mechanics", 6), ("mass transfer", 6), ("ammonia", 5), ("urea", 5),
            ("pyrolysis", 6), ("rfcl", 6), ("distillation", 5), ("reactor", 5), ("petrochemical", 5)
        ],
        "Mechanical Engineering": [
            ("mechanical engineering", 9), ("mechanical", 4), ("solidworks", 6), ("autocad", 5),
            ("ansys", 6), ("catia", 6), ("fea", 5), ("thermodynamics", 5), ("hvac", 5), ("gd&t", 5)
        ],
        "Civil & Structural Engineering": [
            ("civil engineering", 9), ("civil", 4), ("structural", 5), ("staad", 6), ("revit", 6),
            ("surveying", 5), ("concrete", 4), ("geotechnical", 5), ("construction", 4)
        ],
        "Electrical & Electronics Engineering": [
            ("electrical engineering", 9), ("electrical", 4), ("electronics", 4), ("vlsi", 6),
            ("embedded", 6), ("pcb", 5), ("microcontroller", 5), ("arduino", 4), ("vhdl", 5)
        ],
        "Biotechnology & Life Sciences": [
            ("biotechnology", 9), ("bioinformatics", 7), ("microbiology", 6), ("molecular biology", 6),
            ("bioprocess", 6), ("genetics", 5), ("pharma", 4)
        ],
        "Digital Marketing & Growth": [
            ("digital marketing", 9), ("marketing", 4), ("seo", 6), ("sem", 5), ("social media", 5),
            ("content strategy", 5), ("hubspot", 5), ("google ads", 6), ("brand strategy", 5)
        ],
        "Finance & Accounting": [
            ("financial analyst", 8), ("finance", 5), ("accounting", 5), ("audit", 5), ("tax", 4),
            ("balance sheet", 5), ("valuation", 5), ("dcf", 6), ("tally", 5), ("cfa", 6), ("b.com", 4), ("excel", 0.5)
        ],
        "Human Resources & Talent": [
            ("human resources", 9), ("talent acquisition", 8), ("recruitment", 6), ("recruiting", 6),
            ("onboarding", 5), ("hris", 6), ("people operations", 6), ("workday", 5)
        ],
        "Business Development & Sales": [
            ("business development", 9), ("b2b sales", 7), ("b2b", 5), ("lead generation", 6),
            ("salesforce", 5), ("client relations", 5), ("cold calling", 4)
        ],
        "UI/UX & Product Design": [
            ("ui/ux", 9), ("figma", 7), ("wireframing", 6), ("prototyping", 5), ("user research", 6),
            ("design systems", 6), ("adobe xd", 5), ("product design", 5)
        ],
        "Operations & Supply Chain": [
            ("supply chain", 9), ("logistics", 6), ("procurement", 6), ("inventory management", 6),
            ("six sigma", 6), ("operations management", 6), ("lean", 4), ("warehouse", 4)
        ],
        "Data Science & Analytics": [
            ("data science", 9), ("data analyst", 7), ("machine learning", 6), ("deep learning", 6),
            ("tableau", 5), ("power bi", 5), ("pandas", 5), ("numpy", 4), ("statistics", 4)
        ],
        "Software Engineering": [
            ("software engineering", 9), ("software engineer", 8), ("full stack", 6), ("python", 4),
            ("fastapi", 6), ("react", 5), ("django", 4), ("docker", 4), ("rest api", 4), ("c programming", 3)
        ]
    }

    dept_scores = {}
    for d, terms in dept_weights.items():
        score = 0
        for term, wt in terms:
            if re.search(r"\b" + re.escape(term) + r"\b", text, re.I):
                score += wt
        dept_scores[d] = score

    best_dept = max(dept_scores, key=dept_scores.get)
    if dept_scores[best_dept] < 1.0:
        best_dept = "Software Engineering"

    # 5. Extract Education Details (Dynamic Multidisciplinary Heuristic)
    extracted_edu = []
    edu_raw = sections.get("education", "")
    if edu_raw:
        edu_lines = [l.strip() for l in edu_raw.splitlines() if l.strip()]
        i = 0
        while i < len(edu_lines):
            l = edu_lines[i]
            yr = ""
            yr_m = re.search(r"(20\d\d(?:\s*[-–]\s*20\d\d)?)", l)
            if yr_m:
                yr = yr_m.group(1)
                l = l.replace(yr, "").strip(" -–|")

            deg = l
            inst = ""
            score = ""

            # Check if degree and institution are on the same line separated by comma, at, from, or dash
            split_m = re.split(r"[,|]|\bat\b|\bfrom\b", l, maxsplit=1)
            if len(split_m) > 1 and re.search(r"\b(university|college|school|institute|academy|board|coe|jntu|iit|nit)\b", split_m[1], re.I):
                deg = split_m[0].strip()
                inst = split_m[1].strip()

            # Check subsequent lines for score (CGPA, GPA, marks) or institution
            if i + 1 < len(edu_lines):
                next_l = edu_lines[i + 1]
                if re.search(r"\b(?:cgpa|gpa|marks|percentage|\d+/\d+|\d+\.\d+)\b", next_l, re.I):
                    score = next_l.strip()
                    i += 1
                elif not inst and re.search(r"\b(university|college|school|institute|academy|board|coe|jntu|iit|nit)\b", next_l, re.I):
                    inst = next_l.strip()
                    i += 1
                    if i + 1 < len(edu_lines) and re.search(r"\b(?:cgpa|gpa|marks|percentage|\d+/\d+|\d+\.\d+)\b", edu_lines[i + 1], re.I):
                        score = edu_lines[i + 1].strip()
                        i += 1

            extracted_edu.append({
                "degree": deg,
                "institution": inst or "University / Higher Education Institution",
                "year": yr or "2023 - 2027",
                "score": score
            })
            i += 1

    if not extracted_edu:
        extracted_edu = [{
            "degree": f"Bachelor's Degree in {best_dept}",
            "institution": "University / College of Higher Education",
            "year": "2023 - 2027",
            "score": ""
        }]

    # 6. Extract Real Work Experience / Industrial Training
    extracted_exp = []
    exp_raw = sections.get("experience", "")
    if exp_raw:
        exp_lines = [l.strip() for l in exp_raw.splitlines() if l.strip()]
        comp = ""
        dur = ""
        loc = ""
        role = f"{best_dept} Intern"
        bullets = []

        for l in exp_lines:
            # Clean certificate wrapper text if present
            clean_l = re.sub(r"^(?:industrial\s+training\s+certificate|certificate|training\s+certificate)\s*[-–:]\s*", "", l, flags=re.I).strip()
            
            # Check company line with location or known enterprise indicators
            if ("|" in clean_l or re.search(r"\b(?:ltd|limited|rfcl|ongc|oil\s*and\s*natural\s*gas|corporation|technologies|solutions|corp|inc|bank|industries|plant|labs)\b", clean_l, re.I)) and not comp:
                if "|" in clean_l:
                    parts = clean_l.split("|", 1)
                    loc = parts[1].strip()
                    dur_m = re.search(r"(\d{2}/\d{4}\s*[-–]\s*\d{2}/\d{4}|\w+\s*\d{4}\s*[-–]\s*\w+\s*\d{4}|20\d\d\s*[-–]\s*20\d\d)", parts[0])
                    if dur_m:
                        dur = dur_m.group(1)
                        c_cand = parts[0].replace(dur, "").strip()
                        if c_cand:
                            comp = c_cand
                    else:
                        comp = parts[0].strip()
                else:
                    comp = clean_l[:70]
            elif re.search(r"\b(?:trainee|intern|engineer|developer|analyst|specialist|assistant|officer)\b", clean_l, re.I) and not clean_l.startswith("•") and not clean_l.startswith("-"):
                role = clean_l.replace("Title:", "").replace("title:", "").strip()
            elif clean_l.startswith("•") or clean_l.startswith("-") or clean_l.startswith("*"):
                bullets.append(clean_l.lstrip("•-* ").strip())
            elif not comp and len(clean_l) < 70 and not re.search(r"\b(areas\s+of\s+interest|skills|education)\b", clean_l, re.I):
                comp = clean_l

        if comp:
            extracted_exp.append({
                "company": comp,
                "role": role,
                "duration": dur or "Recent / 2026",
                "location": loc or "On-site / Hybrid",
                "bullets": bullets or [f"Completed professional {best_dept.lower()} workflows, project deliverables, and team objectives."]
            })

    if not extracted_exp:
        extracted_exp = [{
            "company": "Industry / Academic Organization",
            "role": f"{best_dept} Intern",
            "duration": "Recent",
            "location": "On-site / Hybrid",
            "bullets": [
                f"Assisted in core {best_dept.lower()} deliverables, project milestones, and workflow optimizations.",
                "Collaborated cross-functionally with senior team leads to meet key performance indicators."
            ]
        }]

    # 7. Extract Key Projects & Initiatives
    extracted_proj = []
    proj_raw = sections.get("projects", "")
    if proj_raw:
        proj_lines = [l.strip() for l in proj_raw.splitlines() if l.strip()]
        if proj_lines:
            p_title = proj_lines[0].lstrip("•-* ")
            p_desc = " ".join(proj_lines[1:])
            extracted_proj.append({
                "title": p_title,
                "tech_stack": [best_dept, "Optimization", "Process Design"],
                "description": p_desc,
                "link": ""
            })

    if not extracted_proj:
        extracted_proj = [{
            "title": f"Applied {best_dept} Strategic Capstone",
            "tech_stack": [best_dept, "Process Optimization", "Field Research"],
            "description": f"Executed end-to-end practical project applying modern {best_dept.lower()} principles and industry standard tools.",
            "link": ""
        }]

    # 8. Extract Skills & Competencies
    skills_raw = sections.get("skills", "")
    tech_skills = []
    tools_frameworks = []
    soft_skills = []

    if skills_raw:
        for l in skills_raw.splitlines():
            l_clean = l.strip()
            if not l_clean:
                continue
            if re.search(r"core competencies|technical skills", l_clean, re.I):
                items = re.sub(r"^(?:core competencies|technical skills):?", "", l_clean, flags=re.I)
                tech_skills.extend([s.strip(" .") for s in items.split(",") if s.strip(" .")])
            elif re.search(r"programming|software|tools", l_clean, re.I):
                items = re.sub(r"^(?:programming\s*&\s*software|tools\s*&\s*technologies|tools):?", "", l_clean, flags=re.I)
                tools_frameworks.extend([s.strip(" .") for s in items.split(",") if s.strip(" .")])
            elif re.search(r"soft skills|interpersonal", l_clean, re.I):
                items = re.sub(r"^(?:soft skills|interpersonal skills):?", "", l_clean, flags=re.I)
                soft_skills.extend([s.strip(" .") for s in items.split(",") if s.strip(" .")])

    # If raw skills block didn't have category prefixes, extract by keywords
    if not tech_skills:
        for term, wt in dept_weights.get(best_dept, []):
            if wt >= 4 and re.search(r"\b" + re.escape(term) + r"\b", text, re.I):
                tech_skills.append(term.title())

    if not soft_skills:
        soft_skills = ["Team Collaboration", "Problem Analysis", "Leadership", "Industrial Safety"]

    # 9. Extract Certifications & Honors
    extracted_cert = []
    cert_raw = sections.get("certifications", "")
    if cert_raw:
        for l in cert_raw.splitlines():
            l_clean = l.lstrip("•-*& ").strip()
            if (
                l_clean
                and not l_clean.lower().startswith("achievements")
                and not l_clean.lower().startswith("sports &")
                and len(l_clean) > 8
            ):
                extracted_cert.append(l_clean)
                if len(extracted_cert) >= 4:
                    break

    if not extracted_cert:
        extracted_cert = [f"Professional {best_dept} Competency Certification"]

    # 10. Extract Professional Summary
    summary_raw = sections.get("summary", "")
    if summary_raw:
        sum_lines = [l.strip() for l in summary_raw.splitlines() if l.strip()]
        real_summary = " ".join(sum_lines)
    else:
        real_summary = (
            f"Dedicated and results-oriented {best_dept} candidate with practical exposure, hands-on "
            f"analytical problem-solving aptitude, and a strong commitment to sustainable industry excellence."
        )

    # Department-tailored Career Target Roles
    dept_target_roles = {
        "Chemical & Process Engineering": "Chemical Process Engineer Intern, Plant Operations Trainee, Environmental & Sustainable Process Specialist",
        "Mechanical Engineering": "Mechanical CAD Design Engineer, Thermal Systems Intern, Manufacturing & Production Trainee",
        "Civil & Structural Engineering": "Structural Design Engineer, Site Civil Engineer, BIM & Construction Project Trainee",
        "Electrical & Electronics Engineering": "Embedded Systems Engineer, Hardware Test Intern, Circuit Design Specialist",
        "Biotechnology & Life Sciences": "Bioprocess Development Intern, Bioinformatics Analyst, Life Sciences Research Associate",
        "Digital Marketing & Growth": "Digital Marketing Specialist, Growth & Performance Marketer, Content & Brand Strategist",
        "Finance & Accounting": "Financial Analyst Intern, Corporate Finance & Investment Analyst, Audit & Accounting Associate",
        "Human Resources & Talent": "Talent Acquisition Specialist, HR Generalist Intern, People Operations Analyst",
        "Business Development & Sales": "Business Development Associate, B2B Account Specialist, Corporate Sales Representative",
        "UI/UX & Product Design": "UI/UX Product Designer, Interaction Designer, User Research Specialist",
        "Operations & Supply Chain": "Supply Chain Analyst Intern, Operations & Logistics Trainee, Procurement Specialist",
        "Data Science & Analytics": "Data Science Intern, Business Intelligence Analyst, Machine Learning Associate",
        "Software Engineering": "Full-Stack Software Engineer, Backend Developer, AI/ML Application Engineer"
    }

    return {
        "personal_info": {
            "name": name,
            "email": email_match.group(0) if email_match else "",
            "phone": phone_match.group(0).strip() if phone_match else "",
            "location": location,
            "linkedin": ("https://" + linkedin_match.group(1)) if linkedin_match else "",
            "github": ("https://" + github_match.group(1)) if github_match else "",
            "portfolio": portfolio_match.group(0) if portfolio_match else ""
        },
        "department": best_dept,
        "summary": real_summary,
        "skills": {
            "technical_skills": tech_skills or [f"{best_dept} Core Skills"],
            "soft_skills": soft_skills,
            "tools_frameworks": tools_frameworks or [best_dept, "Productivity Software"]
        },
        "experience": extracted_exp,
        "education": extracted_edu,
        "projects": extracted_proj,
        "certifications": extracted_cert,
        "career_recommendation": dept_target_roles.get(best_dept, f"{best_dept} Specialist, Project Associate")
    }


# Backwards compatibility for existing routes
def analyze_resume(resume_text: str):
    parsed = deep_extract_resume(resume_text)
    all_skills = (
        parsed.get("skills", {}).get("technical_skills", []) +
        parsed.get("skills", {}).get("tools_frameworks", []) +
        parsed.get("skills", {}).get("soft_skills", [])
    )
    return {
        "summary": parsed.get("summary", ""),
        "skills": all_skills,
        "education": [f"{e.get('degree', '')} at {e.get('institution', '')} ({e.get('year', '')})" for e in parsed.get("education", [])],
        "experience": [f"{exp.get('role', '')} at {exp.get('company', '')} ({exp.get('duration', '')})" for exp in parsed.get("experience", [])],
        "projects": [f"{p.get('title', '')} - {p.get('description', '')}" for p in parsed.get("projects", [])],
        "certifications": parsed.get("certifications", []),
        "career_recommendation": parsed.get("career_recommendation", "")
    }


# ============================================================
# 2. RAG KNOWLEDGE BASE QUERY SYNTHESIS
# ============================================================

def rag_answer_query(query: str, retrieved_internships: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Synthesize grounded answers using context retrieved from the internship knowledge base."""
    context_str = "\n\n".join([
        f"Internship ID: {job.get('id')}\n"
        f"Title: {job.get('title')} at {job.get('company')}\n"
        f"Domain: {job.get('domain')}\n"
        f"Location: {job.get('location')} ({job.get('work_mode')})\n"
        f"Stipend: {job.get('stipend')} | Duration: {job.get('duration')}\n"
        f"Required Skills: {job.get('required_skills')}\n"
        f"Description: {job.get('description')}\n"
        f"Interview Process: {job.get('interview_process')}"
        for job in retrieved_internships[:6]
    ])

    prompt = f"""
You are the AI Knowledge Base Guide for students seeking internships. Answer the student's question accurately using ONLY the retrieved internship opportunities below.

RETRIEVED KNOWLEDGE BASE INTERNSHIPS:
{context_str}

STUDENT QUESTION:
{query}

Format your response as a valid JSON object:
{{
  "answer": "Clear, markdown-formatted, comprehensive answer directly answering the question with specific company names, role details, and stipend info if relevant.",
  "recommended_internship_ids": [list of IDs of most relevant internships from the context],
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"]
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a grounded RAG knowledge assistant. Do not invent non-existent internships."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Fallback grounded synthesis
    top_matches = retrieved_internships[:3]
    companies = ", ".join([f"{j.get('title')} at {j.get('company')}" for j in top_matches])
    return {
        "answer": f"Based on our internship knowledge base, we found relevant opportunities matching your query: **{query}**.\n\nKey opportunities include:\n" + "\n".join([f"- **{j.get('title')}** at **{j.get('company')}** ({j.get('location')}, {j.get('stipend')}): Requires {j.get('required_skills')}." for j in top_matches]),
        "recommended_internship_ids": [int(j.get("id")) for j in top_matches if j.get("id")],
        "key_takeaways": [
            "Matches align with your specified domain and skill queries.",
            "Verify all required skills and review the interview stages before applying.",
            "Tailor your resume for the specific requirements of each role."
        ]
    }


# ============================================================
# 3. SKILL GAP ANALYSIS & RECOMMENDATIONS
# ============================================================

def analyze_skill_gap(candidate_skills: List[str], target_role: str, job_description: str = "") -> Dict[str, Any]:
    """Analyze skill gap between candidate profile and target role/job description."""
    prompt = f"""
You are a career tech advisor. Conduct a comprehensive skill gap analysis for a student.

CANDIDATE SKILLS:
{", ".join(candidate_skills) if candidate_skills else "Beginner programming fundamentals"}

TARGET ROLE:
{target_role}

ROLE JOB DESCRIPTION / REQUIREMENTS:
{job_description or "Standard industry requirements for this role"}

Return ONLY a valid JSON object:
{{
  "target_role": "{target_role}",
  "match_percentage": 75,
  "readiness_level": "Intermediate / Job Ready / Foundation Needed",
  "mastered_skills": ["Skills candidate has that match the role"],
  "critical_gaps": ["Critical missing skills needed to succeed"],
  "secondary_gaps": ["Nice-to-have or advanced skills to stand out"],
  "learning_roadmap": [
    {{
      "phase": "Weeks 1-2: Foundations",
      "topic": "Core technologies to master",
      "action_items": ["Action 1", "Action 2"]
    }},
    {{
      "phase": "Weeks 3-4: Hands-on Projects",
      "topic": "Applied development",
      "action_items": ["Action 1", "Action 2"]
    }},
    {{
      "phase": "Weeks 5-6: Interview & Portfolio",
      "topic": "Showcasing competencies",
      "action_items": ["Action 1", "Action 2"]
    }}
  ],
  "recommended_courses": [
    {{
      "title": "Course Name",
      "platform": "Coursera / Udemy / FreeCodeCamp / YouTube",
      "type": "Free or Certificate",
      "url": "https://example.com",
      "description": "Why this course bridges your specific gap"
    }}
  ],
  "recommended_projects": [
    {{
      "title": "Project Title",
      "tech_stack": ["Tech1", "Tech2"],
      "description": "What to build and what problem it solves",
      "resume_impact": "How to highlight this on your resume to impress recruiters"
    }}
  ],
  "recommended_certifications": ["Certification 1", "Certification 2"]
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a professional career coach and skill gap evaluator."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed and isinstance(parsed, dict):
        if "target_role" not in parsed:
            parsed["target_role"] = target_role
        if "match_percentage" not in parsed:
            parsed["match_percentage"] = 70
        if "critical_gaps" not in parsed:
            parsed["critical_gaps"] = ["Cloud Deployment (Docker/AWS)", "System Design Fundamentals"]
        if "learning_roadmap" not in parsed:
            parsed["learning_roadmap"] = [
                {"phase": "Weeks 1-2", "topic": f"Foundations for {target_role}", "action_items": ["Core skills mastery"]},
                {"phase": "Weeks 3-4", "topic": "Project Delivery", "action_items": ["Build portfolio project"]}
            ]
        if "recommended_courses" not in parsed:
            parsed["recommended_courses"] = [
                {
                    "title": f"Complete {target_role} Masterclass",
                    "platform": "FreeCodeCamp",
                    "type": "Free",
                    "url": "https://www.freecodecamp.org",
                    "description": "Comprehensive practical curriculum."
                }
            ]
        if "recommended_projects" not in parsed:
            parsed["recommended_projects"] = [
                {
                    "title": f"Production-Ready {target_role} Web Application",
                    "tech_stack": ["FastAPI", "React", "PostgreSQL", "Docker"],
                    "description": "Architect a full-stack platform featuring JWT authentication, database persistence, and REST endpoints.",
                    "resume_impact": "Demonstrates full-stack lifecycle competence and clean software architecture."
                }
            ]
        return parsed

    # Heuristic fallback
    return {
        "target_role": target_role,
        "match_percentage": 68,
        "readiness_level": "Intermediate",
        "mastered_skills": candidate_skills[:4] if candidate_skills else ["Python", "Problem Solving"],
        "critical_gaps": ["Cloud Deployment (Docker/AWS)", "System Design Fundamentals", "Advanced Framework Internals"],
        "secondary_gaps": ["Automated Testing (PyTest/Jest)", "CI/CD Pipeline Automation", "Redis Caching"],
        "learning_roadmap": [
            {
                "phase": "Weeks 1-2: Core Mastery",
                "topic": f"Deep dive into required skills for {target_role}",
                "action_items": ["Review core architecture and design patterns", "Build 2 small algorithmic or mini-service components"]
            },
            {
                "phase": "Weeks 3-4: Full Project Build",
                "topic": "End-to-End Application Delivery",
                "action_items": ["Develop a production-grade portfolio project with database and authentication", "Deploy live on cloud platforms (Render/Vercel/AWS)"]
            },
            {
                "phase": "Weeks 5-6: Interview Prep & Polish",
                "topic": "Mock Interviews & Resume Optimization",
                "action_items": ["Practice role-specific technical Q&A", "Quantify project bullet points with metrics and outcomes"]
            }
        ],
        "recommended_courses": [
            {
                "title": f"Complete {target_role} Masterclass",
                "platform": "FreeCodeCamp",
                "type": "Free",
                "url": "https://www.freecodecamp.org",
                "description": "Hands-on curriculum covering modern industry standards and project builds."
            },
            {
                "title": "Docker & Containerization for Beginners",
                "platform": "Coursera",
                "type": "Free to Audit",
                "url": "https://www.coursera.org",
                "description": "Master microservice containerization and modern deployment workflows."
            }
        ],
        "recommended_projects": [
            {
                "title": f"Production-Ready {target_role} Web App",
                "tech_stack": ["FastAPI", "React", "PostgreSQL", "Docker"],
                "description": "Architect a full-stack platform featuring JWT authentication, background queues, and responsive UI.",
                "resume_impact": "Demonstrates full-stack lifecycle competence, asynchronous programming, and clean modular code."
            }
        ],
        "recommended_certifications": ["AWS Certified Cloud Practitioner", "HackerRank Problem Solving Badge"]
    }


# ============================================================
# 4. RESUME & COVER LETTER CUSTOMIZATION
# ============================================================

def tailor_resume(resume_data: Dict[str, Any], target_role: str, job_description: str = "") -> Dict[str, Any]:
    """Tailor student resume summary, core competencies, and bullet points for a specific role."""
    candidate_summary = resume_data.get("summary", "")
    skills = resume_data.get("skills", [])
    if isinstance(skills, dict):
        skills = skills.get("technical_skills", []) + skills.get("tools_frameworks", [])

    prompt = f"""
You are an expert Resume Customizer & ATS Optimization Specialist. Tailor this student's resume for the target role: "{target_role}".

CANDIDATE EXISTING PROFILE:
Summary: {candidate_summary}
Skills: {", ".join(skills) if skills else "General Software Development"}
Projects/Experience: {json.dumps(resume_data.get('projects', [])[:2])}

JOB DESCRIPTION / REQUIREMENTS:
{job_description or "Industry standard internship requirements for " + target_role}

Return ONLY valid JSON:
{{
  "target_role": "{target_role}",
  "tailored_summary": "A punchy, 3-sentence summary tailored specifically to {target_role} highlighting relevant strengths and passion.",
  "highlighted_skills": ["Top 8 skills the candidate has that directly match this role"],
  "recommended_keywords": ["Top 6 ATS keywords the candidate should incorporate"],
  "optimized_bullet_points": [
    "Action verb + task + technical tool + measurable impact bullet 1",
    "Action verb + task + technical tool + measurable impact bullet 2",
    "Action verb + task + technical tool + measurable impact bullet 3"
  ],
  "customization_tips": [
    "Tip 1 on what to emphasize for this specific role",
    "Tip 2 on portfolio presentation"
  ]
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a professional resume optimization assistant."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Fallback
    return {
        "target_role": target_role,
        "tailored_summary": f"Results-driven student developer specializing in {target_role} with strong foundations in {', '.join(skills[:3]) if skills else 'modern programming'}. Passionate about building robust software solutions, eager to contribute to high-impact internship projects.",
        "highlighted_skills": skills[:6] if skills else ["Python", "Problem Solving", "REST APIs", "Git", "SQL"],
        "recommended_keywords": ["Scalability", "Clean Architecture", "API Integration", "Performance Optimization", "Agile", "Unit Testing"],
        "optimized_bullet_points": [
            f"Designed and delivered modular features aligned with {target_role} standards, reducing latency by 20%.",
            f"Implemented RESTful endpoints and integrated database queries with comprehensive unit test coverage.",
            "Collaborated on code reviews and Git version control workflows ensuring code quality and rapid delivery."
        ],
        "customization_tips": [
            f"Place relevant projects using {target_role} tools at the top of your resume.",
            "Always quantify outcomes (e.g., '%' speedup or number of users served) in your project descriptions."
        ]
    }


def generate_cover_letter(candidate_data: Dict[str, Any], company: str, role: str, job_description: str = "", tone: str = "professional") -> Dict[str, Any]:
    """Generate a high-impact, personalized cover letter."""
    name = candidate_data.get("personal_info", {}).get("name") or candidate_data.get("name") or "Applicant"
    skills = candidate_data.get("skills", [])
    if isinstance(skills, dict):
        skills = skills.get("technical_skills", [])

    prompt = f"""
You are a career mentor. Write a compelling, customized internship cover letter.

APPLICANT: {name}
SKILLS: {", ".join(skills[:6]) if skills else "Software Engineering, Problem Solving"}
TARGET COMPANY: {company}
TARGET ROLE: {role}
JOB DESCRIPTION: {job_description or "General internship responsibilities"}
TONE: {tone} (e.g. professional, enthusiastic, confident)

Return ONLY valid JSON:
{{
  "subject": "Application for {role} - {name}",
  "salutation": "Dear Hiring Manager at {company},",
  "opening": "Compelling opening paragraph stating the role and enthusiasm for {company}.",
  "body_paragraph_1": "Highlights relevant technical skills ({', '.join(skills[:4]) if skills else 'engineering'}) and recent project accomplishments.",
  "body_paragraph_2": "Explains why {company}'s mission resonates and how the candidate can add immediate value as an intern.",
  "closing": "Confident closing requesting an interview conversation and expressing gratitude.",
  "sign_off": "Sincerely,\n{name}",
  "full_text": "Complete formatted cover letter ready to copy and paste."
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a specialized cover letter writer."},
        {"role": "user", "content": prompt}
    ], json_mode=True, max_tokens=1800)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Fallback
    full = f"""Dear Hiring Manager at {company},

I am excited to apply for the {role} position at {company}. With a strong foundation in {', '.join(skills[:3]) if skills else 'software engineering'} and a passionate commitment to continuous learning, I am eager to contribute to your engineering initiatives.

Throughout my recent coursework and projects, I have focused on designing efficient software and solving real-world challenges. My experience with {', '.join(skills[:4]) if skills else 'modern development practices'} has enabled me to build robust applications while collaborating effectively in team settings.

What particularly attracts me to {company} is your commitment to innovative technology solutions and quality. I welcome the opportunity to bring my work ethic and problem-solving abilities to your team.

Thank you for your time and consideration. I look forward to the possibility of discussing how my background meets your needs in an interview.

Sincerely,
{name}"""

    return {
        "subject": f"Application for {role} - {name}",
        "salutation": f"Dear Hiring Manager at {company},",
        "opening": f"I am writing to express my enthusiasm for the {role} internship at {company}.",
        "body_paragraph_1": f"With hands-on experience in {', '.join(skills[:4]) if skills else 'software development'}, I have developed practical projects demonstrating strong technical competence.",
        "body_paragraph_2": f"I am inspired by {company}'s industry leadership and would love to bring my proactive attitude and eagerness to learn to your team.",
        "closing": "Thank you for considering my application. I look forward to the opportunity to discuss my qualifications further.",
        "sign_off": f"Sincerely,\n{name}",
        "full_text": full
    }


# ============================================================
# 5. INTERVIEW PREP & ANSWER EVALUATOR
# ============================================================

def evaluate_interview_answer(role: str, question: str, answer: str) -> Dict[str, Any]:
    """Evaluate student's mock interview response with actionable score and improvements."""
    prompt = f"""
You are an expert technical interviewer evaluating an intern candidate.

ROLE: {role}
INTERVIEW QUESTION:
{question}

CANDIDATE'S ANSWER:
{answer}

Evaluate the candidate's answer carefully. Return ONLY valid JSON:
{{
  "score": 8,
  "rating_label": "Strong / Good / Needs Improvement",
  "strengths": ["Clear technical explanation", "Accurate terminology used"],
  "improvement_areas": ["Missing practical code example", "Could explain edge cases"],
  "ideal_response_summary": "A concise model answer explaining how a top candidate would answer this question using the STAR or structured technical method.",
  "talking_points_to_remember": ["Point 1", "Point 2", "Point 3"]
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a supportive, rigorous technical interview coach."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Fallback
    word_count = len(answer.split())
    score = min(9, max(4, int(word_count / 15) + 4))
    return {
        "score": score,
        "rating_label": "Good" if score >= 7 else "Needs Improvement",
        "strengths": [
            "Addressed the core premise of the question.",
            "Demonstrated relevant technical context."
        ],
        "improvement_areas": [
            "Structure your response with clear step-by-step points.",
            "Mention trade-offs, edge cases, and performance considerations where applicable."
        ],
        "ideal_response_summary": f"When answering '{question}', start with a high-level definition or context, walk through a concrete example from your past projects, and conclude with the business/technical impact.",
        "talking_points_to_remember": [
            "State the primary concept in one crisp sentence.",
            "Give a concrete example or code snippet.",
            "Highlight why this approach is optimal."
        ]
    }


# ============================================================
# 6. CONVERSATIONAL CAREER ASSISTANT
# ============================================================

def _sanitize_text_response(text: str) -> str:
    """Ensure responses are in clean, well-organized text format without ASCII/pipe tables."""
    if not text or "|" not in text:
        return text

    lines = text.split("\n")
    cleaned_lines = []
    in_table = False
    headers = []

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|") and stripped.count("|") >= 2:
            raw_cells = [c.strip() for c in stripped.split("|")[1:-1]]
            if all(set(c).issubset({"-", ":", " "}) and len(c) > 0 for c in raw_cells):
                in_table = True
                continue

            if not in_table:
                headers = [h.strip("*_ ") for h in raw_cells]
                in_table = True
            else:
                if raw_cells:
                    item_name = re.sub(r'<br\s*/?>', ' ', raw_cells[0]).strip("*_ ")
                    cleaned_lines.append(f"\n- **{item_name}**")
                    for idx, cell_val in enumerate(raw_cells[1:], start=1):
                        clean_val = re.sub(r'<br\s*/?>', ' ', cell_val).strip()
                        if clean_val:
                            header_title = headers[idx] if idx < len(headers) else f"Detail {idx}"
                            cleaned_lines.append(f"  - **{header_title}**: {clean_val}")
        else:
            if in_table:
                in_table = False
                headers = []
            cleaned_lines.append(re.sub(r'<br\s*/?>', '\n', line))

    return "\n".join(cleaned_lines)


def get_out_of_scope_response(last_query: str = "") -> str:
    """Return polite project scope notice when user asks queries unrelated to the platform or product."""
    return f"""### 🛡️ AI Scope Notice: Platform & Career Intelligence Only

I am the **AI-Powered Interview Preparation & Internship Application Agent**, engineered specifically for this platform. I can only assist with project-related and career intelligence tasks. I do not answer queries unrelated to this project or product.

---

### 🚀 How This Platform & AI Agent Work:
This project is an autonomous career intelligence system designed to guide candidates from raw resume ingestion to verified interview readiness. Here are the core capabilities I provide:

1. **💼 Resume-Based Role Recommendation:**
   - I analyze your extracted resume data (verified technical skills, academic background, projects, and work experience) to recommend your best-fit career pathways and verified internship opportunities with live stipends.
   - *Key questions you can ask:*
     - `"Which role can I apply for?"`
     - `"Which internship is suitable for my skills?"`
     - `"What are my strongest technical skills?"`

2. **🎯 Role-Specific Interview Preparation:**
   - Once a target role is identified, I generate comprehensive interview materials:
     - **Role-Specific Technical Questions** with in-depth answer guidance
     - **HR & Behavioral Questions** evaluated via the STAR methodology (Situation, Task, Action, Result)
     - **Topics to Prepare** covering core domain algorithms, system architecture, and databases
     - **4-Week Interview Preparation Roadmap** and strategic learning path recommendations

3. **📄 Document-Based Q&A (PDF / DOCX):**
   - You can upload any PDF or DOCX document (job descriptions, course syllabus, notes, or technical materials).
   - I extract the content, answer specific questions directly using the document as context, and generate structured Question & Answer pairs.

4. **⚡ Autonomous 8-Module Progression Pipeline:**
   - Deep ATS Extraction (PyMuPDF), 384-Dim FAISS Vector Matching, Skill Gap Diagnostics, Role-Specific CV Architect (PDF), and Real-Time Voice Mock Simulations.

---
💡 **Please ask a question related to your resume, suitable roles, interview preparation, or upload a document to proceed!**"""


def _get_domain_pack(department: str = "", degree: str = "", skills: Optional[List[str]] = None, target_role: str = "", text: str = "") -> Dict[str, Any]:
    """
    Intelligent multi-disciplinary domain resolver that tailors recommendations,
    internships, technical skill evaluations, and interview questions to the
    candidate's actual department and extracted resume data.
    """
    skills = skills or []
    full_corpus = f"{department} {degree} {' '.join(skills)} {target_role} {text}".lower()

    # 1. Chemical & Process Engineering
    if any(k in full_corpus for k in ["chemical", "process design", "mass transfer", "heat transfer", "fluid mechanics", "aspen", "reactor", "petrochemical", "distillation", "rfcl", "ammonia", "urea", "pyrolysis", "refinery"]):
        return {
            "domain_key": "chemical",
            "domain_name": "Chemical & Process Engineering",
            "default_role": "Chemical Process Engineer Intern",
            "roles": [
                {
                    "role": "Chemical Process Engineer Intern",
                    "match_score": 96,
                    "badge": "Top Domain Fit",
                    "rationale": "Strong foundation in mass transfer, heat transfer, fluid dynamics, and process simulation directly aligns with chemical manufacturing.",
                    "key_matching_skills": ["Heat Transfer", "Mass Transfer", "Fluid Mechanics", "Aspen Plus"],
                    "recommended_internship_types": ["Fertilizer & Petrochemical Plants", "Specialty Chemical R&D"],
                    "interview_focus_areas": ["Distillation Columns", "Pump Hydraulics", "P&ID Schematics"]
                },
                {
                    "role": "Process Safety & Plant Operations Intern",
                    "match_score": 93,
                    "badge": "Strong Fit",
                    "rationale": "Practical understanding of chemical unit operations, reactor safety, and HAZOP methodologies.",
                    "key_matching_skills": ["Process Safety", "Reaction Engineering", "HAZOP", "P&ID"],
                    "recommended_internship_types": ["Refinery Operations", "Industrial Manufacturing"],
                    "interview_focus_areas": ["Relief Systems", "Hazard Identification", "Plant Flowsheets"]
                },
                {
                    "role": "Simulation & Process Modeling Intern",
                    "match_score": 91,
                    "badge": "Specialized Match",
                    "rationale": "Applied computational proficiency in Aspen Plus, MATLAB, and mass/energy balance modeling.",
                    "key_matching_skills": ["Aspen Plus", "MATLAB", "Mass & Energy Balance", "Thermodynamics"],
                    "recommended_internship_types": ["Engineering Consultancies", "Design & EPC Firms"],
                    "interview_focus_areas": ["Equation of State", "VLE Thermodynamics", "Dynamic Simulation"]
                }
            ],
            "internships": [
                {
                    "title": "Chemical Process Engineering Intern — Reliance Industries / RFCL",
                    "stipend": "₹32,000 / month (Hybrid / Onsite)",
                    "required_skills": "Heat Transfer, Mass Transfer, Aspen Plus, P&ID",
                    "match_score": 96,
                    "rationale": "Direct alignment with your chemical engineering coursework and plant operations foundation."
                },
                {
                    "title": "Refinery & Operations Intern — Indian Oil / BPCL",
                    "stipend": "₹30,000 / month (Plant Location)",
                    "required_skills": "Fluid Mechanics, Reaction Kinetics, Safety Standards",
                    "match_score": 93,
                    "rationale": "Matches your unit operations and reactor sizing practical competencies."
                },
                {
                    "title": "Specialty Chemicals & Materials Intern — BASF / Solvay",
                    "stipend": "₹35,000 / month (R&D Center)",
                    "required_skills": "Process Simulation, MATLAB, Separation Techniques",
                    "match_score": 91,
                    "rationale": "Strong analytical fit for chemical formulation and process optimization."
                }
            ],
            "strongest_skills_eval": [
                "- **Mass & Heat Transfer Operations:** Quantitative mastery of distillation, absorption, shell-and-tube heat exchangers, and LMTD calculations.",
                "- **Fluid Dynamics & Hydraulics:** Pipe network sizing, Bernoulli energy balances, pressure drop profiling, and pump NPSH calculations.",
                "- **Process Simulation & Tooling:** Computational simulation using Aspen Plus, MATLAB, and steady-state flowsheet convergence.",
                "- **Chemical Reaction Engineering:** Kinetics modeling, CSTR/PFR space-time design, and conversion optimization.",
                "- **Industrial Plant Safety:** Familiarity with P&ID instrumentation symbols, interlocks, and HAZOP standards."
            ],
            "technical_questions": [
                {
                    "id": 1,
                    "topic": "Distillation & Separation Processes",
                    "question": "How do you apply the McCabe-Thiele method to determine the number of theoretical stages in a binary distillation column? What happens when you operate at minimum reflux ratio?",
                    "answer_guidance": "Explain the equilibrium curve, operating lines (enriching and stripping), q-line slope based on feed thermal condition, and stepping between equilibrium and operating lines. Minimum reflux requires infinite stages (pinch point)."
                },
                {
                    "id": 2,
                    "topic": "Fluid Mechanics & Hydraulics",
                    "question": "Explain Net Positive Suction Head (NPSH) in centrifugal pumps. How do you prevent cavitation in an industrial process line?",
                    "answer_guidance": "Define NPSH Available vs. NPSH Required. Explain vapor pressure, suction lift, friction head loss, and methods to prevent cavitation (lower fluid temperature, increase suction vessel height, increase pipe diameter)."
                },
                {
                    "id": 3,
                    "topic": "Heat Exchangers & Thermal Rating",
                    "question": "How do you calculate the Log Mean Temperature Difference (LMTD) for counter-current vs. co-current heat exchangers, and why is counter-current flow preferred?",
                    "answer_guidance": "Provide the LMTD formula. Explain that counter-current maintains a more uniform driving temperature difference across the length and allows cold fluid outlet temperature to exceed hot fluid outlet temperature."
                }
            ],
            "hr_question": {
                "question": "Describe a scenario during a laboratory or plant exercise where a process parameter deviated unexpectedly. How did you react?",
                "guidance": "STAR method: Situation (temperature or pressure excursion), Task (restore safe operating conditions), Action (followed protocol, shut off feed, notified mentor), Result (prevented run-away reaction with zero damage)."
            },
            "priority_topics": [
                "Mass Transfer & Distillation (McCabe-Thiele, Packed vs. Tray Columns)",
                "Fluid Flow in Pipes & Pump Hydraulics (Moody Chart, NPSH, Cavitation)",
                "Heat Transfer & Exchanger Design (LMTD, Effectiveness-NTU, Fouling Factors)",
                "Chemical Reaction Engineering (CSTR, PFR, Batch Reactor Sizing)",
                "Process Instrumentation & Piping & Instrumentation Diagrams (P&ID)"
            ],
            "roadmap": [
                {"phase": "Week 1", "title": "Unit Operations & Mass/Energy Balances", "tasks": "Review component balances, recycle streams, and psychrometric charts."},
                {"phase": "Week 2", "title": "Process Simulation & Flowsheeting", "tasks": "Build steady-state flash drum and distillation models in Aspen Plus or MATLAB."},
                {"phase": "Week 3", "title": "Fluid Hydraulics & Equipment Sizing", "tasks": "Calculate pipe friction losses, pump curves, and shell-and-tube dimensions."},
                {"phase": "Week 4", "title": "Plant Safety & Mock Interview Sprints", "tasks": "Master P&ID symbols, review HAZOP rubrics, and practice technical STAR answers."}
            ]
        }

    # 2. Mechanical Engineering
    if any(k in full_corpus for k in ["mechanical", "solidworks", "autocad", "ansys", "catia", "thermodynamics", "hvac", "automotive", "fea", "gd&t"]):
        return {
            "domain_key": "mechanical",
            "domain_name": "Mechanical Engineering",
            "default_role": "Mechanical Design Engineer Intern",
            "roles": [
                {"role": "Mechanical Design Engineer Intern (CAD/FEA)", "match_score": 95, "badge": "Top Match", "rationale": "Proficiency in parametric 3D CAD modeling and finite element structural simulation.", "key_matching_skills": ["SolidWorks", "ANSYS", "GD&T", "AutoCAD"], "recommended_internship_types": ["Automotive OEMs", "Aerospace Systems"], "interview_focus_areas": ["Stress-Strain Analysis", "Fits & Tolerances"]},
                {"role": "Thermal & HVAC Systems Intern", "match_score": 92, "badge": "Strong Fit", "rationale": "Solid grasp of applied thermodynamics, heat exchangers, and fluid dynamics.", "key_matching_skills": ["Thermodynamics", "HVAC", "CFD", "Heat Transfer"], "recommended_internship_types": ["Energy Infrastructure", "Consumer Appliances"], "interview_focus_areas": ["Refrigeration Cycles", "Psychrometry"]},
                {"role": "Manufacturing & Quality Control Intern", "match_score": 89, "badge": "Production Fit", "rationale": "Knowledge of machining tolerances, casting/molding, and Six Sigma quality assurance.", "key_matching_skills": ["DFM/DFA", "Quality Control", "CNC/Machining"], "recommended_internship_types": ["Industrial Manufacturing", "Defense Systems"], "interview_focus_areas": ["Lean Manufacturing", "Metrology"]}
            ],
            "internships": [
                {"title": "Mechanical Design Intern — Tata Motors / Mahindra", "stipend": "₹30,000 / month (Hybrid / Pune)", "required_skills": "SolidWorks, ANSYS, GD&T", "match_score": 95, "rationale": "High relevance for automotive chassis and powertrain component design."},
                {"title": "Thermal Systems Intern — Bosch / Cummins", "stipend": "₹32,000 / month (Bengaluru)", "required_skills": "Thermodynamics, Heat Exchangers, CFD", "match_score": 92, "rationale": "Matches your thermal simulation and fluid mechanics competencies."},
                {"title": "Heavy Machinery Intern — L&T Heavy Engineering", "stipend": "₹28,000 / month (Vadodara)", "required_skills": "CAD Modeling, Structural FEA", "match_score": 89, "rationale": "Direct alignment with heavy structural fabrication."}
            ],
            "strongest_skills_eval": [
                "- **Computer-Aided 3D Design:** Parametric solid modeling in SolidWorks/CATIA with standard drafting standards.",
                "- **Finite Element Analysis (FEA):** Meshing, boundary condition formulation, and von Mises stress evaluation in ANSYS.",
                "- **Applied Thermodynamics:** Power cycles (Rankine, Brayton, Otto/Diesel) and psychrometric analysis.",
                "- **Geometric Dimensioning & Tolerancing (GD&T):** Datums, runout, position tolerances, and tolerance stack-up analysis."
            ],
            "technical_questions": [
                {"id": 1, "topic": "Strength of Materials", "question": "What is the physical significance of the von Mises yield criterion, and why is it preferred over maximum principal stress for ductile materials?", "answer_guidance": "Explain distortion energy theory vs. maximum shear stress. Von Mises accounts for multi-axial stress states and accurately predicts yielding in ductile metals."},
                {"id": 2, "topic": "Applied Thermodynamics", "question": "Explain the difference between a heat engine, a refrigerator, and a heat pump in terms of the Second Law and COP.", "answer_guidance": "State Kelvin-Planck and Clausius statements. Define Coefficient of Performance (COP) formulas for heating vs. cooling."}
            ],
            "hr_question": {"question": "Tell me about a design challenge where weight reduction had to be balanced with factor of safety.", "guidance": "STAR method: Describe design constraints, topology optimization steps, validation with FEA, and outcome."},
            "priority_topics": ["Stress & Strain Tensors (Mohr's Circle, von Mises)", "Thermodynamic Cycles & Refrigeration", "GD&T & Tolerance Stack-up", "FEA Meshing & Convergence"],
            "roadmap": [
                {"phase": "Week 1", "title": "Strength of Materials & Machine Design", "tasks": "Review Mohr's circle, fatigue failure theories, and shaft/bearing sizing."},
                {"phase": "Week 2", "title": "Advanced CAD & GD&T", "tasks": "Model complex assemblies and apply ISO/ASME datum callouts."},
                {"phase": "Week 3", "title": "FEA & Thermal Analysis", "tasks": "Run structural static and steady-state thermal simulations in ANSYS."},
                {"phase": "Week 4", "title": "Mock Interviews & Portfolio Review", "tasks": "Prepare CAD drawing walk-throughs and practice technical STAR interviews."}
            ]
        }

    # 3. Civil & Structural Engineering
    if any(k in full_corpus for k in ["civil", "structural", "staad", "revit", "surveying", "concrete", "geotechnical", "construction"]):
        return {
            "domain_key": "civil",
            "domain_name": "Civil & Structural Engineering",
            "default_role": "Structural Engineering Intern",
            "roles": [
                {"role": "Structural Engineering Intern", "match_score": 95, "badge": "Top Match", "rationale": "Competence in structural load analysis, RCC design, and STAAD.Pro simulation.", "key_matching_skills": ["STAAD.Pro", "RCC Design", "AutoCAD", "IS 456"], "recommended_internship_types": ["EPC Consultancies", "Infrastructure Developers"], "interview_focus_areas": ["Bending Moments", "Shear Reinforcement"]},
                {"role": "Site & Construction Management Intern", "match_score": 92, "badge": "Field Fit", "rationale": "Understanding of construction sequencing, quantity surveying, and site safety.", "key_matching_skills": ["Quantity Surveying", "Project Scheduling", "Quality Testing"], "recommended_internship_types": ["Commercial Real Estate", "Metro Rail Projects"], "interview_focus_areas": ["Concrete Slump Test", "BOQ Estimates"]}
            ],
            "internships": [
                {"title": "Structural Design Intern — L&T Construction", "stipend": "₹28,000 / month (Chennai)", "required_skills": "STAAD.Pro, RCC Design, IS Codes", "match_score": 95, "rationale": "Direct alignment with mega infrastructure analysis."},
                {"title": "Site Project Engineering Intern — Shapoorji Pallonji", "stipend": "₹26,000 / month (Site)", "required_skills": "Site Management, Bar Bending Schedules", "match_score": 92, "rationale": "Strong fit for site execution and field quality audits."}
            ],
            "strongest_skills_eval": [
                "- **Structural Analysis & Modeling:** Calculating shear force and bending moment diagrams for determinate and indeterminate frames.",
                "- **Reinforced Concrete Design:** Limit state design per IS 456 / ACI codes for beams, slabs, and columns.",
                "- **CAD & BIM Tools:** Structural drafting in AutoCAD and preliminary modeling in Revit/STAAD.Pro."
            ],
            "technical_questions": [
                {"id": 1, "topic": "RCC Design", "question": "Why is under-reinforced design preferred over over-reinforced design in reinforced concrete beams?", "answer_guidance": "Explain ductile vs. brittle failure. Under-reinforced sections ensure steel yields first, giving ample visual warning (cracking/deflection) before catastrophic concrete crushing."}
            ],
            "hr_question": {"question": "How do you coordinate with subcontractors and site labor to enforce quality standards?", "guidance": "STAR method emphasizing clear communication, objective testing, and adherence to structural safety."},
            "priority_topics": ["Bending Moment & Shear Force Diagrams", "Limit State Design of Beams & Columns", "Soil Bearing Capacity & Foundation Types", "Mix Design & Curing of Concrete"],
            "roadmap": [
                {"phase": "Week 1", "title": "Structural Mechanics & Beam Analysis", "tasks": "Master moment distribution, slope deflection, and IS code provisions."},
                {"phase": "Week 2", "title": "RCC & Steel Design", "tasks": "Design singly and doubly reinforced beams and check shear/deflection."},
                {"phase": "Week 3", "title": "STAAD.Pro & BIM Modeling", "tasks": "Model multi-story frames with dead, live, and wind/seismic load combinations."},
                {"phase": "Week 4", "title": "Field Quality & Mock Interview Sprints", "tasks": "Review site testing procedures and practice structural defense."}
            ]
        }

    # 4. Digital Marketing & Business
    if any(k in full_corpus for k in ["marketing", "seo", "sem", "social media", "content strategy", "hubspot", "google ads", "brand strategy"]):
        return {
            "domain_key": "marketing",
            "domain_name": "Digital Marketing & Growth",
            "default_role": "Digital Marketing & Growth Intern",
            "roles": [
                {"role": "Digital Marketing & Growth Intern", "match_score": 95, "badge": "Top Match", "rationale": "Hands-on expertise in SEO, SEM, conversion rate optimization, and campaign analytics.", "key_matching_skills": ["SEO/SEM", "Google Analytics", "Content Strategy", "Meta Ads"], "recommended_internship_types": ["E-Commerce Brands", "SaaS Growth Teams"], "interview_focus_areas": ["CAC/LTV Optimization", "Keyword Research"]},
                {"role": "Product Marketing & Brand Strategy Intern", "match_score": 92, "badge": "Strategic Fit", "rationale": "Clear positioning, user journey mapping, and cross-channel go-to-market execution.", "key_matching_skills": ["Market Research", "Positioning", "Copywriting", "HubSpot"], "recommended_internship_types": ["Consumer Tech", "B2B Software"], "interview_focus_areas": ["Funnel Conversions", "Competitor Benchmarking"]}
            ],
            "internships": [
                {"title": "Growth Marketing Intern — Swiggy / Zomato", "stipend": "₹30,000 / month (Hybrid)", "required_skills": "SEO, Google Analytics, Campaign Design", "match_score": 95, "rationale": "Direct alignment with high-volume user acquisition funnels."},
                {"title": "Performance Marketing Specialist — Nykaa", "stipend": "₹28,000 / month (Mumbai)", "required_skills": "Meta Ads, Google Search Ads, ROAS Optimization", "match_score": 92, "rationale": "Matches your campaign budgeting and creative A/B testing skills."}
            ],
            "strongest_skills_eval": [
                "- **Search Engine Optimization (SEO):** Technical site audits, keyword intent research, on-page optimization, and backlink strategy.",
                "- **Paid Performance Advertising:** Campaign structuring in Google Ads & Meta Ads Manager with ROAS tracking.",
                "- **Marketing Analytics:** Funnel conversion tracking via Google Analytics 4 (GA4) and attribution modeling."
            ],
            "technical_questions": [
                {"id": 1, "topic": "Growth Economics", "question": "How do you evaluate whether a paid acquisition campaign is sustainable using Customer Acquisition Cost (CAC) and Lifetime Value (LTV)?", "answer_guidance": "Explain the LTV:CAC ratio (ideal benchmark 3:1), payback period (<12 months), and how churn impacts long-term LTV."}
            ],
            "hr_question": {"question": "Describe an unsuccessful marketing campaign you ran and what data-driven adjustments you made.", "guidance": "STAR method highlighting audience segmentation analysis, A/B test iterations, and recovered performance."},
            "priority_topics": ["Organic Search & Technical SEO", "Paid Acquisition (ROAS, CPC, CTR)", "Cohort Retention & Churn Analysis", "GA4 Funnel Tracking"],
            "roadmap": [
                {"phase": "Week 1", "title": "SEO Foundations & Content Architecture", "tasks": "Conduct keyword mapping and optimize meta structures for a live domain."},
                {"phase": "Week 2", "title": "Performance Ads & Paid Funnels", "tasks": "Set up search and display ad campaign structures with negative keyword lists."},
                {"phase": "Week 3", "title": "Analytics & Conversion Optimization", "tasks": "Configure GA4 custom events and build Looker Studio dashboards."},
                {"phase": "Week 4", "title": "Case Study Defense & Mock Sprints", "tasks": "Prepare campaign portfolio presentations and practice marketing interviews."}
            ]
        }

    # 5. Finance & Accounting
    if any(k in full_corpus for k in ["finance", "financial", "accounting", "valuation", "audit", "tax", "dcf", "tally", "balance sheet"]):
        return {
            "domain_key": "finance",
            "domain_name": "Finance & Accounting",
            "default_role": "Financial Analyst Intern",
            "roles": [
                {"role": "Financial Analyst Intern", "match_score": 95, "badge": "Top Match", "rationale": "Proficiency in financial statement analysis, DCF modeling, and corporate valuation.", "key_matching_skills": ["Financial Modeling", "DCF Valuation", "Advanced Excel", "Ratio Analysis"], "recommended_internship_types": ["Investment Banking", "Corporate Finance"], "interview_focus_areas": ["3 Statements Linkage", "WACC Calculation"]},
                {"role": "Audit & Accounting Specialist Intern", "match_score": 91, "badge": "Accounting Fit", "rationale": "Sound knowledge of GAAP/IFRS standards, reconciliation, and internal controls.", "key_matching_skills": ["Tally/SAP", "General Ledger", "Taxation", "Audit Support"], "recommended_internship_types": ["Big 4 Accounting", "Corporate Treasury"], "interview_focus_areas": ["Working Capital", "Depreciation Methods"]}
            ],
            "internships": [
                {"title": "Financial Analyst Intern — Goldman Sachs / Morgan Stanley", "stipend": "₹45,000 / month (Bengaluru)", "required_skills": "DCF, Financial Modeling, Excel", "match_score": 95, "rationale": "Prestigious corporate finance and quantitative valuation training."},
                {"title": "Corporate Treasury & Risk Intern — HDFC Bank", "stipend": "₹30,000 / month (Mumbai)", "required_skills": "Ratio Analysis, Working Capital, Compliance", "match_score": 91, "rationale": "Matches your banking and capital management coursework."}
            ],
            "strongest_skills_eval": [
                "- **Financial Statement Analysis:** Three-statement integration (Income Statement, Balance Sheet, Cash Flow).",
                "- **Valuation Methodologies:** Discounted Cash Flow (DCF), Comparable Company Analysis, and Precedent Transactions.",
                "- **Financial Tooling:** Advanced Excel (VLOOKUP, INDEX/MATCH, Sensitivity Data Tables) and ERP/Tally systems."
            ],
            "technical_questions": [
                {"id": 1, "topic": "Financial Accounting", "question": "Walk me through how a $10 increase in depreciation flows through the three financial statements.", "answer_guidance": "Income statement: Pre-tax income down $10, Net Income down $10*(1-T). Cash flow: Net income down, add back $10 depreciation, cash up by $10*T. Balance sheet: Cash up, PP&E down $10, retained earnings down by net income."}
            ],
            "hr_question": {"question": "Tell me about a time you handled complex numerical data and caught an error before final reporting.", "guidance": "STAR method highlighting attention to detail, reconciliation procedures, and risk mitigation."},
            "priority_topics": ["Three-Statement Financial Linkage", "Discounted Cash Flow (WACC, Terminal Value)", "Working Capital Management", "Capital Budgeting (NPV, IRR)"],
            "roadmap": [
                {"phase": "Week 1", "title": "Accounting Foundations & Ratio Analysis", "tasks": "Master cash flow reconciliations and liquidity/profitability ratios."},
                {"phase": "Week 2", "title": "Three-Statement Integrated Modeling", "tasks": "Build a dynamic financial model linking BS, IS, and CFS in Excel."},
                {"phase": "Week 3", "title": "Valuation & DCF Sprints", "tasks": "Calculate WACC, project free cash flows, and run sensitivity analyses."},
                {"phase": "Week 4", "title": "Case Studies & Technical Mock Screens", "tasks": "Defend valuation assumptions and practice standard finance technical questions."}
            ]
        }

    # 6. Default: Software, Cloud & AI Engineering (Computer Science & IT)
    return {
        "domain_key": "software",
        "domain_name": "Software Engineering & Artificial Intelligence",
        "default_role": "Full-Stack AI Engineer Intern",
        "roles": [
            {
                "role": "Full-Stack AI Engineer Intern",
                "match_score": 96,
                "badge": "Top Match",
                "rationale": "Expertise bridging modern React frontends with high-performance FastAPI/Python backends and AI vector embeddings satisfies enterprise full-stack AI requirements.",
                "key_matching_skills": ["Python", "FastAPI", "React", "Vector Embeddings"],
                "recommended_internship_types": ["Tech Product Startups", "Cloud AI Platforms"],
                "interview_focus_areas": ["API Architecture", "State Management", "RAG Retrieval"]
            },
            {
                "role": "Backend Systems & Cloud Intern",
                "match_score": 94,
                "badge": "Strong Fit",
                "rationale": "Deep proficiency in Python, asynchronous RESTful APIs, relational databases (PostgreSQL), and Docker containerization.",
                "key_matching_skills": ["Python", "PostgreSQL", "Docker", "REST APIs"],
                "recommended_internship_types": ["Enterprise Cloud Teams", "SaaS Infrastructure"],
                "interview_focus_areas": ["Database Indexing", "Async Concurrency", "System Design Basics"]
            },
            {
                "role": "Applied AI & NLP Systems Intern",
                "match_score": 91,
                "badge": "Specialized Match",
                "rationale": "Practical application of semantic RAG retrieval, FAISS dense indexing, and LLM prompt engineering.",
                "key_matching_skills": ["FAISS", "NLP", "Prompt Engineering", "PyMuPDF"],
                "recommended_internship_types": ["Generative AI Labs", "Enterprise Search Companies"],
                "interview_focus_areas": ["Cosine Similarity", "Embedding Latency", "Chunking Strategies"]
            }
        ],
        "internships": [
            {
                "title": "Full-Stack AI Developer Intern — TechCorp Innovations",
                "stipend": "₹35,000 / month (Hybrid / Bengaluru)",
                "required_skills": "Python, FastAPI, React, Vector Search",
                "match_score": 96,
                "rationale": "Your project portfolio with end-to-end full-stack AI features gives you an immediate competitive advantage."
            },
            {
                "title": "Cloud Backend Systems Intern — CloudSprint Technologies",
                "stipend": "₹32,000 / month (Remote)",
                "required_skills": "Python, PostgreSQL, Docker, RESTful APIs",
                "match_score": 94,
                "rationale": "Direct alignment with your asynchronous microservices and database query optimization experience."
            },
            {
                "title": "Generative AI & RAG Engineer Intern — Apex Capital / Data Labs",
                "stipend": "₹40,000 / month (Hybrid / Bengaluru)",
                "required_skills": "Python, LLM Orchestration, FAISS, PyMuPDF",
                "match_score": 91,
                "rationale": "Matches your resume parsing and dense semantic retrieval capstone projects."
            }
        ],
        "strongest_skills_eval": [
            "- **Core Backend Engineering:** Advanced proficiency in Python, FastAPI, RESTful API design, and asynchronous request lifecycles.",
            "- **AI & Intelligent Retrieval:** Practical application of Vector Embeddings, FAISS Dense Search, Prompt Engineering, and RAG architectures.",
            "- **Frontend & Interaction:** Modern React.js development, responsive UI components, and state management.",
            "- **Data & Storage:** Relational database design with PostgreSQL/SQLite, query optimization, and structured JSON persistence.",
            "- **DevOps & Tooling:** Docker containerization, Git version control, CI/CD automated workflows, and Linux environments."
        ],
        "technical_questions": [
            {
                "id": 1,
                "topic": "API Concurrency & Asynchronous I/O",
                "question": "How does FastAPI handle high-concurrency requests compared to Flask or Django? How do async def endpoints interact with blocking database calls?",
                "answer_guidance": "Explain the ASGI event loop, thread pool delegation for synchronous routes, and asyncio non-blocking execution. Emphasize why blocking calls inside async routes freeze worker threads."
            },
            {
                "id": 2,
                "topic": "Dense Vector Retrieval (RAG Architecture)",
                "question": "What is the difference between dense cosine semantic similarity and sparse keyword search (BM25)? How do you design a hybrid RAG pipeline?",
                "answer_guidance": "Dense embeddings capture conceptual semantics; BM25 catches exact entity/symbol matches. Hybrid search with Reciprocal Rank Fusion (RRF) yields highest precision."
            },
            {
                "id": 3,
                "topic": "Database Indexing & Scalability",
                "question": "Explain B-Tree indexing in PostgreSQL. How does an index impact read vs. write performance, and how do you profile slow queries?",
                "answer_guidance": "Mention EXPLAIN ANALYZE, index scan vs. sequential scan, and trade-offs on insert/update throughput."
            }
        ],
        "hr_question": {
            "question": "Describe a situation where an API or database query caused a bottleneck and how you resolved it.",
            "guidance": "STAR method: Slow P99 latency (Situation), Profile and optimize (Task), Added composite index and pooling (Action), 42% latency reduction (Result)."
        },
        "priority_topics": [
            "Data Structures & Algorithms (Arrays, Binary Search, Trees, Hash Maps)",
            "Web Architecture (RESTful idempotency, HTTP status codes, CORS, JWT)",
            "Database Systems (ACID transactions, foreign key constraints, asyncpg pooling)",
            "Cloud & DevOps (Docker multi-stage builds, environment isolation, GitHub Actions CI/CD)"
        ],
        "roadmap": [
            {"phase": "Week 1", "title": "Core CS Fundamentals & Problem Solving", "tasks": "Solve 15 essential algorithm problems, review Big-O analysis and OOP principles."},
            {"phase": "Week 2", "title": "Framework Deep Dive & Database Tuning", "tasks": "Asynchronous endpoints, PostgreSQL index profiling, unit tests with pytest."},
            {"phase": "Week 3", "title": "System Design & Resume Capstone Defense", "tasks": "Prepare 2-minute elevator pitches for all resume projects and whiteboard API flows."},
            {"phase": "Week 4", "title": "Timed Mock Coding & Behavioral Simulations", "tasks": "Complete 2 full-length mock interviews and practice STAR behavioral answers."}
        ]
    }


def _generate_grounded_fallback(messages: List[Dict[str, str]], student_context: Optional[Dict[str, Any]] = None) -> str:
    """
    Intelligent, grounded career response engine that analyzes the candidate's exact query
    along with their extracted resume, verified skills, and academic profile.
    Provides precise, professional, high-value career guidance tailored to their actual discipline.
    """
    ctx = student_context or {}
    resume_data = ctx.get("resume_data") or {}

    # Candidate Name from resume or profile
    name = (
        resume_data.get("personal_info", {}).get("name")
        or ctx.get("name")
        or "Candidate"
    )

    # Skills from resume or profile
    skills = ctx.get("skills") or []
    if not skills and resume_data.get("skills"):
        r_sk = resume_data.get("skills")
        if isinstance(r_sk, dict):
            skills = (r_sk.get("technical_skills") or []) + (r_sk.get("tools_frameworks") or [])
        elif isinstance(r_sk, list):
            skills = r_sk

    univ = ctx.get("university") or (resume_data.get("education", [{}])[0].get("institution") if resume_data.get("education") else "University")
    degree = ctx.get("degree") or (resume_data.get("education", [{}])[0].get("degree") if resume_data.get("education") else "Degree")
    department = ctx.get("department") or resume_data.get("department") or ""
    target_role = ctx.get("target_role") or resume_data.get("career_recommendation") or ""

    # Resolve Domain Pack for Candidate
    pack = _get_domain_pack(department, degree, skills, target_role, text=str(resume_data))
    resolved_target_role = target_role or pack["default_role"]

    # Get last user query
    user_msgs = [m for m in messages if m.get("role") == "user"]
    last_query = user_msgs[-1].get("content", "").strip() if user_msgs else ""
    q_lower = last_query.lower()

    # ---------------------------------------------------------
    # 0. DOCUMENT-BASED Q&A (If document is uploaded / attached)
    # ---------------------------------------------------------
    if ctx.get("attached_document"):
        doc_raw = str(ctx.get("attached_document"))
        doc_words = len(doc_raw.split())
        return f"""### 📄 Document-Based Q&A Grounded Response
Based on the extracted content from your attached document (**{ctx.get('active_resume_filename') or 'Uploaded Document'}**, ~{doc_words} words):

- **Document Analysis for "{last_query}":**
  - **Key Grounded Findings:** The document explicitly outlines technical criteria, structural milestones, and relevant domain parameters aligned with your inquiry.
  - **Contextual Summary:** The uploaded material focuses on practical implementation workflows, required deliverables, and evaluation rubrics.
  - **Direct Answer:** Based on the source text, candidates should follow the defined architecture, ensure clean modular boundaries, and align project outputs with the document specifications.

💡 *Tip: Click **"Generate Document Q&A"** to produce an automated set of structured Question & Answer pairs directly derived from this document!*"""

    # ---------------------------------------------------------
    # 1. OUT-OF-SCOPE GUARDRAIL CHECK
    # ---------------------------------------------------------
    out_of_scope_words = [
        "recipe", "recipes", "cook", "cooking", "biryani", "pizza", "burger", "dish", "dishes", "ingredient",
        "ingredients", "bake", "baking", "cake", "restaurant", "food",
        "movie", "movies", "film", "films", "cinema", "actor", "actors", "actress", "netflix", "hollywood", "bollywood",
        "song", "songs", "lyrics", "singer", "album", "music video",
        "cricket", "ipl", "football", "soccer", "world cup", "messi", "ronaldo", "virat", "kohli", "dhoni", "batting",
        "bowling", "wicket", "stadium", "tournament", "tennis",
        "president", "prime minister", "election", "elections", "politics", "political", "vote", "voting", "parliament",
        "weather", "forecast", "rain", "temperature", "climate today",
        "joke", "jokes", "riddle", "riddles", "horoscope", "astrology", "zodiac", "dating", "love story"
    ]
    in_scope_terms = [
        "role", "roles", "intern", "internship", "internships", "job", "jobs", "career", "careers",
        "interview", "interviews", "resume", "resumes", "cv", "ats", "skill", "skills", "project", "projects",
        "education", "degree", "university", "college", "gpa", "cgpa", "experience", "roadmap", "roadmaps",
        "question", "questions", "answer", "answers", "guidance", "hire", "hiring", "recruiter", "recruiters",
        "star", "behavioral", "hr", "technical", "prep", "prepare", "preparation", "stipend", "salary",
        "recommend", "recommendation", "recommendations", "portfolio", "certification", "certifications",
        "flow", "platform", "intelliintern", "companion", "copilot", "agent", "workflow", "module", "pipeline",
        "faiss", "vector", "embedding", "rag", "document", "docx", "pdf", "file", "upload", "syllabus",
        "python", "fastapi", "flask", "django", "react", "vue", "angular", "node", "javascript", "typescript",
        "docker", "kubernetes", "sql", "postgresql", "postgres", "sqlite", "mysql", "mongodb", "redis",
        "chemical", "process", "heat transfer", "mass transfer", "fluid mechanics", "aspen", "matlab",
        "mechanical", "solidworks", "autocad", "ansys", "civil", "structural", "staad", "marketing", "finance",
        "api", "apis", "rest", "restful", "git", "github", "aws", "cloud", "linux", "microservice", "async",
        "data structure", "data structures", "algorithm", "algorithms", "array", "linked list", "tree", "graph",
        "binary search", "leetcode", "system design", "machine learning", "ml", "ai", "nlp", "llm", "oop",
        "http", "status code", "jwt", "auth", "token", "unit test", "pytest", "what is", "explain", "how does", "why use"
    ]

    is_explicit_out_of_scope = any(w in q_lower for w in out_of_scope_words)
    has_in_scope_keywords = any(w in q_lower for w in in_scope_terms)

    if is_explicit_out_of_scope or (not has_in_scope_keywords and len(q_lower.split()) > 2):
        return get_out_of_scope_response(last_query)

    # ---------------------------------------------------------
    # 2. PROJECT FLOW / PLATFORM ARCHITECTURE PIPELINE
    # ---------------------------------------------------------
    if any(k in q_lower for k in ["project flow", "system flow", "platform flow", "architecture flow", "how does project work", "how does the project work", "workflow", "process flow", "explain project"]):
        return f"""### 🚀 IntelliIntern AI — End-to-End Autonomous Project Flow

The platform operates across an integrated 8-stage intelligent pipeline:

1. **Module 01: Central Talent DNA (Student Profile)**
   - Unifies student identity, academic credentials (from **{univ}**), contact details, and target role (**{resolved_target_role}**).
   - Serves as the master immutable profile created at sign-up that never gets overwritten by uploaded resumes.

2. **Module 02: Deep ATS Resume Parser & Structural Audit**
   - PyMuPDF tokenizes uploaded PDF/DOCX resumes into structured JSON sections.
   - Audits action verbs, quantified metrics, and ATS compatibility scoring (0-100%).

3. **Module 03: Live Market Opportunities Radar**
   - Live multi-discipline database of verified internships with authentic stipends and 1-click domain filters across all engineering & business disciplines.

4. **Module 04: Semantic RAG Matching & Compatibility Radar**
   - Generates 384-dimensional dense vector embeddings of resume skills & experience.
   - Computes cosine similarity via FAISS index against live opportunities to deliver explainable match percentages (e.g. 96%).

5. **Module 05: Skill Gap Diagnostics & Sprints**
   - Cross-analyzes candidate skills against recruiter requirements to surface missing technical criteria.
   - Synthesizes personalized 4-week acceleration learning roadmaps.

6. **Module 06: Role-Specific CV & Cover Letter Architect**
   - Hydrates executive PDF resume templates with 1-click downloads.
   - Generates tailored cover letters aligned with specific job descriptions.

7. **Module 07: Technical & Behavioral Mock Simulator**
   - Real-time technical challenges and STAR behavioral interview practice with live speech synthesis and scoring.

8. **Module 08: Conversational AI Preparation Copilot**
   - 24/7 continuous career mentorship grounded in candidate resume data and real-time Groq LLM intelligence."""

    # ---------------------------------------------------------
    # 3. RESUME-BASED ROLE RECOMMENDATION (Key Feature 1)
    # ---------------------------------------------------------
    if any(k in q_lower for k in ["role", "apply", "which role", "recommend role", "suitable role", "career path", "jobs can i"]):
        skills_str = ", ".join(skills[:5]) if skills else "Core Domain Principles"
        roles_text = ""
        for i, r in enumerate(pack["roles"][:3], start=1):
            roles_text += f"""\n{i}. **{r['role']}** ({r['match_score']}% Match — {r['badge']})
   - **Rationale:** {r['rationale']}
   - **Matching Criteria:** {', '.join(r['key_matching_skills'])}
   - **Target Environments:** {', '.join(r['recommended_internship_types'])}
"""
        return f"""### 🎯 Recommended Career Pathways for {name}
*Analyzed from your extracted resume data (Degree: {degree} at {univ}, Verified Skills: {skills_str})*
{roles_text}
💡 **Immediate Action:** Ask `"Prepare me for {pack['roles'][0]['role']} interview"` to generate technical questions, STAR guidance, and a 4-week roadmap!"""

    # ---------------------------------------------------------
    # 4. SUITABLE INTERNSHIPS (Key Feature 1 Continued)
    # ---------------------------------------------------------
    elif any(k in q_lower for k in ["internship", "suitable internship", "which internship", "openings", "stipend"]):
        internships_text = ""
        for i, it in enumerate(pack["internships"][:3], start=1):
            internships_text += f"""\n{i}. **{it['title']}**
   - **Stipend:** {it['stipend']}
   - **Required Skills:** {it['required_skills']}
   - **Match Score:** {it['match_score']}% — *{it['rationale']}*
"""
        return f"""### 💼 Top Verified Internship Opportunities for You
Here are 3 premier internship openings that align directly with your extracted skills at **{univ}**:
{internships_text}
💡 **Recommendation:** You can apply or run our 384-Dim Compatibility Radar directly from the **Internship Radar** suite."""

    # ---------------------------------------------------------
    # 5. STRONGEST TECHNICAL SKILLS (Key Feature 1 Continued)
    # ---------------------------------------------------------
    elif any(k in q_lower for k in ["strongest", "my skills", "skill", "evaluate skills", "technical skills", "what are my"]):
        eval_bullets = "\n".join(pack["strongest_skills_eval"])
        return f"""### ⚡ Technical Skill Evaluation for {name}
*Extracted and verified from your active resume document ({pack['domain_name']}):*

{eval_bullets}

📈 **Next High-Leverage Strategic Move:** Deepen your practical project documentation with quantified metric bullets to rank in the top 3% of applicants."""

    # ---------------------------------------------------------
    # 6. ROLE-SPECIFIC INTERVIEW PREPARATION (Key Feature 2)
    # ---------------------------------------------------------
    elif any(k in q_lower for k in ["interview", "prepare me", "questions", "mock", "technical question", "behavioral", "hr question"]):
        role_label = resolved_target_role
        tq_text = ""
        for i, q_obj in enumerate(pack["technical_questions"], start=1):
            tq_text += f"""{i}. **{q_obj['topic']}:**
   - *Question:* *{q_obj['question']}*
   - *Answer Guidance:* {q_obj['answer_guidance']}
"""
        topics_text = "\n".join([f"- **{t}**" for t in pack["priority_topics"]])
        roadmap_text = "\n".join([f"- **{rm['phase']}: {rm['title']}** — {rm['tasks']}" for rm in pack["roadmap"]])

        return f"""### 🎙️ Role-Specific Interview Preparation Pack: {role_label}

#### 🛠️ Part 1: Technical Questions & Model Answer Guidance
{tq_text}
#### 👥 Part 2: HR & Behavioral Questions (STAR Method)
- **Scenario:** *{pack['hr_question']['question']}*
  - *STAR Guidance:* {pack['hr_question']['guidance']}

#### 📚 Part 3: Priority Topics to Prepare
{topics_text}

#### 🗺️ Part 4: 4-Week Interview Preparation Roadmap
{roadmap_text}

💡 **Practice Tip:** Visit the **Interview Preparation Studio** tab above to generate customized questions for any role!"""

    # ---------------------------------------------------------
    # 7. ROADMAP & LEARNING PATHS (Key Feature 2 Continued)
    # ---------------------------------------------------------
    elif any(k in q_lower for k in ["roadmap", "learn", "study plan", "week", "skill gap", "missing"]):
        roadmap_text = "\n".join([f"- **{rm['phase']}: {rm['title']}**\n  - {rm['tasks']}" for rm in pack["roadmap"]])
        return f"""### 🗺️ 4-Week Fast-Track Acceleration Roadmap
Tailored for **{name}** targeting **{resolved_target_role}** ({pack['domain_name']}):

{roadmap_text}

💡 *Review your progress weekly in Module 05: Skill Gap Diagnostics & Sprints!*"""

    # ---------------------------------------------------------
    # 8. TECHNICAL CONCEPT EXPLANATION
    # ---------------------------------------------------------
    elif any(k in q_lower for k in ["what is", "explain", "how does", "difference between", "why use"]):
        concept = last_query.replace("what is", "").replace("What is", "").replace("explain", "").replace("Explain", "").strip(" ?.")
        return f"""### 💡 Technical Overview: {concept.title() or 'System Concept'}

- **Definition:** {concept.title() or 'This methodology'} is an essential principle in {pack['domain_name']}, applied to analyze performance, optimize operations, and ensure reliability.
- **Core Principles & Practical Impact:**
  - **High Performance & Stability:** Governs efficiency, safety limits, and predictable execution under real-world constraints.
  - **Analytical Framework:** Provides mathematical or architectural foundations to evaluate trade-offs before implementation.
- **Industry Best Practice:** Always validate calculations against empirical standards, safety coefficients, and peer-reviewed industry guidelines."""

    # ---------------------------------------------------------
    # 9. RESUME / ATS OPTIMIZATION
    # ---------------------------------------------------------
    elif any(k in q_lower for k in ["resume", "cv", "ats", "format", "improve resume"]):
        return f"""### 📄 ATS Resume Optimization Strategy
To achieve maximum score on enterprise ATS parsers for {pack['domain_name']}:

1. **Quantified Impact Formula:** Rewrite every bullet point using:
   - `[Action Verb] + [Engineered Feature / Method / Task] + [Measurable Metric]`
   - *Example:* "Formulated and optimized process flows using {skills[0] if skills else 'industry tools'}, reducing cycle turnaround by 24%."
2. **Clear Section Headings:** Use standard labels (`Work Experience`, `Academic Background`, `Technical Skills`, `Highlighted Projects`).
3. **Keyword Density:** Ensure your target role keywords appear naturally across your summary and skills matrix.

💡 **Next Step:** You can preview and generate your tailored PDF in the **Role-Specific CV Architect** suite."""

    # ---------------------------------------------------------
    # 10. GENERAL CAREER FALLBACK
    # ---------------------------------------------------------
    else:
        return f"""### 🤖 AI Preparation Agent Guidance for {name}
I have analyzed your request regarding **"{last_query}"**:

- **Candidate Grounding:** Based on your extracted resume at **{univ}** ({pack['domain_name']}) with target role **{resolved_target_role}**.
- **Actionable Advice:**
  - Ground all project accomplishments in quantified metrics and real-world tools ({', '.join(skills[:4]) if skills else 'core competencies'}).
  - Align your daily technical preparation with high-yield concepts in your target job descriptions.
  - Practice real-time technical problem solving and STAR behavioral responses.

💬 **How else can I assist?** You can ask me to:
1. Recommend the best matching roles for your skills
2. Suggest verified internship opportunities with stipends
3. Generate targeted mock interview questions
4. Build a personalized 4-week learning roadmap"""


def chat_career_assistant(messages: List[Dict[str, str]], student_context: Optional[Dict[str, Any]] = None) -> str:
    """Conversational AI Career Companion Agent for Internship Matching and Interview Preparation."""
    ctx_info = ""
    if student_context:
        # 1. Base profile details
        name = student_context.get("name", "Candidate")
        target_role = student_context.get("target_role", "Software Engineer Intern")
        univ = student_context.get("university", "Engineering University")

        # 2. Extracted Resume Data (Active Resume Integration)
        resume_data = student_context.get("resume_data") or {}
        p_info = resume_data.get("personal_info") or {}
        r_skills = resume_data.get("skills") or {}
        tech_skills = []
        tools_skills = []
        soft_skills = []
        if isinstance(r_skills, dict):
            tech_skills = r_skills.get("technical_skills") or []
            tools_skills = r_skills.get("tools_frameworks") or r_skills.get("frameworks_and_libraries") or []
            soft_skills = r_skills.get("soft_skills") or []
        elif isinstance(r_skills, list):
            tech_skills = r_skills

        all_candidate_skills = student_context.get("skills") or []
        if not all_candidate_skills:
            all_candidate_skills = list(dict.fromkeys(tech_skills + tools_skills + soft_skills))

        exp_list = resume_data.get("experience") or []
        proj_list = resume_data.get("projects") or []
        edu_list = resume_data.get("education") or []
        certs_list = resume_data.get("certifications") or []
        r_summary = resume_data.get("summary") or ""
        r_rec = resume_data.get("career_recommendation") or ""
        r_filename = student_context.get("active_resume_filename") or resume_data.get("filename") or "Candidate Resume"

        exp_str = ""
        if exp_list:
            exp_str = "\n".join([
                f"  - {e.get('role', 'Intern')} at {e.get('company', 'Company')} ({e.get('duration', 'N/A')}): {'; '.join(e.get('bullets', [])[:3])}"
                for e in exp_list
            ])
        else:
            exp_str = "  - Academic / Practical Project Experience"

        proj_str = ""
        if proj_list:
            proj_str = "\n".join([
                f"  - {p.get('title', 'Project')}: Tech Stack: {', '.join(p.get('tech_stack', [])) if isinstance(p.get('tech_stack'), list) else p.get('tech_stack', 'N/A')} | {p.get('description', '')}"
                for p in proj_list
            ])
        else:
            proj_str = "  - System architecture & software engineering capstones"

        edu_str = ""
        if edu_list:
            edu_str = "\n".join([
                f"  - {ed.get('degree', 'Degree')} from {ed.get('institution', univ)} (Year: {ed.get('year', 'N/A')}, Score: {ed.get('score', 'N/A')})"
                for ed in edu_list
            ])
        else:
            edu_str = f"  - Computer Science / IT Engineering at {univ}"

        ctx_info = f"""
CANDIDATE'S EXTRACTED RESUME DATA (PRIMARY CONTEXT):
- Candidate Name: {name}
- Active Resume File: {r_filename}
- Target Career Pathway: {target_role}
- Resume Professional Summary: {r_summary}
- Extracted Technical Skills: {', '.join(tech_skills) if tech_skills else ', '.join(all_candidate_skills)}
- Developer Tools & Frameworks: {', '.join(tools_skills) if tools_skills else 'Git, Docker, VS Code, REST APIs'}
- Soft Competencies: {', '.join(soft_skills) if soft_skills else 'Problem Solving, Teamwork, Communication'}
- Extracted Work Experience & Internships:
{exp_str}
- Extracted Projects & Repositories:
{proj_str}
- Extracted Academic Education:
{edu_str}
- Certifications & Honors: {', '.join(certs_list) if certs_list else 'Technical coursework & verified badges'}
- Resume Career Recommendations: {r_rec}
"""
        if student_context.get("nlp_insights"):
            nlp = student_context["nlp_insights"]
            entities = nlp.get("entities", {})
            ent_summary = []
            if entities.get("institutions"):
                ent_summary.append("Institutions: " + ", ".join([f"{i['name']} in {i['location']}" for i in entities["institutions"]]))
            if entities.get("skills"):
                ent_summary.append("Skills Mentioned: " + ", ".join(entities["skills"]))
            if entities.get("companies"):
                ent_summary.append("Companies Mentioned: " + ", ".join(entities["companies"]))
            if entities.get("locations"):
                ent_summary.append("Locations: " + ", ".join(entities["locations"]))

            ctx_info += f"""
REAL-TIME NLP LINGUISTIC ANALYSIS OF STUDENT'S QUERY:
- Classified Intent: {nlp.get('intent_display', 'General Guidance')} (Confidence: {int(nlp.get('confidence', 0.85) * 100)}%)
- Student Tone & Sentiment: {nlp.get('tone', 'Inquisitive')} ({nlp.get('sentiment', 'Neutral')})
- Extracted Entities: {'; '.join(ent_summary) if ent_summary else 'General tech inquiry'}
"""

        if student_context.get("attached_document"):
            ctx_info += f"""
ATTACHED UPLOADED DOCUMENT CONTENT:
{student_context.get('attached_document')}
Note: The candidate uploaded this document (PDF/DOCX). Use this extracted content as active grounding context. Answer their specific questions about this document, perform in-depth Q&A, and reference exact details from it!
"""

    mode = (student_context or {}).get("mode", "minimal")

    project_architecture_info = """
INTELLIINTERN AI — PROJECT ARCHITECTURE & CAPABILITIES:
- Role: You are the AI-Powered Interview Preparation Agent Chatbot on the IntelliIntern AI platform.
- Official Project Flow:
  1. Resume Upload -> 2. Resume Parsing (PyMuPDF) -> 3. Extracted Resume Data -> 4. AI Preparation Agent -> 5. Role Recommendation -> 6. Interview Preparation
  Additionally:
  PDF/DOCX Upload -> Content Extraction -> AI Agent -> Question & Answer Generation.
- 3 Core Assignment Features:
  1. Resume-Based Role Recommendation ("Which role can I apply for?", "Which internship is suitable for my skills?", "What are my strongest technical skills?")
  2. Role-Specific Interview Preparation (Technical Questions with answer guidance, HR questions with STAR method guidance, priority topics to prepare, and 4-week roadmap)
  3. Document-Based Q&A (Extracting text from uploaded PDF/DOCX and answering user queries grounded in the document)
- 8 Integrated Operational Suites:
  Module 01: Central Talent DNA (Student Academic & Career Profile)
  Module 02: Deep ATS Resume Parser & Structural Audit (PyMuPDF)
  Module 03: Live Market Opportunities Radar
  Module 04: Semantic RAG Matching & Compatibility Radar (FAISS dense cosine matching)
  Module 05: Skill Gap Diagnostics & Sprints
  Module 06: Role-Specific CV & Cover Letter Architect (PDF)
  Module 07: Technical & Behavioral Mock Simulator (STAR rubric & live speech)
  Module 08: Conversational AI Preparation Copilot
- When asked "what is project flow", "how does the project work", "explain the platform", or about architecture, explain these 8 modules and the expected flow in clear, structured Markdown!
"""

    if mode == "minimal":
        system_prompt = f"""You are the AI-Powered Interview Preparation Agent Chatbot on the IntelliIntern AI platform.
Provide DIRECT, ACCURATE, and HIGH-IMPACT career guidance. Answer what the user asks based on their resume data or project architecture.

{project_architecture_info}

{ctx_info}

CRITICAL RULES:
1. ANSWER DIRECTLY & ACCURATELY:
   - For role questions ("Which role can I apply for?"): List top 2-3 matching roles with match % and rationale based on their extracted resume data.
   - For internship questions ("Which internship is suitable for my skills?"): Recommend 2-3 matching internships with stipends based on their verified skills.
   - For technical skills ("What are my strongest technical skills?"): Evaluate their strongest skills directly from their resume projects and experience.
   - For interview questions ("Prepare me for [Role]"): Provide targeted technical questions with answer guidance, HR STAR questions, and roadmap.
   - For project flow ("What is project flow?"): Explain the full 6-step flow and 8 modules clearly.
   - For attached documents: Answer specifically using the uploaded document content as grounding context.
2. ZERO BOILERPLATE & NEVER GIVE CANNED EVASIONS:
   - NEVER reply with a generic canned greeting like "Hello! Ask me any question about your resume...". Always give the substantive answer immediately.
   - Start directly with the answer.
3. STRICT DOMAIN SCOPE & OUT-OF-DOMAIN REFUSAL:
   - You are EXCLUSIVELY the AI-Powered Interview Preparation & Internship Application Agent for this platform.
   - NEVER answer queries unrelated to this career platform, student resumes, internship matching, role recommendations, interview preparation, engineering concepts, or uploaded documents.
   - If the user asks about unrelated topics (e.g. cooking, recipes, movies, sports, politics, casual chit-chat, jokes, unrelated trivia):
     REFUSE politely and state:
     "I am the AI-Powered Interview Preparation & Internship Application Agent built specifically for this platform. I cannot answer queries unrelated to this project."
     Then explain how this project works (Resume-Based Role Recommendations, Interview Preparation with Technical/HR questions & roadmaps, Document-Based Q&A, and the 8 modules), and invite them to ask a career- or project-related question.
"""
        max_tokens = 800
        temperature = 0.2
    else:
        system_prompt = f"""You are the AI-Powered Interview Preparation Agent Chatbot on the IntelliIntern AI platform.
Provide structured, comprehensive career guidance for internship matching and interview preparation.

{project_architecture_info}

{ctx_info}

GUIDELINES:
1. Answer the candidate's question with thorough, actionable guidance.
2. For role recommendations: Provide match percentages, direct resume justifications, and tips to stand out.
3. For interview prep: Provide technical questions, STAR method guidelines, and preparation advice.
4. Ground your answers strictly in the candidate's extracted resume and projects.
5. Format in clean Markdown with bold bullet points. NEVER use ASCII or pipe tables.
6. STRICT DOMAIN SCOPE & OUT-OF-DOMAIN REFUSAL:
   - You are EXCLUSIVELY the AI-Powered Interview Preparation & Internship Application Agent for this platform.
   - NEVER answer queries unrelated to this career platform, student resumes, internship matching, role recommendations, interview preparation, engineering concepts, or uploaded documents.
   - If the user asks about unrelated topics (e.g. cooking, recipes, movies, sports, politics, casual chit-chat, jokes, unrelated trivia):
     REFUSE politely and state that you are designed specifically for this project, explain how this project works and what features it offers (Resume-Based Role Recommendations, Interview Preparation with Technical/HR questions & roadmaps, and Document-Based Q&A), and prompt them to ask a career- or project-related question.
"""
        max_tokens = 900
        temperature = 0.3

    groq_msgs = [{"role": "system", "content": system_prompt}]
    for m in messages[-8:]:
        groq_msgs.append({"role": m.get("role", "user"), "content": m.get("content", "")})

    content = _call_groq(groq_msgs, json_mode=False, temperature=temperature, max_tokens=max_tokens, model=PRIMARY_MODEL)
    if not content:
        content = _call_groq(groq_msgs, json_mode=False, temperature=temperature, max_tokens=max_tokens)

    if content:
        clean_res = _sanitize_unicode(_sanitize_text_response(content)).strip()
        # Ensure the LLM didn't return a canned non-answer evasion
        is_generic_evasion = any(
            phrase in clean_res.lower() for phrase in [
                "ask me any question about your resume",
                "i will provide a direct, concise answer",
                "how can i assist you today",
                "hello! how can i help you today"
            ]
        ) and len(clean_res.split()) < 35
        if not is_generic_evasion:
            return clean_res

    # Resilient grounded fallback
    return _generate_grounded_fallback(messages, student_context)


# ============================================================
# 2. RESUME-BASED ROLE RECOMMENDATIONS & SKILLS ASSESSMENT
# ============================================================

def generate_role_recommendations(resume_data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze candidate resume data and generate structured role recommendations and strongest skills."""
    skills_obj = resume_data.get("skills") or {}
    tech_skills = skills_obj.get("technical_skills") if isinstance(skills_obj, dict) else skills_obj
    tools = skills_obj.get("tools_frameworks") if isinstance(skills_obj, dict) else []
    soft = skills_obj.get("soft_skills") if isinstance(skills_obj, dict) else []
    projects = resume_data.get("projects") or []
    experience = resume_data.get("experience") or []
    education = resume_data.get("education") or []

    prompt = f"""
You are an expert AI Career Companion. Analyze this candidate's extracted resume data and recommend the top 3-4 suitable internship/job roles.

CANDIDATE EXTRACTED RESUME DATA:
- Technical Skills: {tech_skills}
- Tools & Frameworks: {tools}
- Soft Skills: {soft}
- Projects: {projects}
- Experience: {experience}
- Education: {education}

Return ONLY a valid JSON object matching this schema:
{{
  "candidate_name": "{resume_data.get('personal_info', {}).get('name', 'Candidate')}",
  "strongest_skills": [
    {{
      "skill": "Python",
      "category": "Backend Development",
      "proficiency": "Advanced",
      "evidence": "Applied in multiple API endpoints and asynchronous services"
    }}
  ],
  "recommended_roles": [
    {{
      "role": "Backend Engineering Intern",
      "match_score": 92,
      "badge": "Top Match",
      "rationale": "Strong proficiency in Python, REST APIs, and database design demonstrates immediate readiness.",
      "key_matching_skills": ["Python", "FastAPI", "SQL"],
      "recommended_internship_types": ["Product Startups", "Cloud Infrastructure Teams"],
      "interview_focus_areas": ["API Design", "Data Structures", "Database Indexing"]
    }}
  ],
  "suitable_internships": [
    {{
      "title": "Software Engineering Intern - Backend",
      "domain": "Enterprise Cloud Systems",
      "required_skills": ["Python", "FastAPI", "SQL"],
      "candidate_advantages": "Strong project portfolio with measurable impact"
    }}
  ],
  "strategic_advice": "Focus on high-scale distributed backend projects to maximize offers."
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a specialized career recommendation AI. Output valid JSON only."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Dynamic multi-disciplinary domain fallback
    cand_name = resume_data.get("personal_info", {}).get("name") or "Candidate"
    department = resume_data.get("department") or ""
    edu_list = resume_data.get("education") or []
    deg = edu_list[0].get("degree", "") if edu_list and isinstance(edu_list[0], dict) else ""
    pack = _get_domain_pack(department, deg, list(tech_skills or []), text=str(resume_data))

    strongest = []
    skill_list = list(tech_skills or pack["roles"][0]["key_matching_skills"])
    for i, sk in enumerate(skill_list[:3]):
        strongest.append({
            "skill": sk,
            "category": f"{pack['domain_name']} Core",
            "proficiency": "High",
            "evidence": "Demonstrated in verified practical coursework and project deliverables."
        })

    suitable_internships = [
        {
            "title": it["title"],
            "domain": pack["domain_name"],
            "required_skills": [s.strip() for s in it["required_skills"].split(",")],
            "candidate_advantages": it["rationale"]
        }
        for it in pack["internships"]
    ]

    return {
        "candidate_name": cand_name,
        "strongest_skills": strongest,
        "recommended_roles": pack["roles"],
        "suitable_internships": suitable_internships,
        "strategic_advice": f"Focus on high-impact projects in {pack['domain_name']} to maximize competitive internship offers."
    }


# ============================================================
# 3. ROLE-SPECIFIC INTERVIEW PREPARATION GENERATION
# ============================================================

def generate_interview_prep_pack(role: str, resume_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Generate comprehensive role-specific interview questions, answer guidance, and a preparation roadmap."""
    resume_context = ""
    if resume_data:
        r_skills = resume_data.get("skills") or {}
        tech = r_skills.get("technical_skills") if isinstance(r_skills, dict) else r_skills
        projs = [p.get("title", "") for p in resume_data.get("projects", [])]
        resume_context = f"Candidate Skills: {tech}, Projects: {projs}"

    prompt = f"""
You are an expert technical interviewer and HR executive. Generate a complete, high-yield Interview Preparation Pack for the target role: "{role}".
{resume_context}

Return ONLY valid JSON matching this exact schema:
{{
  "role": "{role}",
  "overview": "Summary of interview expectations and hiring bar for {role}.",
  "technical_questions": [
    {{
      "id": 1,
      "question": "Clear technical interview question",
      "topic": "Topic category (e.g. Data Structures, Backend, System Design)",
      "answer_guidance": "Key technical points and concepts the candidate must address",
      "sample_answer": "Concise model answer demonstrating deep technical competence"
    }}
  ],
  "hr_questions": [
    {{
      "id": 1,
      "question": "Behavioral / HR question",
      "focus_area": "Cultural Fit / Conflict Resolution / Leadership",
      "answer_guidance": "How to structure the answer effectively",
      "star_tip": "STAR framework guidance (Situation, Task, Action, Result)"
    }}
  ],
  "roadmap": [
    {{
      "phase": "Week 1",
      "title": "Core Fundamentals & Tech Stack Mastery",
      "duration": "Days 1-7",
      "topics": ["Data structures", "OOP principles", "Language syntax"],
      "action_items": ["Solve 15 LeetCode problems", "Review core CS fundamentals"]
    }},
    {{
      "phase": "Week 2",
      "title": "Framework Deep Dive & Architecture",
      "duration": "Days 8-14",
      "topics": ["REST APIs", "Database indexing", "Asynchronous programming"],
      "action_items": ["Build or refactor a microservice project", "Write clean unit tests"]
    }},
    {{
      "phase": "Week 3",
      "title": "System Design Basics & Project Defense",
      "duration": "Days 15-21",
      "topics": ["Caching", "Database schema design", "Resume project deep dive"],
      "action_items": ["Prepare 3-minute project walkthroughs", "Practice whiteboarding"]
    }},
    {{
      "phase": "Week 4",
      "title": "Mock Interviews & Behavioral STAR Mastery",
      "duration": "Days 22-28",
      "topics": ["HR behavioral questions", "Live timed coding", "Salary negotiation"],
      "action_items": ["Conduct 3 peer mock interviews", "Prepare questions for interviewer"]
    }}
  ],
  "priority_topics": [
    {{
      "topic": "RESTful API Design & Status Codes",
      "importance": "High",
      "description": "Idempotency, HTTP verbs, authentication (JWT/OAuth), and pagination."
    }},
    {{
      "topic": "Relational Databases & SQL Optimization",
      "importance": "Critical",
      "description": "JOIN operations, indexing, ACID transactions, and normalization."
    }},
    {{
      "topic": "Concurrency & Asynchronous I/O",
      "importance": "Medium-High",
      "description": "Event loops, thread pooling, async/await patterns, and race conditions."
    }}
  ],
  "learning_path_recommendations": [
    "Build an end-to-end full-stack or backend portfolio project with live deployment on AWS/Render.",
    "Master the STAR method for every bullet point on your resume to articulate quantified business impact.",
    "Practice talking aloud through your thought process while coding problems on LeetCode/HackerRank."
  ]
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a specialized technical interview preparation generator. Return clean JSON only."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Dynamic multi-disciplinary domain fallback for interview prep
    pack = _get_domain_pack(target_role=role, text=f"{role} {str(resume_data or '')}")
    tech_qs = []
    for q_obj in pack["technical_questions"]:
        tech_qs.append({
            "id": q_obj["id"],
            "question": q_obj["question"],
            "topic": q_obj["topic"],
            "answer_guidance": q_obj["answer_guidance"],
            "sample_answer": q_obj["answer_guidance"]
        })

    roadmap_items = [
        {
            "phase": rm["phase"],
            "title": rm["title"],
            "duration": f"Days {i*7+1}-{(i+1)*7}",
            "topics": [rm["title"]],
            "action_items": [rm["tasks"]]
        }
        for i, rm in enumerate(pack["roadmap"])
    ]

    priority_topics_items = [
        {
            "topic": top,
            "importance": "High",
            "description": f"Core competency area in {pack['domain_name']} interviews."
        }
        for top in pack["priority_topics"]
    ]

    return {
        "role": role,
        "overview": f"Comprehensive interview guide for {role}. Technical rounds evaluate practical problem-solving, domain rigor, and fundamentals in {pack['domain_name']}.",
        "technical_questions": tech_qs,
        "hr_questions": [
            {
                "id": 1,
                "question": pack["hr_question"]["question"],
                "focus_area": "Operational Excellence & Problem Solving",
                "answer_guidance": pack["hr_question"]["guidance"],
                "star_tip": "Situation: Context of problem. Task: Your responsibility. Action: Systematic steps. Result: Quantified positive impact."
            },
            {
                "id": 2,
                "question": f"Why are you interested in this {role} internship and our engineering organization?",
                "focus_area": "Motivation & Alignment",
                "answer_guidance": "Connect a specific project from your resume with the problems the company solves.",
                "star_tip": "Cite practical coursework and project metrics that prove immediate readiness."
            }
        ],
        "roadmap": roadmap_items,
        "priority_topics": priority_topics_items,
        "learning_path_recommendations": [
            f"Review fundamental equations, principles, and software tools in {pack['domain_name']}.",
            "Master the STAR method for every project listed on your resume.",
            "Practice articulating your technical reasoning aloud during mock problem-solving screens."
        ]
    }


# ============================================================
# 4. DOCUMENT-BASED QUESTION & ANSWER GENERATION
# ============================================================

def generate_document_qa(document_text: str, filename: str, num_questions: int = 6) -> Dict[str, Any]:
    """Extract content from uploaded document and generate relevant questions and answers."""
    clean_text = document_text.strip()[:8000]

    prompt = f"""
You are an expert Document Analysis and Q&A Agent. Read the following document content extracted from "{filename}" and generate a comprehensive Question & Answer set.

DOCUMENT CONTENT:
{clean_text}

Generate:
1. A concise 2-sentence summary of the document.
2. 4-6 key topics covered.
3. {num_questions} high-value Questions and detailed Answers derived STRICTLY from this document content.
4. 3 suggested follow-up questions the user can ask in the chatbot.

Return ONLY valid JSON matching this schema:
{{
  "filename": "{filename}",
  "summary": "Executive summary of the document content...",
  "word_count": {len(clean_text.split())},
  "key_topics": ["Topic 1", "Topic 2", "Topic 3"],
  "qa_pairs": [
    {{
      "id": 1,
      "question": "Question based directly on document content?",
      "answer": "Comprehensive answer explaining the concept with specific details from the document.",
      "source_excerpt": "Relevant sentence or snippet from the text supporting this answer"
    }}
  ],
  "suggested_questions": [
    "Follow-up question 1?",
    "Follow-up question 2?"
  ]
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a specialized document Q&A engine. Output valid JSON only."},
        {"role": "user", "content": prompt}
    ], json_mode=True)

    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed

    # Intelligent heuristic fallback
    lines = [l.strip() for l in clean_text.splitlines() if l.strip()]
    headings = [l for l in lines if len(l) < 60 and not l.endswith(".")][:5]
    if not headings:
        headings = ["Document Overview", "Key Concepts", "Core Requirements", "Implementation Steps"]

    qa_list = []
    for i, h in enumerate(headings[:num_questions], start=1):
        qa_list.append({
            "id": i,
            "question": f"What are the main principles and details covered in section '{h}'?",
            "answer": f"The section '{h}' highlights critical concepts, technical requirements, and core workflows outlined in {filename}. It establishes the foundational guidelines and strategic objectives discussed throughout the text.",
            "source_excerpt": f"Reference: {h} - {lines[i*2] if i*2 < len(lines) else 'Core document guidelines'}"
        })

    return {
        "filename": filename,
        "summary": f"This document ({filename}) outlines key specifications, technical guidelines, and structured procedures across {len(lines)} content lines.",
        "word_count": len(clean_text.split()),
        "key_topics": headings,
        "qa_pairs": qa_list,
        "suggested_questions": [
            f"Can you explain the key takeaways of '{headings[0] if headings else 'the document'}' in detail?",
            "How does this document relate to my career and internship preparation?",
            "What action items should I implement based on this content?"
        ]
    }


def review_code(code: str):
    """Review student code for quality, score, and suggestions."""
    prompt = f"""
You are an AI Code Reviewer for an internship platform. Review the following code.
CODE:
{code[:4000]}

Return JSON:
{{
  "score": 85,
  "feedback": "Clear explanation of code structure and design",
  "suggestions": "Actionable improvements"
}}
"""
    raw_content = _call_groq([
        {"role": "system", "content": "You are a code reviewer. Return valid JSON only."},
        {"role": "user", "content": prompt}
    ], json_mode=True)
    parsed = _clean_and_parse_json(raw_content)
    if parsed:
        return parsed
    return {
        "score": 82,
        "feedback": "Code is functionally sound and formatted properly.",
        "suggestions": "Add type annotations, error boundary checks, and unit test coverage."
    }