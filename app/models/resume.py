"""이력서 모델"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Resume(Base):
    """생성된 이력서"""
    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)         # 이력서 제목
    job_posting: Mapped[str] = mapped_column(Text, nullable=True)           # 채용공고 원문
    job_url: Mapped[str] = mapped_column(String(500), nullable=True)        # 채용공고 URL
    company_name: Mapped[str] = mapped_column(String(200), nullable=True)   # 지원 회사
    position: Mapped[str] = mapped_column(String(200), nullable=True)       # 지원 직무
    # AI가 분석한 채용공고 핵심 키워드 (JSON)
    job_keywords: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    # AI가 생성한 맞춤형 이력서 내용 (JSON)
    generated_content: Mapped[str] = mapped_column(Text, nullable=True)
    # ATS 점수
    ats_score: Mapped[int] = mapped_column(Integer, nullable=True)
    ats_details: Mapped[str] = mapped_column(Text, nullable=True)           # ATS 분석 상세 (JSON)
    pdf_path: Mapped[str] = mapped_column(String(500), nullable=True)       # 생성된 PDF 경로
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="resumes")
