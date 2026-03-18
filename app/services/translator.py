"""한국어 이력서 → 영문 이력서 번역 서비스 (직역이 아닌 현지화)"""
from app.services.gemini import generate_json


async def translate_resume_to_english(resume_content: dict, profile_data: dict) -> dict:
    """한국어 이력서 콘텐츠를 영문으로 현지화 번역"""

    # 번역 프롬프트 구성
    profile_summary = f"""
이름: {profile_data.get('name', '')}
이메일: {profile_data.get('email', '')}
전화번호: {profile_data.get('phone', '')}
주소: {profile_data.get('address', '')}
깃허브: {profile_data.get('github_url', '')}
링크드인: {profile_data.get('linkedin_url', '')}
포트폴리오: {profile_data.get('portfolio_url', '')}
"""

    prompt = f"""당신은 영문 이력서 전문가입니다. 아래 한국어 이력서를 영미권 취업 시장에 맞게 영문으로 현지화 번역해주세요.

번역 원칙:
1. 직역이 아닌 현지화: 한국식 표현을 영미권에서 자연스러운 표현으로 변환
2. 직무/직책명은 글로벌 표준 명칭 사용 (예: "대리" → "Associate", "과장" → "Manager")
3. 학교/기관명은 공식 영문명 사용
4. 성과 수치가 있으면 그대로 유지
5. Action verb로 시작하는 bullet point 형식 사용
6. ATS 친화적인 키워드 사용

[프로필 정보]
{profile_summary}

[한국어 이력서 내용]
전문가 요약: {resume_content.get('summary', '')}
핵심 기술: {', '.join(resume_content.get('skills', []))}

경력:
{_format_careers_for_prompt(resume_content.get('enhanced_careers', []))}

프로젝트:
{_format_projects_for_prompt(resume_content.get('projects', []))}

학력:
{_format_educations_for_prompt(resume_content.get('educations', []))}

자격증:
{_format_certs_for_prompt(resume_content.get('certificates', []))}

아래 JSON 형식으로 응답하세요:
{{
  "profile": {{
    "name": "영문 이름",
    "email": "이메일",
    "phone": "전화번호",
    "address": "주소",
    "github_url": "깃허브",
    "linkedin_url": "링크드인",
    "portfolio_url": "포트폴리오"
  }},
  "summary": "Professional Summary in English",
  "skills": ["skill1", "skill2"],
  "enhanced_careers": [
    {{
      "company_name": "Company Name",
      "position": "Job Title",
      "department": "Department",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "highlights": "• Achievement 1\\n• Achievement 2"
    }}
  ],
  "projects": [
    {{
      "project_name": "Project Name",
      "role": "Role",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "description": "Project description",
      "achievements": "Key achievements",
      "tech_stack": ["tech1", "tech2"],
      "github_url": "",
      "demo_url": ""
    }}
  ],
  "educations": [
    {{
      "school_name": "University Name",
      "degree": "Bachelor of Science",
      "major": "Computer Science",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM",
      "gpa": ""
    }}
  ],
  "certificates": [
    {{
      "cert_name": "Certificate Name",
      "issuer": "Issuing Organization",
      "issue_date": "YYYY-MM"
    }}
  ],
  "job_info": {{
    "position": "Target Position"
  }}
}}"""

    result = await generate_json(prompt)

    # 프로필 정보가 번역에 포함되지 않은 경우 원본으로 보완
    if "profile" not in result:
        result["profile"] = {
            "name": profile_data.get("name", ""),
            "email": profile_data.get("email", ""),
            "phone": profile_data.get("phone", ""),
            "address": profile_data.get("address", ""),
            "github_url": profile_data.get("github_url", ""),
            "linkedin_url": profile_data.get("linkedin_url", ""),
            "portfolio_url": profile_data.get("portfolio_url", ""),
        }

    return result


def _format_careers_for_prompt(careers: list) -> str:
    """경력 데이터를 프롬프트용 텍스트로 변환"""
    if not careers:
        return "없음"
    lines = []
    for c in careers:
        lines.append(
            f"- {c.get('company_name', '')} | {c.get('position', '')} | "
            f"{c.get('start_date', '')}~{c.get('end_date', '')}\n"
            f"  {c.get('highlights', c.get('description', ''))}"
        )
    return "\n".join(lines)


def _format_projects_for_prompt(projects: list) -> str:
    """프로젝트 데이터를 프롬프트용 텍스트로 변환"""
    if not projects:
        return "없음"
    lines = []
    for p in projects:
        lines.append(
            f"- {p.get('project_name', '')} | {p.get('role', '')} | "
            f"{p.get('start_date', '')}~{p.get('end_date', '')}\n"
            f"  {p.get('description', '')}"
        )
    return "\n".join(lines)


def _format_educations_for_prompt(educations: list) -> str:
    """학력 데이터를 프롬프트용 텍스트로 변환"""
    if not educations:
        return "없음"
    return "\n".join(
        f"- {e.get('school_name', '')} {e.get('degree', '')} {e.get('major', '')}"
        for e in educations
    )


def _format_certs_for_prompt(certs: list) -> str:
    """자격증 데이터를 프롬프트용 텍스트로 변환"""
    if not certs:
        return "없음"
    return "\n".join(
        f"- {c.get('cert_name', '')} ({c.get('issuer', '')})"
        for c in certs
    )
