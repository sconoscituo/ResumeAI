"""애플리케이션 설정 모듈"""
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """환경 변수 기반 설정"""
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./resumeai.db")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    APP_NAME: str = "ResumeAI - AI 이력서/자소서 빌더"
    APP_VERSION: str = "1.0.0"


settings = Settings()
