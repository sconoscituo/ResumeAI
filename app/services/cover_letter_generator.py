"""자기소개서 생성 서비스"""
import json
from app.services.gemini import generate_text


SECTION_PROMPTS = {
    "motivation": """지원동기를 작성해주세요.
- 해당 회사/직무를 선택한 구체적인 이유
- 회사의 비전/문화와 본인의 가치관 연결
- 직무 관련 경험과 역량 강조""",

    "growth": """성장과정을 작성해주세요.
- 직무 역량 형성에 영향을 준 경험 중심
- 구체적인 에피소드와 배운 점
- 현재의 역량과 연결""",

    "personality": """성격의 장단점을 작성해주세요.
- 업무와 관련된 강점 2-3가지 (구체적 사례 포함)
- 단점과 이를 극복하려는 노력
- 솔직하고 신뢰감 있는 표현""",

    "aspiration": """입사 후 포부를 작성해주세요.
- 단기(1-2년) 및 장기(3-5년) 목표
- 회사의 성장에 기여하는 방향
- 직무 전문성 개발 계획""",

    "achievement": """주요 성과 및 경험을 작성해주세요.
- STAR 기법 활용 (상황-과제-행동-결과)
- 수치화된 성과 포함
- 직무 연관성 강조""",

    "teamwork": """팀워크/협업 경험을 작성해주세요.
- 팀 프로젝트에서의 역할
- 갈등 해결 경험
- 협업으로 달성한 성과""",

    "challenge": """도전/극복 경험을 작성해주세요.
- 어려운 상황이나 실패 경험
- 극복 과정과 방법
- 성장과 배움""",

    "custom": """아래 항목에 맞게 작성해주세요.""",
}


def build_profile_context(profile_data: dict) -> str:
    """프로필 정보를 프롬프트용 텍스트로 변환"""
    lines = []

    lines.append(f"## 지원자 정보")
    lines.append(f"- 이름: {profile_data.get('name', '')}")
    lines.append(f"- 이메일: {profile_data.get('email', '')}")
    if profile_data.get("summary"):
        lines.append(f"- 한 줄 소개: {profile_data['summary']}")

    # 기술 스택
    skills = profile_data.get("skills_list", [])
    if skills:
        lines.append(f"\n## 기술 스택")
        lines.append(", ".join(skills))

    # 학력
    educations = profile_data.get("educations", [])
    if educations:
        lines.append(f"\n## 학력")
        for edu in educations:
            lines.append(f"- {edu.get('school_name', '')} {edu.get('major', '')} {edu.get('degree', '')} ({edu.get('start_date', '')} ~ {edu.get('end_date', '')})")

    # 경력
    careers = profile_data.get("careers", [])
    if careers:
        lines.append(f"\n## 경력")
        for career in careers:
            lines.append(f"- {career.get('company_name', '')} / {career.get('position', '')} ({career.get('start_date', '')} ~ {career.get('end_date', '')})")
            if career.get("description"):
                lines.append(f"  담당업무: {career['description']}")
            if career.get("achievements"):
                lines.append(f"  주요성과: {career['achievements']}")

    # 프로젝트
    projects = profile_data.get("projects", [])
    if projects:
        lines.append(f"\n## 프로젝트")
        for proj in projects:
            lines.append(f"- {proj.get('project_name', '')} ({proj.get('role', '')})")
            if proj.get("description"):
                lines.append(f"  내용: {proj['description']}")
            if proj.get("achievements"):
                lines.append(f"  성과: {proj['achievements']}")

    # 자격증
    certificates = profile_data.get("certificates", [])
    if certificates:
        lines.append(f"\n## 자격증")
        for cert in certificates:
            lines.append(f"- {cert.get('cert_name', '')} ({cert.get('issuer', '')}, {cert.get('issue_date', '')})")

    return "\n".join(lines)


async def generate_section(
    section_type: str,
    section_title: str,
    profile_data: dict,
    job_analysis: dict,
    word_limit: int = 500,
) -> str:
    """자기소개서 항목 하나 생성"""
    profile_context = build_profile_context(profile_data)
    section_guide = SECTION_PROMPTS.get(section_type, SECTION_PROMPTS["custom"])

    job_context = ""
    if job_analysis:
        job_context = f"""
## 채용 정보
- 회사: {job_analysis.get('company_name', '')}
- 직무: {job_analysis.get('position', '')}
- 핵심 키워드: {', '.join(job_analysis.get('keywords', []))}
- 요구 역량: {', '.join(job_analysis.get('required_skills', []))}
- 주요 업무: {'; '.join(job_analysis.get('responsibilities', [])[:3])}
"""

    prompt = f"""당신은 한국 취업 시장 전문 자기소개서 작성 컨설턴트입니다.
아래 지원자 정보와 채용공고를 바탕으로 자기소개서 항목을 작성해주세요.

{profile_context}

{job_context}

## 작성 항목
제목: {section_title}
{section_guide}

## 작성 지침
- 글자 수: {word_limit}자 내외
- 구체적인 경험과 수치를 포함
- 채용공고의 핵심 키워드를 자연스럽게 녹여낼 것
- 한국 취업 문화에 맞는 공손하고 전문적인 어투
- 첫인상을 주는 강렬한 첫 문장으로 시작
- 자기소개서 항목 제목은 작성하지 말고 내용만 작성

지금 바로 자기소개서를 작성해주세요:"""

    content = await generate_text(prompt)
    return content.strip()
