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


async def generate_resume_pdf(resume_id: int, resume_content: dict, profile_data: dict) -> str:
    """이력서 PDF 생성 및 저장, 파일 경로 반환"""
    env = get_jinja_env()
    template = env.get_template("pdf/resume_template.html")

    # 템플릿 렌더링
    html_content = template.render(
        resume=resume_content,
        profile=profile_data,
    )

    # PDF 생성
    pdf_filename = f"resume_{resume_id}.pdf"
    pdf_path = PDF_DIR / pdf_filename

    html_obj = HTML(string=html_content, base_url=str(Path(__file__).parent.parent))
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: html_obj.write_pdf(str(pdf_path)))

    return str(pdf_path)


async def generate_resume_pdf_bytes(resume_content: dict, profile_data: dict) -> bytes:
    """이력서 PDF를 바이트로 반환 (다운로드용)"""
    env = get_jinja_env()
    template = env.get_template("pdf/resume_template.html")

    html_content = template.render(
        resume=resume_content,
        profile=profile_data,
    )

    html_obj = HTML(string=html_content, base_url=str(Path(__file__).parent.parent))
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, html_obj.write_pdf)
