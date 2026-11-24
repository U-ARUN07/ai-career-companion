import io
import os
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle
)


def _clean_text(val: Any) -> str:
    """Escape XML-sensitive characters for ReportLab paragraphs."""
    if val is None:
        return ""
    text = str(val).strip()
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return text


def generate_cv_pdf_bytes(cv_data: Dict[str, Any], template: str = "modern") -> bytes:
    """
    Generate an executive, beautifully styled CV PDF in-memory and return raw bytes.
    Supports both CustomizerPage cvData and standard resume schemas.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=14 * mm,
        leftMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    # Color themes based on chosen template
    if template == "classic":
        primary_color = colors.HexColor("#0f766e")    # Harvard / Deep Teal
        accent_color = colors.HexColor("#000000")
        rule_color = colors.HexColor("#0d9488")
    elif template == "minimal":
        primary_color = colors.HexColor("#0f172a")    # Deep Slate / Monochrome
        accent_color = colors.HexColor("#000000")
        rule_color = colors.HexColor("#334155")
    else:  # "modern"
        primary_color = colors.HexColor("#0d9488")    # Modern Oceanic Teal
        accent_color = colors.HexColor("#000000")     # Solid Pitch Black
        rule_color = colors.HexColor("#0d9488")

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "CVName",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=accent_color,
        alignment=TA_CENTER,
        spaceAfter=2
    )

    role_style = ParagraphStyle(
        "CVRole",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=primary_color,
        alignment=TA_CENTER,
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        "CVContact",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        alignment=TA_CENTER,
        spaceAfter=6
    )

    section_style = ParagraphStyle(
        "CVSectionHeading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#000000"),
        spaceBefore=6,
        spaceAfter=2
    )

    body_style = ParagraphStyle(
        "CVBody",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2
    )

    bullet_style = ParagraphStyle(
        "CVBullet",
        parent=body_style,
        leftIndent=11,
        firstLineIndent=-7,
        spaceAfter=2
    )

    story = []

    # 1. HEADER: NAME & TITLE
    name = cv_data.get("fullName") or cv_data.get("name") or "Candidate"
    role = cv_data.get("roleTitle") or cv_data.get("career_objective") or ""

    story.append(Paragraph(f"<b>{_clean_text(name).upper()}</b>", name_style))
    if role:
        story.append(Paragraph(f"<b>{_clean_text(role)}</b>", role_style))

    # 2. CONTACT STRIP
    contact_parts = []
    for field in ["email", "phone", "location", "linkedin", "github"]:
        val = cv_data.get(field)
        if val:
            contact_parts.append(_clean_text(val))

    if contact_parts:
        contact_line = " &nbsp;|&nbsp; ".join(contact_parts)
        story.append(Paragraph(contact_line, contact_style))

    story.append(HRFlowable(width="100%", thickness=1.5, color=rule_color, spaceAfter=6, spaceBefore=2))

    # Helper: add section banner
    def add_section_header(title: str):
        story.append(Paragraph(f"<b>{_clean_text(title).upper()}</b>", section_style))
        story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#cbd5e1"), spaceAfter=4, spaceBefore=1))

    # 3. PROFESSIONAL SUMMARY
    summary = cv_data.get("summary")
    if summary:
        add_section_header("Professional Summary")
        story.append(Paragraph(_clean_text(summary), body_style))
        story.append(Spacer(1, 3))

    # 4. TECHNICAL COMPETENCIES / SKILLS
    skills = cv_data.get("skills")
    if skills:
        add_section_header("Professional Competencies & Skills")
        if isinstance(skills, dict):
            has_rendered_any = False
            # Check for domain-specific / universal keys
            if skills.get("technical_skills"):
                val_str = ", ".join(skills["technical_skills"]) if isinstance(skills["technical_skills"], list) else str(skills["technical_skills"])
                story.append(Paragraph(f"<b>Core Domain Competencies:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True
            if skills.get("languages"):
                val_str = ", ".join(skills["languages"]) if isinstance(skills["languages"], list) else str(skills["languages"])
                story.append(Paragraph(f"<b>Programming Languages:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True
            if skills.get("tools_frameworks"):
                val_str = ", ".join(skills["tools_frameworks"]) if isinstance(skills["tools_frameworks"], list) else str(skills["tools_frameworks"])
                story.append(Paragraph(f"<b>Tools, Software & Platforms:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True
            if skills.get("frameworks"):
                val_str = ", ".join(skills["frameworks"]) if isinstance(skills["frameworks"], list) else str(skills["frameworks"])
                story.append(Paragraph(f"<b>Frameworks & Libraries:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True
            if skills.get("cloud_devops"):
                val_str = ", ".join(skills["cloud_devops"]) if isinstance(skills["cloud_devops"], list) else str(skills["cloud_devops"])
                story.append(Paragraph(f"<b>Cloud & DevOps:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True
            if skills.get("soft_skills"):
                val_str = ", ".join(skills["soft_skills"]) if isinstance(skills["soft_skills"], list) else str(skills["soft_skills"])
                story.append(Paragraph(f"<b>Professional & Interpersonal Strengths:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True
            if skills.get("concepts"):
                val_str = ", ".join(skills["concepts"]) if isinstance(skills["concepts"], list) else str(skills["concepts"])
                story.append(Paragraph(f"<b>Architectural Concepts:</b> {_clean_text(val_str)}", body_style))
                has_rendered_any = True

            if not has_rendered_any:
                for k, v in skills.items():
                    if v:
                        v_str = ", ".join(v) if isinstance(v, list) else str(v)
                        story.append(Paragraph(f"<b>{k.replace('_', ' ').title()}:</b> {_clean_text(v_str)}", body_style))
        elif isinstance(skills, list):
            skill_text = " &bull; ".join(_clean_text(s) for s in skills if s)
            story.append(Paragraph(skill_text, body_style))
        elif isinstance(skills, str):
            story.append(Paragraph(_clean_text(skills), body_style))
        story.append(Spacer(1, 3))

    # 5. WORK EXPERIENCE
    experience = cv_data.get("experience") or []
    if experience:
        add_section_header("Professional Experience & Internships")
        for exp in experience:
            if isinstance(exp, dict):
                role_str = _clean_text(exp.get("role") or exp.get("title") or "Engineering Role")
                company_str = _clean_text(exp.get("company") or "Company")
                duration_str = _clean_text(exp.get("duration") or "")
                location_str = _clean_text(exp.get("location") or "")

                top_left = f"<b>{role_str}</b> &mdash; <b>{company_str}</b>"
                top_right = f"<font color=\"#1e293b\"><b>{duration_str}</b>{(' | ' + location_str) if location_str else ''}</font>"

                tbl = Table(
                    [[Paragraph(top_left, body_style), Paragraph(top_right, ParagraphStyle("TR", parent=body_style, alignment=TA_RIGHT))]],
                    colWidths=["72%", "28%"]
                )
                tbl.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                ]))
                story.append(tbl)

                bullets = exp.get("bullets") or []
                if isinstance(bullets, str):
                    bullets = [bullets]
                for b in bullets:
                    if b:
                        story.append(Paragraph(f"&bull; {_clean_text(b)}", bullet_style))
                story.append(Spacer(1, 3))
            elif isinstance(exp, str):
                story.append(Paragraph(f"&bull; {_clean_text(exp)}", bullet_style))
        story.append(Spacer(1, 2))

    # 6. KEY PROJECTS & INITIATIVES
    projects = cv_data.get("projects") or []
    if projects:
        add_section_header("Key Projects & Strategic Initiatives")
        for proj in projects:
            if isinstance(proj, dict):
                title_str = _clean_text(proj.get("title") or "Project")
                raw_tech = proj.get("tech") or proj.get("tech_stack") or ""
                if isinstance(raw_tech, list):
                    tech_str = ", ".join(str(t) for t in raw_tech)
                else:
                    tech_str = str(raw_tech)
                tech_str = _clean_text(tech_str)

                heading_text = f"<b>{title_str}</b>"
                if tech_str:
                    heading_text += f" <font color=\"#0d9488\"><b>(Tech Stack: {tech_str})</b></font>"

                story.append(Paragraph(heading_text, body_style))

                bullets = proj.get("bullets") or []
                if isinstance(bullets, str):
                    bullets = [bullets]
                for b in bullets:
                    if b:
                        story.append(Paragraph(f"&bull; {_clean_text(b)}", bullet_style))

                desc = proj.get("description")
                if desc and not bullets:
                    story.append(Paragraph(f"&bull; {_clean_text(desc)}", bullet_style))

                story.append(Spacer(1, 3))
            elif isinstance(proj, str):
                story.append(Paragraph(f"&bull; {_clean_text(proj)}", bullet_style))
        story.append(Spacer(1, 2))

    # 7. EDUCATION & CREDENTIALS
    education = cv_data.get("education") or []
    if education:
        add_section_header("Education & Credentials")
        for edu in education:
            if isinstance(edu, dict):
                deg_str = _clean_text(edu.get("degree") or "Degree")
                school_str = _clean_text(edu.get("school") or edu.get("institution") or "University")
                dur_str = _clean_text(edu.get("duration") or edu.get("year") or "")
                gpa_str = _clean_text(edu.get("gpa") or edu.get("score") or "")

                left_txt = f"<b>{deg_str}</b> &mdash; <b>{school_str}</b>"
                right_txt = f"<font color=\"#1e293b\"><b>{dur_str}</b>{(' | ' + gpa_str) if gpa_str else ''}</font>"

                tbl = Table(
                    [[Paragraph(left_txt, body_style), Paragraph(right_txt, ParagraphStyle("ETR", parent=body_style, alignment=TA_RIGHT))]],
                    colWidths=["72%", "28%"]
                )
                tbl.setStyle(TableStyle([
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                ]))
                story.append(tbl)

                if edu.get("details"):
                    story.append(Paragraph(f"<font color=\"#64748b\">{_clean_text(edu['details'])}</font>", body_style))
                story.append(Spacer(1, 3))
            elif isinstance(edu, str):
                story.append(Paragraph(f"&bull; {_clean_text(edu)}", bullet_style))
        story.append(Spacer(1, 2))

    # 8. CERTIFICATIONS & HONORS
    certifications = cv_data.get("certifications") or []
    if certifications:
        add_section_header("Certifications & Honors")
        for cert in certifications:
            if cert:
                story.append(Paragraph(f"&bull; {_clean_text(cert)}", bullet_style))
        story.append(Spacer(1, 2))

    # 9. CAREER RECOMMENDATION / OBJECTIVE
    career_rec = cv_data.get("career_recommendation")
    if career_rec:
        add_section_header("Career Pathway")
        story.append(Paragraph(_clean_text(career_rec), body_style))

    doc.build(story)
    return buffer.getvalue()


def generate_cv_pdf(
    cv_data: Optional[Dict[str, Any]] = None,
    output_path: Optional[str] = None,
    **kwargs
) -> str:
    """
    Generate a CV PDF and write to output_path on disk.
    Fully backwards-compatible with keyword arguments (summary=..., skills=..., etc.)
    """
    if cv_data is None:
        cv_data = {}

    for k, v in kwargs.items():
        if k not in cv_data:
            cv_data[k] = v

    if not output_path:
        filename = kwargs.get("filename") or cv_data.get("filename") or "Candidate_CV.pdf"
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(base_dir, "uploads", "cv")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, filename)

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    template = cv_data.get("template") or "modern"
    pdf_bytes = generate_cv_pdf_bytes(cv_data, template=template)

    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    return output_path
