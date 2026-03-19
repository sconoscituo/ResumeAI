"""
ATS(지원자 추적 시스템) 점수 분석 + 자기소개서 매칭 라우터
"""
import json
import google.generativeai as genai
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.utils.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/ats", tags=["ATS 분석"])

try:
    from app.config import config
    GEMINI_KEY = config.GEMINI_API_KEY
except Exception:
    GEMINI_KEY = ""


class ATSRequest(BaseModel):
    resume_text: str
    job_description: str
    job_title: Optional[str] = None


class ATSResponse(BaseModel):
    score: int  # 0-100
    matched_keywords: List[str]
    missing_keywords: List[str]
    improvement_tips: List[str]
    overall_feedback: str


class CoverLetterRequest(BaseModel):
    resume_text: str
    job_description: str
    company_name: str
    job_title: str
    tone: Optional[str] = "전문적"  # 전문적, 친근한, 열정적


@router.post("/score", response_model=ATSResponse)
async def analyze_ats_score(
    request: ATSRequest,
    current_user: User = Depends(get_current_user),
):
    """이력서 ATS 점수 분석"""
    if not GEMINI_KEY:
        raise HTTPException(500, "AI 서비스 설정이 필요합니다")

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""다음 이력서와 채용공고를 분석해서 ATS 점수를 평가해줘.

채용공고:
{request.job_description[:1000]}

이력서:
{request.resume_text[:1500]}

JSON으로 반환 (마크다운 없이):
{{
  "score": 75,
  "matched_keywords": ["Python", "FastAPI"],
  "missing_keywords": ["Docker", "Kubernetes"],
  "improvement_tips": ["Docker 경험 추가", "프로젝트 성과 수치화"],
  "overall_feedback": "전반적인 평가 2-3문장"
}}"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```"):
            text = text[text.find("{"):text.rfind("}") + 1]
        data = json.loads(text)
        return ATSResponse(**data)
    except Exception:
        raise HTTPException(500, "ATS 분석 중 오류가 발생했습니다")


@router.post("/cover-letter")
async def generate_cover_letter(
    request: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
):
    """맞춤형 자기소개서 생성"""
    if not GEMINI_KEY:
        raise HTTPException(500, "AI 서비스 설정이 필요합니다")

    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""다음 정보를 바탕으로 {request.tone} 톤의 자기소개서를 작성해줘.

회사: {request.company_name}
직무: {request.job_title}
채용공고 핵심 요구사항: {request.job_description[:500]}
지원자 이력: {request.resume_text[:800]}

800-1200자 분량의 자기소개서를 한국어로 작성해줘."""

    response = model.generate_content(prompt)
    return {
        "cover_letter": response.text,
        "company": request.company_name,
        "job_title": request.job_title,
    }
