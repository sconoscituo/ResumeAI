"""ResumeAI 기본 헬스체크 테스트"""
import os
import pytest
from httpx import AsyncClient, ASGITransport

os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test_resumeai.db")


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_app_is_created():
    """앱 인스턴스가 정상적으로 생성되는지 확인"""
    from app.main import app
    assert app is not None
    assert "ResumeAI" in app.title


@pytest.mark.anyio
async def test_openapi_schema():
    """OpenAPI 스키마 엔드포인트가 응답하는지 확인"""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert "openapi" in data
    assert "ResumeAI" in data["info"]["title"]


@pytest.mark.anyio
async def test_docs_endpoint():
    """Swagger UI 문서 페이지가 응답하는지 확인"""
    from app.main import app
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/docs")
    assert response.status_code == 200


@pytest.mark.anyio
async def test_resumes_api_exists():
    """이력서 API 엔드포인트가 등록되어 있는지 확인"""
    from app.main import app
    routes = [route.path for route in app.routes]
    assert any("/api/resumes" in r or "/resumes" in r for r in routes)


@pytest.mark.anyio
async def test_cover_letters_api_exists():
    """자소서 API 엔드포인트가 등록되어 있는지 확인"""
    from app.main import app
    routes = [route.path for route in app.routes]
    assert any("/api/cover-letters" in r or "/cover-letters" in r for r in routes)
