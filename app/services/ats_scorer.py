"""ATS (Applicant Tracking System) 키워드 매칭 분석 서비스"""
import json
import re
from app.services.gemini import generate_json


def extract_keywords_simple(text: str) -> list[str]:
    """텍스트에서 간단한 키워드 추출 (전처리용)"""
    # 한글, 영문, 숫자만 남기고 소문자화
    text = re.sub(r"[^\w\s가-힣]", " ", text)
    words = text.split()
    # 2글자 이상 단어만
    return [w for w in words if len(w) >= 2]


async def calculate_ats_score(profile_data: dict, job_analysis: dict) -> dict:
    """ATS 점수 계산 및 상세 분석"""

    # 프로필 전체 텍스트 구성
    profile_texts = []
    profile_texts.append(profile_data.get("summary", ""))
    profile_texts.extend(profile_data.get("skills_list", []))

    for career in profile_data.get("careers", []):
        profile_texts.append(career.get("description", ""))
        profile_texts.append(career.get("achievements", ""))
        profile_texts.append(career.get("position", ""))

    for project in profile_data.get("projects", []):
        profile_texts.append(project.get("description", ""))
        profile_texts.append(project.get("achievements", ""))
        profile_texts.append(project.get("tech_stack", ""))

    for cert in profile_data.get("certificates", []):
        profile_texts.append(cert.get("cert_name", ""))

    profile_full_text = " ".join(t for t in profile_texts if t)

    # 채용공고 키워드
    job_keywords = (
        job_analysis.get("keywords", [])
        + job_analysis.get("required_skills", [])
        + job_analysis.get("preferred_skills", [])
    )

    prompt = f"""당신은 ATS(Applicant Tracking System) 전문가입니다.
아래 이력서와 채용공고를 비교하여 ATS 매칭 분석을 수행하세요.

## 이력서 내용
{profile_full_text[:3000]}

## 채용공고 핵심 키워드
{json.dumps(job_keywords, ensure_ascii=False)}

## 채용공고 요구사항
{json.dumps(job_analysis.get('requirements', []), ensure_ascii=False)}

다음 JSON 형식으로 분석 결과를 제공하세요:
{{
  "overall_score": 75,
  "keyword_match_score": 80,
  "skill_match_score": 70,
  "experience_match_score": 75,
  "matched_keywords": ["매칭된 키워드1", "키워드2"],
  "missing_keywords": ["누락된 키워드1", "키워드2"],
  "matched_skills": ["매칭된 기술1", "기술2"],
  "missing_skills": ["누락된 기술1", "기술2"],
  "strengths": ["강점1", "강점2", "강점3"],
  "improvements": ["개선 권고사항1", "권고2", "권고3"],
  "summary": "ATS 분석 종합 의견 (2-3문장)"
}}

점수는 0-100 사이의 정수로 제공하세요."""

    result = await generate_json(prompt)

    # 안전 처리: overall_score가 없으면 기본값
    if "overall_score" not in result:
        result["overall_score"] = 0

    return result
