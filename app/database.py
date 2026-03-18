"""데이터베이스 설정 및 세션 관리"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

# SQLite일 때만 check_same_thread=False 적용
_connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    _connect_args = {"check_same_thread": False}

# 비동기 엔진 생성
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args=_connect_args,
)

# 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """모든 모델의 기본 클래스"""
    pass


async def get_db() -> AsyncSession:
    """DB 세션 의존성 주입"""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """테이블 초기화 (앱 시작 시 실행)"""
    # 모든 모델을 import해서 Base.metadata에 등록
    from app.models import profile, resume, cover_letter  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
