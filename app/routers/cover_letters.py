"""자기소개서 생성/관리 API 라우터"""
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.cover_letter import CoverLetter, CoverLetterSection
from app.models.profile import Profile, Education, Career, Project, Certificate
from app.schemas.resume import (
    CoverLetterCreate, CoverLetterResponse,
    CoverLetterSectionResponse, GenerateSectionRequest,
)
from app.services.job_analyzer import fetch_job_posting, analyze_job_posting
from app.services.cover_letter_generator import generate_section
from app.services.proofreader import proofread_text
from app.routers.resumes import _get_profile_data

router = APIRouter(prefix="/api/cover-letters", tags=["자기소개서"])


async def _load_cover_letter(cover_letter_id: int, db: AsyncSession) -> CoverLetter:
    stmt = (
        select(CoverLetter)
        .where(CoverLetter.id == cover_letter_id)
        .options(selectinload(CoverLetter.sections))
    )
    result = await db.execute(stmt)
    cl = result.scalar_one_or_none()
    if not cl:
        raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")
    return cl


@router.get("/", response_model=list[CoverLetterResponse])
async def list_cover_letters(db: AsyncSession = Depends(get_db)):
    """자기소개서 목록 조회"""
    stmt = (
        select(CoverLetter)
        .options(selectinload(CoverLetter.sections))
        .order_by(CoverLetter.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=CoverLetterResponse, status_code=201)
async def create_cover_letter(data: CoverLetterCreate, db: AsyncSession = Depends(get_db)):
    """자기소개서 생성 (항목 구조만 생성, AI 내용은 별도 요청)"""
    job_text = data.job_posting or ""
    if data.job_url and not job_text:
        try:
            job_text = await fetch_job_posting(data.job_url)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"채용공고 URL 접근 실패: {str(e)}")

    cl = CoverLetter(
        profile_id=data.profile_id,
        title=data.title,
        company_name=data.company_name,
        position=data.position,
        job_posting=job_text,
        job_url=data.job_url,
    )
    db.add(cl)
    await db.flush()  # ID 확보

    # 항목 생성
    for i, sec_data in enumerate(data.sections):
        section = CoverLetterSection(
            cover_letter_id=cl.id,
            section_type=sec_data.section_type,
            title=sec_data.title,
            word_limit=sec_data.word_limit,
            order=sec_data.order if sec_data.order else i,
        )
        db.add(section)

    await db.commit()
    return await _load_cover_letter(cl.id, db)


@router.get("/{cl_id}", response_model=CoverLetterResponse)
async def get_cover_letter(cl_id: int, db: AsyncSession = Depends(get_db)):
    """자기소개서 상세 조회"""
    return await _load_cover_letter(cl_id, db)


@router.post("/{cl_id}/generate-all", response_model=CoverLetterResponse)
async def generate_all_sections(cl_id: int, db: AsyncSession = Depends(get_db)):
    """모든 항목 AI 생성"""
    cl = await _load_cover_letter(cl_id, db)
    profile_data = await _get_profile_data(cl.profile_id, db)

    # 채용공고 분석
    job_analysis = {}
    if cl.job_posting:
        job_analysis = await analyze_job_posting(cl.job_posting)

    # 각 섹션 AI 생성
    for section in cl.sections:
        content = await generate_section(
            section_type=section.section_type,
            section_title=section.title,
            profile_data=profile_data,
            job_analysis=job_analysis,
            word_limit=section.word_limit or 500,
        )
        section.content = content

    await db.commit()
    return await _load_cover_letter(cl_id, db)


@router.post("/generate-section", response_model=CoverLetterSectionResponse)
async def generate_single_section(req: GenerateSectionRequest, db: AsyncSession = Depends(get_db)):
    """특정 항목만 AI 재생성"""
    cl = await _load_cover_letter(req.cover_letter_id, db)
    profile_data = await _get_profile_data(cl.profile_id, db)

    # 섹션 찾기
    section = next((s for s in cl.sections if s.id == req.section_id), None)
    if not section:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    # 채용공고 분석
    job_analysis = {}
    if cl.job_posting:
        job_analysis = await analyze_job_posting(cl.job_posting)

    content = await generate_section(
        section_type=section.section_type,
        section_title=section.title,
        profile_data=profile_data,
        job_analysis=job_analysis,
        word_limit=section.word_limit or 500,
    )
    section.content = content
    await db.commit()
    await db.refresh(section)
    return section


@router.put("/{cl_id}/sections/{section_id}/content")
async def update_section_content(
    cl_id: int,
    section_id: int,
    payload: dict,
    db: AsyncSession = Depends(get_db),
):
    """항목 내용 수동 수정"""
    result = await db.execute(
        select(CoverLetterSection).where(
            CoverLetterSection.id == section_id,
            CoverLetterSection.cover_letter_id == cl_id,
        )
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    section.content = payload.get("content", section.content)
    await db.commit()
    await db.refresh(section)
    return {"id": section.id, "content": section.content}


@router.post("/{cl_id}/proofread")
async def proofread_cover_letter(cl_id: int, db: AsyncSession = Depends(get_db)):
    """자소서 전체 내용 맞춤법/문법/문체 교정"""
    cl = await _load_cover_letter(cl_id, db)

    # 내용이 있는 섹션만 합쳐서 교정
    full_text = "\n\n".join(
        f"[{s.title}]\n{s.content}"
        for s in cl.sections
        if s.content and s.content.strip()
    )

    if not full_text.strip():
        raise HTTPException(status_code=400, detail="교정할 내용이 없습니다. 먼저 자소서를 생성하세요.")

    result = await proofread_text(full_text)
    return result


@router.post("/{cl_id}/sections/{section_id}/proofread")
async def proofread_section(cl_id: int, section_id: int, db: AsyncSession = Depends(get_db)):
    """자소서 특정 섹션 맞춤법/문법/문체 교정"""
    result_q = await db.execute(
        select(CoverLetterSection).where(
            CoverLetterSection.id == section_id,
            CoverLetterSection.cover_letter_id == cl_id,
        )
    )
    section = result_q.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다.")

    if not section.content or not section.content.strip():
        raise HTTPException(status_code=400, detail="교정할 내용이 없습니다.")

    result = await proofread_text(section.content)
    return result


@router.delete("/{cl_id}", status_code=204)
async def delete_cover_letter(cl_id: int, db: AsyncSession = Depends(get_db)):
    """자기소개서 삭제"""
    result = await db.execute(select(CoverLetter).where(CoverLetter.id == cl_id))
    cl = result.scalar_one_or_none()
    if not cl:
        raise HTTPException(status_code=404, detail="자기소개서를 찾을 수 없습니다.")
    await db.delete(cl)
    await db.commit()
