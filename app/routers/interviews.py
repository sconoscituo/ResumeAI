"""면접 예상 질문 생성 API 라우터"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.cover_letter import CoverLetter
from app.routers.resumes import _get_profile_data
from app.services.interview_generator import generate_interview_questions

router = APIRouter(prefix="/api/interviews", tags=["면접 준비"])


class InterviewGenerateRequest(BaseModel):
    """면접 질문 생성 요청"""
    profile_id: int                     # 프로필 ID (필수)
    cover_letter_id: int | None = None  # 자소서 ID (선택)


@router.post("/generate")
async def generate_interview(
    data: InterviewGenerateRequest,
    db: AsyncSession = Depends(get_db),
):
    """자소서 + 이력서 기반 면접 예상 질문 10개 + 모범답변 생성"""
    # 프로필 데이터 로드
    profile_data = await _get_profile_data(data.profile_id, db)

    # 자소서 내용 로드 (선택)
    cover_letter_text = ""
    if data.cover_letter_id:
        stmt = (
            select(CoverLetter)
            .where(CoverLetter.id == data.cover_letter_id)
            .options(selectinload(CoverLetter.sections))
        )
        result = await db.execute(stmt)
        cl = result.scalar_one_or_none()
        if cl and cl.sections:
            # 모든 섹션 내용을 합쳐서 전달
            cover_letter_text = "\n\n".join(
                f"[{s.title}]\n{s.content or ''}"
                for s in cl.sections
                if s.content
            )

    # 면접 질문 생성
    questions_data = await generate_interview_questions(profile_data, cover_letter_text)

    if "error" in questions_data.get("questions", [{}])[0] if questions_data.get("questions") else {}:
        raise HTTPException(status_code=500, detail="면접 질문 생성에 실패했습니다.")

    return questions_data
