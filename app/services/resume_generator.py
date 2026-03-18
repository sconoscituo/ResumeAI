"""이력서 생성 서비스"""
import json
from app.services.gemini import generate_json, generate_text


async def generate_resume_summary(profile_data: dict, job_analysis: dict) -> str:
    """채용공고에 맞는 맞춤형 이력서 요약 생성"""
    skills = profile_data.get("skills_list", [])
    careers = profile_data.get("careers", [])
    career_summary = "; ".join(
        f"{c.get('company_name', '')} {c.get('position', '')}"
        for c in careers[:3]
    )

    prompt = f"""한국 취업 시장 전문가로서 아래 정보를 바탕으로 이력서 상단에 들어갈 전문가 요약(Professional Summary)을 작성해주세요.

## 지원자 정보
- 이름: {profile_data.get('name', '')}
- 기술 스택: {', '.join(skills)}
- 경력: {career_summary}
- 기존 요약: {profile_data.get('summary', '')}

## 지원 직무
- 회사: {job_analysis.get('company_name', '')}
- 직무: {job_analysis.get('position', '')}
- 핵심 키워드: {', '.join(job_analysis.get('keywords', [])[:8])}

## 작성 기준
- 3-4문장으로 간결하게
- 직무와 관련된 핵심 역량 강조
- ATS 통과를 위한 키워드 자연스럽게 포함
- 3인칭 사용 금지, "저는" 등 1인칭 표현도 사용 금지 (명사형으로 작성)
- 숫자/수치 포함하여 임팩트 강조

요약만 작성하세요 (제목 없이):"""

    return await generate_text(prompt)


async def generate_career_highlights(career: dict, job_keywords: list) -> str:
    """경력 항목별 AI 강화 불릿 포인트 생성"""
    prompt = f"""다음 경력 사항을 이력서용 불릿 포인트로 재작성해주세요.

## 경력 정보
- 회사: {career.get('company_name', '')}
- 직위: {career.get('position', '')}
- 담당업무: {career.get('description', '')}
- 주요성과: {career.get('achievements', '')}

## 채용공고 키워드 (가능하면 포함)
{', '.join(job_keywords[:10])}

## 작성 기준
- 3-5개의 불릿 포인트
- 행동 동사로 시작 (개발, 구현, 개선, 달성 등)
- 수치/결과 포함 (가능한 경우)
- 각 줄은 "- "로 시작

불릿 포인트만 작성하세요:"""

    result = await generate_text(prompt)
    return result.strip()


async def build_resume_content(profile_data: dict, job_analysis: dict) -> dict:
    """완성된 이력서 콘텐츠 구조 생성"""
    job_keywords = job_analysis.get("keywords", []) + job_analysis.get("required_skills", [])

    # 전문가 요약 생성
    summary = await generate_resume_summary(profile_data, job_analysis)

    # 각 경력에 대한 강화된 설명 생성
    enhanced_careers = []
    for career in profile_data.get("careers", []):
        highlights = await generate_career_highlights(career, job_keywords)
        enhanced_careers.append({
            **career,
            "highlights": highlights,
        })

    return {
        "summary": summary.strip(),
        "enhanced_careers": enhanced_careers,
        "skills": profile_data.get("skills_list", []),
        "educations": profile_data.get("educations", []),
        "projects": profile_data.get("projects", []),
        "certificates": profile_data.get("certificates", []),
        "profile": {
            "name": profile_data.get("name", ""),
            "email": profile_data.get("email", ""),
            "phone": profile_data.get("phone", ""),
            "address": profile_data.get("address", ""),
            "github_url": profile_data.get("github_url", ""),
            "linkedin_url": profile_data.get("linkedin_url", ""),
            "portfolio_url": profile_data.get("portfolio_url", ""),
        },
        "job_info": {
            "company_name": job_analysis.get("company_name", ""),
            "position": job_analysis.get("position", ""),
        },
    }
