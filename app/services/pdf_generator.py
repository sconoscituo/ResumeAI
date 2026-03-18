"""PDF 생성 서비스 (WeasyPrint)"""
import asyncio
import json
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS
from app.config import settings


# PDF 저장 디렉토리
PDF_DIR = Path("./pdfs")
PDF_DIR.mkdir(exist_ok=True)

# 지원하는 템플릿 목록
TEMPLATE_MAP = {
    "default":  "pdf/resume_template.html",   # 기본 스타일
    "modern":   "pdf/resume_modern.html",      # 모던 (컬러 헤더)
    "minimal":  "pdf/resume_minimal.html",     # 미니멀 (흑백)
    "creative": "pdf/resume_creative.html",    # 크리에이티브 (사이드바)
    "english":  "pdf/resume_english.html",     # 영문 이력서
}

TEMPLATE_LABELS = {
    "default":  "기본",
    "modern":   "모던",
    "minimal":  "미니멀",
    "creative": "크리에이티브",
    "english":  "영문",
}


def _from_json_filter(value):
    """Jinja2 커스텀 필터: JSON 문자열 → 파이썬 객체"""
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        return []


def get_jinja_env() -> Environment:
    """Jinja2 환경 설정 (PDF용 커스텀 필터 포함)"""
    templates_path = Path(__file__).parent.parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(templates_path)),
        autoescape=True,
    )
    env.filters["from_json"] = _from_json_filter
    return env


def _resolve_template(template_name: str) -> str:
    """템플릿 이름으로 실제 경로 반환 (없으면 기본값)"""
    return TEMPLATE_MAP.get(template_name, TEMPLATE_MAP["default"])


async def generate_resume_pdf(resume_id: int, resume_content: dict, profile_data: dict,
                               template_name: str = "default") -> str:
    """이력서 PDF 생성 및 저장, 파일 경로 반환"""
    env = get_jinja_env()
    tpl_path = _resolve_template(template_name)
    template = env.get_template(tpl_path)

    # 템플릿 렌더링
    html_content = template.render(
        resume=resume_content,
        profile=profile_data,
    )

    # PDF 생성
    pdf_filename = f"resume_{resume_id}_{template_name}.pdf"
    pdf_path = PDF_DIR / pdf_filename

    html_obj = HTML(string=html_content, base_url=str(Path(__file__).parent.parent))
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: html_obj.write_pdf(str(pdf_path)))

    return str(pdf_path)


async def generate_resume_pdf_bytes(resume_content: dict, profile_data: dict,
                                     template_name: str = "default") -> bytes:
    """이력서 PDF를 바이트로 반환 (다운로드용)"""
    env = get_jinja_env()
    tpl_path = _resolve_template(template_name)
    template = env.get_template(tpl_path)

    html_content = template.render(
        resume=resume_content,
        profile=profile_data,
    )

    html_obj = HTML(string=html_content, base_url=str(Path(__file__).parent.parent))
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, html_obj.write_pdf)
