"""이력서 생성/관리 API 라우터"""
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import io

from app.database import get_db
from app.models.resume import Resume
from app.models.profile import Profile, Education, Career, Project, Certificate
from app.schemas.resume import ResumeCreate, ResumeResponse
from app.services.job_analyzer import fetch_job_posting, analyze_job_posting
from app.services.resume_generator import build_resume_content
from app.services.pdf_generator import generate_resume_pdf_bytes

router = APIRouter(prefix="/api/resumes", tags=["이력서"])


async def _get_profile_data(profile_id: int, db: AsyncSession) -> dict:
    """프로필 데이터를 딕셔너리로 반환"""
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

    return {
        "name": profile.name,
        "email": profile.email,
        "phone": profile.phone or "",
        "address": profile.address or "",
        "summary": profile.summary or "",
        "github_url": profile.github_url or "",
        "linkedin_url": profile.linkedin_url or "",
        "portfolio_url": profile.portfolio_url or "",
        "skills_list": profile.get_skills(),
        "educations": [
            {
                "school_name": e.school_name,
                "major": e.major or "",
                "degree": e.degree or "",
                "start_date": e.start_date or "",
                "end_date": e.end_date or "",
                "gpa": e.gpa or "",
                "description": e.description or "",
            }
            for e in profile.educations
        ],
        "careers": [
            {
                "company_name": c.company_name,
                "position": c.position or "",
                "department": c.department or "",
                "start_date": c.start_date or "",
                "end_date": c.end_date or "",
                "description": c.description or "",
                "achievements": c.achievements or "",
            }
            for c in profile.careers
        ],
        "projects": [
            {
                "project_name": p.project_name,
                "role": p.role or "",
                "start_date": p.start_date or "",
                "end_date": p.end_date or "",
                "tech_stack": p.tech_stack or "[]",
                "description": p.description or "",
                "achievements": p.achievements or "",
                "github_url": p.github_url or "",
                "demo_url": p.demo_url or "",
            }
            for p in profile.projects
        ],
        "certificates": [
            {
                "cert_name": c.cert_name,
                "issuer": c.issuer or "",
                "issue_date": c.issue_date or "",
            }
            for c in profile.certificates
        ],
    }


@router.get("/", response_model=list[ResumeResponse])
async def list_resumes(db: AsyncSession = Depends(get_db)):
    """이력서 목록 조회"""
    result = await db.execute(select(Resume).order_by(Resume.created_at.desc()))
    return result.scalars().all()


@router.post("/generate", response_model=ResumeResponse, status_code=201)
async def generate_resume(data: ResumeCreate, db: AsyncSession = Depends(get_db)):
    """채용공고 기반 맞춤형 이력서 생성"""
    # 1. 채용공고 분석
    job_text = data.job_posting or ""
    if data.job_url and not job_text:
        try:
            job_text = await fetch_job_posting(data.job_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"채용공고 URL 접근 실패: {str(e)}")

    job_analysis = {}
    if job_text:
        job_analysis = await analyze_job_posting(job_text)

    # 2. 프로필 데이터 로드
    profile_data = await _get_profile_data(data.profile_id, db)

    # 3. 이력서 콘텐츠 생성
    resume_content = await build_resume_content(profile_data, job_analysis)

    # 4. DB 저장
    resume = Resume(
        profile_id=data.profile_id,
        title=data.title,
        company_name=data.company_name or job_analysis.get("company_name", ""),
        position=data.position or job_analysis.get("position", ""),
        job_posting=job_text,
        job_url=data.job_url,
        job_keywords=json.dumps(job_analysis.get("keywords", []), ensure_ascii=False),
        generated_content=json.dumps(resume_content, ensure_ascii=False),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    """이력서 상세 조회"""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")
    return resume


@router.get("/{resume_id}/pdf")
async def download_resume_pdf(resume_id: int, db: AsyncSession = Depends(get_db)):
    """이력서 PDF 다운로드"""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")

    if not resume.generated_content:
        raise HTTPException(status_code=400, detail="이력서 콘텐츠가 없습니다. 먼저 이력서를 생성하세요.")

    profile_data = await _get_profile_data(resume.profile_id, db)
    resume_content = json.loads(resume.generated_content)

    pdf_bytes = await generate_resume_pdf_bytes(resume_content, profile_data)

    filename = f"이력서_{resume.company_name or 'resume'}_{resume_id}.pdf"
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename.encode().hex()}"},
    )


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(resume_id: int, db: AsyncSession = Depends(get_db)):
    """이력서 삭제"""
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")
    await db.delete(resume)
    await db.commit()
