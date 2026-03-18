"""프로필(경력사항) 관리 API 라우터"""
import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.profile import Profile, Education, Career, Project, Certificate
from app.schemas.profile import (
    ProfileCreate, ProfileUpdate, ProfileResponse,
    EducationCreate, EducationResponse,
    CareerCreate, CareerResponse,
    ProjectCreate, ProjectResponse,
    CertificateCreate, CertificateResponse,
)

router = APIRouter(prefix="/api/profiles", tags=["프로필"])


def _load_profile_with_relations(stmt):
    return stmt.options(
        selectinload(Profile.educations),
        selectinload(Profile.careers),
        selectinload(Profile.projects),
        selectinload(Profile.certificates),
    )


@router.get("/", response_model=list[ProfileResponse])
async def list_profiles(db: AsyncSession = Depends(get_db)):
    """프로필 목록 조회"""
    stmt = _load_profile_with_relations(select(Profile))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(data: ProfileCreate, db: AsyncSession = Depends(get_db)):
    """새 프로필 생성"""
    profile = Profile(
        name=data.name,
        email=data.email,
        phone=data.phone,
        address=data.address,
        summary=data.summary,
        github_url=data.github_url,
        linkedin_url=data.linkedin_url,
        portfolio_url=data.portfolio_url,
        skills=data.skills or "[]",
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)

    # 관계 로드
    stmt = _load_profile_with_relations(select(Profile).where(Profile.id == profile.id))
    result = await db.execute(stmt)
    return result.scalar_one()


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    """프로필 상세 조회"""
    stmt = _load_profile_with_relations(select(Profile).where(Profile.id == profile_id))
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    return profile


@router.put("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: int, data: ProfileUpdate, db: AsyncSession = Depends(get_db)):
    """프로필 수정"""
    stmt = select(Profile).where(Profile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.commit()

    stmt = _load_profile_with_relations(select(Profile).where(Profile.id == profile_id))
    result = await db.execute(stmt)
    return result.scalar_one()


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    """프로필 삭제"""
    result = await db.execute(select(Profile).where(Profile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    await db.delete(profile)
    await db.commit()


# --- 학력 ---
@router.post("/{profile_id}/educations", response_model=EducationResponse, status_code=201)
async def add_education(profile_id: int, data: EducationCreate, db: AsyncSession = Depends(get_db)):
    """학력 추가"""
    edu = Education(profile_id=profile_id, **data.model_dump())
    db.add(edu)
    await db.commit()
    await db.refresh(edu)
    return edu


@router.put("/{profile_id}/educations/{edu_id}", response_model=EducationResponse)
async def update_education(profile_id: int, edu_id: int, data: EducationCreate, db: AsyncSession = Depends(get_db)):
    """학력 수정"""
    result = await db.execute(select(Education).where(Education.id == edu_id, Education.profile_id == profile_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="학력 정보를 찾을 수 없습니다.")
    for k, v in data.model_dump().items():
        setattr(edu, k, v)
    await db.commit()
    await db.refresh(edu)
    return edu


@router.delete("/{profile_id}/educations/{edu_id}", status_code=204)
async def delete_education(profile_id: int, edu_id: int, db: AsyncSession = Depends(get_db)):
    """학력 삭제"""
    result = await db.execute(select(Education).where(Education.id == edu_id, Education.profile_id == profile_id))
    edu = result.scalar_one_or_none()
    if not edu:
        raise HTTPException(status_code=404, detail="학력 정보를 찾을 수 없습니다.")
    await db.delete(edu)
    await db.commit()


# --- 경력 ---
@router.post("/{profile_id}/careers", response_model=CareerResponse, status_code=201)
async def add_career(profile_id: int, data: CareerCreate, db: AsyncSession = Depends(get_db)):
    """경력 추가"""
    career = Career(profile_id=profile_id, **data.model_dump())
    db.add(career)
    await db.commit()
    await db.refresh(career)
    return career


@router.put("/{profile_id}/careers/{career_id}", response_model=CareerResponse)
async def update_career(profile_id: int, career_id: int, data: CareerCreate, db: AsyncSession = Depends(get_db)):
    """경력 수정"""
    result = await db.execute(select(Career).where(Career.id == career_id, Career.profile_id == profile_id))
    career = result.scalar_one_or_none()
    if not career:
        raise HTTPException(status_code=404, detail="경력 정보를 찾을 수 없습니다.")
    for k, v in data.model_dump().items():
        setattr(career, k, v)
    await db.commit()
    await db.refresh(career)
    return career


@router.delete("/{profile_id}/careers/{career_id}", status_code=204)
async def delete_career(profile_id: int, career_id: int, db: AsyncSession = Depends(get_db)):
    """경력 삭제"""
    result = await db.execute(select(Career).where(Career.id == career_id, Career.profile_id == profile_id))
    career = result.scalar_one_or_none()
    if not career:
        raise HTTPException(status_code=404, detail="경력 정보를 찾을 수 없습니다.")
    await db.delete(career)
    await db.commit()


# --- 프로젝트 ---
@router.post("/{profile_id}/projects", response_model=ProjectResponse, status_code=201)
async def add_project(profile_id: int, data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """프로젝트 추가"""
    project = Project(profile_id=profile_id, **data.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


@router.put("/{profile_id}/projects/{proj_id}", response_model=ProjectResponse)
async def update_project(profile_id: int, proj_id: int, data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    """프로젝트 수정"""
    result = await db.execute(select(Project).where(Project.id == proj_id, Project.profile_id == profile_id))
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="프로젝트 정보를 찾을 수 없습니다.")
    for k, v in data.model_dump().items():
        setattr(proj, k, v)
    await db.commit()
    await db.refresh(proj)
    return proj


@router.delete("/{profile_id}/projects/{proj_id}", status_code=204)
async def delete_project(profile_id: int, proj_id: int, db: AsyncSession = Depends(get_db)):
    """프로젝트 삭제"""
    result = await db.execute(select(Project).where(Project.id == proj_id, Project.profile_id == profile_id))
    proj = result.scalar_one_or_none()
    if not proj:
        raise HTTPException(status_code=404, detail="프로젝트 정보를 찾을 수 없습니다.")
    await db.delete(proj)
    await db.commit()


# --- 자격증 ---
@router.post("/{profile_id}/certificates", response_model=CertificateResponse, status_code=201)
async def add_certificate(profile_id: int, data: CertificateCreate, db: AsyncSession = Depends(get_db)):
    """자격증 추가"""
    cert = Certificate(profile_id=profile_id, **data.model_dump())
    db.add(cert)
    await db.commit()
    await db.refresh(cert)
    return cert


@router.put("/{profile_id}/certificates/{cert_id}", response_model=CertificateResponse)
async def update_certificate(profile_id: int, cert_id: int, data: CertificateCreate, db: AsyncSession = Depends(get_db)):
    """자격증 수정"""
    result = await db.execute(select(Certificate).where(Certificate.id == cert_id, Certificate.profile_id == profile_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="자격증 정보를 찾을 수 없습니다.")
    for k, v in data.model_dump().items():
        setattr(cert, k, v)
    await db.commit()
    await db.refresh(cert)
    return cert


@router.delete("/{profile_id}/certificates/{cert_id}", status_code=204)
async def delete_certificate(profile_id: int, cert_id: int, db: AsyncSession = Depends(get_db)):
    """자격증 삭제"""
    result = await db.execute(select(Certificate).where(Certificate.id == cert_id, Certificate.profile_id == profile_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(status_code=404, detail="자격증 정보를 찾을 수 없습니다.")
    await db.delete(cert)
    await db.commit()
