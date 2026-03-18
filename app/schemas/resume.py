"""이력서/자소서 관련 Pydantic 스키마"""
from typing import Optional
from pydantic import BaseModel


class ResumeCreate(BaseModel):
    profile_id: int
    title: str
    company_name: Optional[str] = None
    position: Optional[str] = None
    job_posting: Optional[str] = None
    job_url: Optional[str] = None


class ResumeResponse(BaseModel):
    id: int
    profile_id: int
    title: str
    company_name: Optional[str] = None
    position: Optional[str] = None
    job_posting: Optional[str] = None
    job_url: Optional[str] = None
    job_keywords: Optional[str] = None
    generated_content: Optional[str] = None
    ats_score: Optional[int] = None
    ats_details: Optional[str] = None

    model_config = {"from_attributes": True}


class CoverLetterSectionCreate(BaseModel):
    section_type: str
    title: str
    word_limit: Optional[int] = None
    order: int = 0


class CoverLetterCreate(BaseModel):
    profile_id: int
    title: str
    company_name: Optional[str] = None
    position: Optional[str] = None
    job_posting: Optional[str] = None
    job_url: Optional[str] = None
    sections: list[CoverLetterSectionCreate] = []


class CoverLetterSectionResponse(BaseModel):
    id: int
    section_type: str
    title: str
    content: Optional[str] = None
    word_limit: Optional[int] = None
    order: int

    model_config = {"from_attributes": True}


class CoverLetterResponse(BaseModel):
    id: int
    profile_id: int
    title: str
    company_name: Optional[str] = None
    position: Optional[str] = None
    sections: list[CoverLetterSectionResponse] = []

    model_config = {"from_attributes": True}


class JobAnalysisRequest(BaseModel):
    job_url: Optional[str] = None
    job_text: Optional[str] = None


class ATSRequest(BaseModel):
    profile_id: int
    resume_id: int


class GenerateSectionRequest(BaseModel):
    cover_letter_id: int
    section_id: int
