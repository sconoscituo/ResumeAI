"""채용공고 모델"""
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobPosting(Base):
    """수집된 채용공고"""
    __tablename__ = "job_postings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)          # 채용 직무명
    company: Mapped[str] = mapped_column(String(200), nullable=True)         # 회사명
    url: Mapped[str] = mapped_column(String(500), nullable=True)             # 채용공고 URL
    description: Mapped[str] = mapped_column(Text, nullable=True)            # 채용공고 내용
    deadline: Mapped[str] = mapped_column(String(100), nullable=True)        # 마감일
    source: Mapped[str] = mapped_column(String(50), nullable=True)           # 수집 출처 (사람인/잡코리아 등)
    keyword: Mapped[str] = mapped_column(String(200), nullable=True)         # 검색에 사용된 키워드
    matched_score: Mapped[int] = mapped_column(Integer, nullable=True, default=0)  # 프로필 매칭 점수 (0~100)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=True)  # 매칭된 프로필
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    profile: Mapped["Profile"] = relationship("Profile", back_populates="job_postings")
