"""채용공고 검색/목록/자동 매칭 API 라우터"""
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.profile import Profile
from app.routers.resumes import _get_profile_data
from app.services.job_crawler import fetch_jobs_with_matching

router = APIRouter(prefix="/api/jobs", tags=["채용공고"])


@router.get("/search")
async def search_jobs(
    keyword: str = Query(..., description="검색 키워드 (예: 백엔드, Python, 데이터분석)"),
    profile_id: Optional[int] = Query(None, description="매칭 점수 계산을 위한 프로필 ID"),
    limit: int = Query(10, ge=1, le=20, description="결과 개수"),
    db: AsyncSession = Depends(get_db),
):
    """키워드 기반 채용공고 검색 + 프로필 매칭 점수"""
    profile_data = None
    if profile_id:
        try:
            profile_data = await _get_profile_data(profile_id, db)
        except Exception:
            profile_data = None

    jobs = await fetch_jobs_with_matching(keyword, profile_data, limit)
    return {"keyword": keyword, "total": len(jobs), "jobs": jobs}


@router.get("/profiles")
async def list_profiles_for_jobs(db: AsyncSession = Depends(get_db)):
    """채용공고 검색에 사용할 프로필 목록"""
    result = await db.execute(select(Profile).order_by(Profile.created_at.desc()))
    profiles = result.scalars().all()
    return [{"id": p.id, "name": p.name, "email": p.email} for p in profiles]
