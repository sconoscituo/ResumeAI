"""FastAPI 애플리케이션 진입점"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.config import settings
from app.database import init_db
from app.routers import profiles, resumes, cover_letters, analysis, pages
from app.routers import interviews, jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 이벤트"""
    # DB 테이블 초기화
    await init_db()
    # PDF 저장 디렉토리 생성
    Path("./pdfs").mkdir(exist_ok=True)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI 기반 이력서 및 자기소개서 자동 생성 서비스",
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 서빙
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# 라우터 등록
app.include_router(pages.router)           # HTML 페이지 (최우선)
app.include_router(profiles.router)        # 프로필 API
app.include_router(resumes.router)         # 이력서 API
app.include_router(cover_letters.router)   # 자소서 API
app.include_router(analysis.router)        # 분석 API
app.include_router(interviews.router)      # 면접 준비 API
app.include_router(jobs.router)            # 채용공고 API
