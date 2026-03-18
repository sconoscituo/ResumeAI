"""프로필 관련 Pydantic 스키마"""
from typing import Optional
from pydantic import BaseModel


class EducationBase(BaseModel):
    school_name: str
    major: Optional[str] = None
    degree: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    gpa: Optional[str] = None
    description: Optional[str] = None


class EducationCreate(EducationBase):
    pass


class EducationResponse(EducationBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


class CareerBase(BaseModel):
    company_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    achievements: Optional[str] = None


class CareerCreate(CareerBase):
    pass


class CareerResponse(CareerBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    project_name: str
    role: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    tech_stack: Optional[str] = None  # JSON 문자열
    description: Optional[str] = None
    achievements: Optional[str] = None
    github_url: Optional[str] = None
    demo_url: Optional[str] = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


class CertificateBase(BaseModel):
    cert_name: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    cert_number: Optional[str] = None


class CertificateCreate(CertificateBase):
    pass


class CertificateResponse(CertificateBase):
    id: int
    profile_id: int

    model_config = {"from_attributes": True}


class ProfileBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    summary: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    skills: Optional[str] = "[]"  # JSON 문자열


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    name: Optional[str] = None
    email: Optional[str] = None


class ProfileResponse(ProfileBase):
    id: int
    educations: list[EducationResponse] = []
    careers: list[CareerResponse] = []
    projects: list[ProjectResponse] = []
    certificates: list[CertificateResponse] = []

    model_config = {"from_attributes": True}
