"""자기소개서 모델"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CoverLetter(Base):
    """자기소개서 (여러 항목으로 구성)"""
    __tablename__ = "cover_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)         # 자소서 제목
    company_name: Mapped[str] = mapped_column(String(200), nullable=True)   # 지원 회사
    position: Mapped[str] = mapped_column(String(200), nullable=True)       # 지원 직무
    job_posting: Mapped[str] = mapped_column(Text, nullable=True)           # 채용공고 원문
    job_url: Mapped[str] = mapped_column(String(500), nullable=True)        # 채용공고 URL
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="cover_letters")
    sections: Mapped[list["CoverLetterSection"]] = relationship(
        "CoverLetterSection", back_populates="cover_letter", cascade="all, delete-orphan", order_by="CoverLetterSection.order"
    )


class CoverLetterSection(Base):
    """자기소개서 항목 (지원동기, 성장과정 등)"""
    __tablename__ = "cover_letter_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cover_letter_id: Mapped[int] = mapped_column(Integer, ForeignKey("cover_letters.id"), nullable=False)
    section_type: Mapped[str] = mapped_column(String(100), nullable=False)  # 항목 유형 (motivation, growth, aspiration 등)
    title: Mapped[str] = mapped_column(String(300), nullable=False)         # 항목 제목
    content: Mapped[str] = mapped_column(Text, nullable=True)               # AI 생성 내용
    word_limit: Mapped[int] = mapped_column(Integer, nullable=True)         # 글자 수 제한
    order: Mapped[int] = mapped_column(Integer, default=0)                  # 순서

    cover_letter: Mapped["CoverLetter"] = relationship("CoverLetter", back_populates="sections")


# 자기소개서 항목 유형 정의
SECTION_TYPES = {
    "motivation": "지원동기",
    "growth": "성장과정",
    "personality": "성격의 장단점",
    "aspiration": "입사 후 포부",
    "achievement": "주요 성과 및 경험",
    "teamwork": "협력/팀워크 경험",
    "challenge": "도전/극복 경험",
    "custom": "직접 입력",
}
