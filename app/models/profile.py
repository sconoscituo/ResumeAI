"""사용자 프로필 관련 모델"""
import json
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Profile(Base):
    """사용자 프로필 (기본 정보)"""
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(String(300), nullable=True)
    summary: Mapped[str] = mapped_column(Text, nullable=True)  # 한 줄 소개
    github_url: Mapped[str] = mapped_column(String(300), nullable=True)
    linkedin_url: Mapped[str] = mapped_column(String(300), nullable=True)
    portfolio_url: Mapped[str] = mapped_column(String(300), nullable=True)
    # 기술 스택 (JSON 배열로 저장)
    skills: Mapped[str] = mapped_column(Text, nullable=True, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 관계
    educations: Mapped[list["Education"]] = relationship("Education", back_populates="profile", cascade="all, delete-orphan")
    careers: Mapped[list["Career"]] = relationship("Career", back_populates="profile", cascade="all, delete-orphan")
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="profile", cascade="all, delete-orphan")
    certificates: Mapped[list["Certificate"]] = relationship("Certificate", back_populates="profile", cascade="all, delete-orphan")
    resumes: Mapped[list["Resume"]] = relationship("Resume", back_populates="profile", cascade="all, delete-orphan")
    cover_letters: Mapped[list["CoverLetter"]] = relationship("CoverLetter", back_populates="profile", cascade="all, delete-orphan")
    job_postings: Mapped[list["JobPosting"]] = relationship("JobPosting", back_populates="profile", cascade="all, delete-orphan")

    def get_skills(self) -> list:
        """기술 스택 JSON 파싱"""
        try:
            return json.loads(self.skills or "[]")
        except Exception:
            return []

    def set_skills(self, skills: list):
        """기술 스택 JSON 저장"""
        self.skills = json.dumps(skills, ensure_ascii=False)


class Education(Base):
    """학력 사항"""
    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    school_name: Mapped[str] = mapped_column(String(200), nullable=False)   # 학교명
    major: Mapped[str] = mapped_column(String(200), nullable=True)          # 전공
    degree: Mapped[str] = mapped_column(String(50), nullable=True)          # 학위 (학사/석사/박사)
    start_date: Mapped[str] = mapped_column(String(20), nullable=True)      # 입학일 (YYYY-MM)
    end_date: Mapped[str] = mapped_column(String(20), nullable=True)        # 졸업일 (YYYY-MM 또는 "재학중")
    gpa: Mapped[str] = mapped_column(String(20), nullable=True)             # 학점
    description: Mapped[str] = mapped_column(Text, nullable=True)           # 추가 설명

    profile: Mapped["Profile"] = relationship("Profile", back_populates="educations")


class Career(Base):
    """경력 사항"""
    __tablename__ = "careers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)  # 회사명
    position: Mapped[str] = mapped_column(String(200), nullable=True)       # 직위/직책
    department: Mapped[str] = mapped_column(String(200), nullable=True)     # 부서
    start_date: Mapped[str] = mapped_column(String(20), nullable=True)      # 입사일 (YYYY-MM)
    end_date: Mapped[str] = mapped_column(String(20), nullable=True)        # 퇴사일 (YYYY-MM 또는 "재직중")
    description: Mapped[str] = mapped_column(Text, nullable=True)           # 담당 업무
    achievements: Mapped[str] = mapped_column(Text, nullable=True)          # 주요 성과

    profile: Mapped["Profile"] = relationship("Profile", back_populates="careers")


class Project(Base):
    """프로젝트 경험"""
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    project_name: Mapped[str] = mapped_column(String(200), nullable=False)  # 프로젝트명
    role: Mapped[str] = mapped_column(String(200), nullable=True)           # 역할
    start_date: Mapped[str] = mapped_column(String(20), nullable=True)
    end_date: Mapped[str] = mapped_column(String(20), nullable=True)
    tech_stack: Mapped[str] = mapped_column(Text, nullable=True)            # 사용 기술 (JSON)
    description: Mapped[str] = mapped_column(Text, nullable=True)           # 프로젝트 설명
    achievements: Mapped[str] = mapped_column(Text, nullable=True)          # 성과
    github_url: Mapped[str] = mapped_column(String(300), nullable=True)
    demo_url: Mapped[str] = mapped_column(String(300), nullable=True)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="projects")

    def get_tech_stack(self) -> list:
        try:
            return json.loads(self.tech_stack or "[]")
        except Exception:
            return []


class Certificate(Base):
    """자격증"""
    __tablename__ = "certificates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    profile_id: Mapped[int] = mapped_column(Integer, ForeignKey("profiles.id"), nullable=False)
    cert_name: Mapped[str] = mapped_column(String(200), nullable=False)     # 자격증명
    issuer: Mapped[str] = mapped_column(String(200), nullable=True)         # 발급기관
    issue_date: Mapped[str] = mapped_column(String(20), nullable=True)      # 취득일
    cert_number: Mapped[str] = mapped_column(String(100), nullable=True)    # 자격증 번호

    profile: Mapped["Profile"] = relationship("Profile", back_populates="certificates")
