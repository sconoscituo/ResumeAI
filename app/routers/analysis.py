"""ATS 분석 및 채용공고 분석 API 라우터"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.resume import Resume
from app.schemas.resume import JobAnalysisRequest, ATSRequest
from app.services.job_analyzer import fetch_job_posting, analyze_job_posting
from app.services.ats_scorer import calculate_ats_score
from app.routers.resumes import _get_profile_data

router = APIRouter(prefix="/api/analysis", tags=["분석"])


@router.post("/job-posting")
async def analyze_job(req: JobAnalysisRequest):
    """채용공고 URL 또는 텍스트 분석"""
    job_text = req.job_text or ""

    if req.job_url and not job_text:
        try:
            job_text = await fetch_job_posting(req.job_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"채용공고 URL 접근 실패: {str(e)}")

    if not job_text:
        raise HTTPException(status_code=400, detail="채용공고 URL 또는 텍스트를 입력하세요.")

    result = await analyze_job_posting(job_text)
    return {"job_text_preview": job_text[:300], "analysis": result}


@router.post("/ats-score")
async def ats_score(req: ATSRequest, db: AsyncSession = Depends(get_db)):
    """이력서 ATS 점수 계산"""
    # 이력서 조회
    result = await db.execute(select(Resume).where(Resume.id == req.resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")

    # 프로필 데이터
    profile_data = await _get_profile_data(req.profile_id, db)

    # 채용공고 분석 (이미 저장된 경우 재사용)
    job_analysis = {}
    if resume.job_posting:
        job_analysis = await analyze_job_posting(resume.job_posting)

    # ATS 점수 계산
    ats_result = await calculate_ats_score(profile_data, job_analysis)

    # 결과 저장
    resume.ats_score = ats_result.get("overall_score", 0)
    resume.ats_details = json.dumps(ats_result, ensure_ascii=False)
    await db.commit()

    return {
        "resume_id": req.resume_id,
        "ats_score": resume.ats_score,
        "details": ats_result,
    }


@router.get("/ats-score/{resume_id}")
async def get_ats_score(resume_id: int, db: AsyncSession = Depends(get_db)):
    """저장된 ATS 점수 조회"""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")

    if resume.ats_score is None:
        raise HTTPException(status_code=404, detail="ATS 분석 결과가 없습니다. 먼저 분석을 실행하세요.")

    details = {}
    if resume.ats_details:
        try:
            details = json.loads(resume.ats_details)
        except Exception:
            pass

    return {
        "resume_id": resume_id,
        "ats_score": resume.ats_score,
        "details": details,
    }
