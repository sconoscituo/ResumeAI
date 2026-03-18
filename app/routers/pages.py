"""HTML 페이지 라우터 (Jinja2 템플릿 렌더링)"""
import json
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pathlib import Path

from app.database import get_db
from app.models.profile import Profile
from app.models.resume import Resume
from app.models.cover_letter import CoverLetter, SECTION_TYPES

router = APIRouter(tags=["페이지"])

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))


@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """메인 대시보드"""
    # 프로필 목록
    profiles_result = await db.execute(select(Profile).order_by(Profile.created_at.desc()))
    profiles = profiles_result.scalars().all()

    # 최근 이력서
    resumes_result = await db.execute(
        select(Resume).order_by(Resume.created_at.desc()).limit(5)
    )
    resumes = resumes_result.scalars().all()

    # 최근 자소서
    cl_result = await db.execute(
        select(CoverLetter)
        .options(selectinload(CoverLetter.sections))
        .order_by(CoverLetter.created_at.desc())
        .limit(5)
    )
    cover_letters = cl_result.scalars().all()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "profiles": profiles,
        "resumes": resumes,
        "cover_letters": cover_letters,
    })


@router.get("/profiles/new", response_class=HTMLResponse)
async def new_profile_page(request: Request):
    """새 프로필 입력 페이지"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": None,
        "mode": "create",
    })


@router.get("/profiles/{profile_id}", response_class=HTMLResponse)
async def profile_page(request: Request, profile_id: int, db: AsyncSession = Depends(get_db)):
    """프로필 상세/수정 페이지"""
    stmt = (
        select(Profile)
        .where(Profile.id == profile_id)
        .options(
            selectinload(Profile.educations),
            selectinload(Profile.careers),
            selectinload(Profile.projects),
            selectinload(Profile.certificates),
        )
    )
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")

    return templates.TemplateResponse("profile.html", {
        "request": request,
        "profile": profile,
        "skills": profile.get_skills(),
        "mode": "edit",
    })


@router.get("/resumes/new", response_class=HTMLResponse)
async def new_resume_page(request: Request, db: AsyncSession = Depends(get_db)):
    """새 이력서 생성 페이지"""
    profiles_result = await db.execute(select(Profile))
    profiles = profiles_result.scalars().all()

    return templates.TemplateResponse("resume.html", {
        "request": request,
        "profiles": profiles,
        "resume": None,
        "mode": "create",
    })


@router.get("/resumes/{resume_id}", response_class=HTMLResponse)
async def resume_page(request: Request, resume_id: int, db: AsyncSession = Depends(get_db)):
    """이력서 상세/미리보기 페이지"""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")

    resume_content = {}
    if resume.generated_content:
        try:
            resume_content = json.loads(resume.generated_content)
        except Exception:
            pass

    job_keywords = []
    if resume.job_keywords:
        try:
            job_keywords = json.loads(resume.job_keywords)
        except Exception:
            pass

    profiles_result = await db.execute(select(Profile))
    profiles = profiles_result.scalars().all()

    return templates.TemplateResponse("resume.html", {
        "request": request,
        "resume": resume,
        "resume_content": resume_content,
        "job_keywords": job_keywords,
        "profiles": profiles,
        "mode": "view",
    })


@router.get("/cover-letters/new", response_class=HTMLResponse)
async def new_cover_letter_page(request: Request, db: AsyncSession = Depends(get_db)):
    """새 자소서 생성 페이지"""
    profiles_result = await db.execute(select(Profile))
    profiles = profiles_result.scalars().all()

    return templates.TemplateResponse("cover_letter.html", {
        "request": request,
        "profiles": profiles,
        "cover_letter": None,
        "section_types": SECTION_TYPES,
        "mode": "create",
    })


@router.get("/cover-letters/{cl_id}", response_class=HTMLResponse)
async def cover_letter_page(request: Request, cl_id: int, db: AsyncSession = Depends(get_db)):
    """자소서 상세/편집 페이지"""
    stmt = (
        select(CoverLetter)
        .where(CoverLetter.id == cl_id)
        .options(selectinload(CoverLetter.sections))
    )
    result = await db.execute(stmt)
    cl = result.scalar_one_or_none()
    if not cl:
        raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")

    profiles_result = await db.execute(select(Profile))
    profiles = profiles_result.scalars().all()

    return templates.TemplateResponse("cover_letter.html", {
        "request": request,
        "cover_letter": cl,
        "sections": cl.sections,
        "profiles": profiles,
        "section_types": SECTION_TYPES,
        "mode": "edit",
    })


@router.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request, db: AsyncSession = Depends(get_db)):
    """ATS 분석 페이지"""
    profiles_result = await db.execute(select(Profile))
    profiles = profiles_result.scalars().all()

    resumes_result = await db.execute(select(Resume).order_by(Resume.created_at.desc()))
    resumes = resumes_result.scalars().all()

    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "profiles": profiles,
        "resumes": resumes,
    })
