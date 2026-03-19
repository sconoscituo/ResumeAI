# ResumeAI - AI 이력서/자기소개서 빌더

## 필요한 API 키 및 환경변수

| 환경변수 | 설명 | 발급 URL |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini AI API 키 (이력서 생성/분석용) | https://aistudio.google.com/app/apikey |
| `DATABASE_URL` | 데이터베이스 연결 URL (기본: SQLite) | - |
| `DEBUG` | 디버그 모드 활성화 여부 (`True` / `False`) | - |

## GitHub Secrets 설정

GitHub 저장소 → Settings → Secrets and variables → Actions → New repository secret

| Secret 이름 | 값 |
|---|---|
| `GEMINI_API_KEY` | Gemini API 키 |

## 로컬 개발 환경 설정

```bash
# 1. 저장소 클론
git clone https://github.com/sconoscituo/ResumeAI.git
cd ResumeAI

# 2. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 환경변수 설정
cp .env.example .env
# .env 파일을 열어 아래 항목 입력:
# GEMINI_API_KEY=your_gemini_api_key

# 5. 서버 실행
uvicorn app.main:app --reload
```

서버 기동 후 http://localhost:8000 에서 웹 UI를, http://localhost:8000/docs 에서 API 문서를 확인할 수 있습니다.

## Docker로 실행

```bash
docker-compose up --build
```

## 주요 기능 사용법

### AI 이력서 생성
- 사용자가 입력한 경력, 학력, 스킬 정보를 바탕으로 Gemini AI가 전문적인 이력서를 자동 작성합니다.
- 다양한 이력서 템플릿 중 선택 가능합니다.

### AI 자기소개서 작성
- 지원 직무와 회사 정보를 입력하면 맞춤형 자기소개서를 생성합니다.
- `beautifulsoup4`를 활용한 채용공고 파싱 기능을 지원합니다.

### PDF 내보내기
- `WeasyPrint`를 사용해 완성된 이력서/자소서를 PDF로 내보낼 수 있습니다.
- PDF 생성을 위해 시스템에 WeasyPrint 의존 라이브러리가 필요합니다:
  ```bash
  # Ubuntu/Debian
  sudo apt-get install libpango-1.0-0 libcairo2 libgdk-pixbuf2.0-0
  ```

### 파일 업로드
- 기존 이력서(PDF, DOCX 등)를 업로드하면 AI가 내용을 분석하고 개선안을 제안합니다.

## 프로젝트 구조

```
ResumeAI/
├── app/
│   ├── config.py       # 환경변수 설정
│   ├── database.py     # DB 연결 관리
│   ├── main.py         # FastAPI 앱 진입점
│   ├── models/         # SQLAlchemy 모델
│   ├── routers/        # API 라우터
│   ├── schemas/        # Pydantic 스키마
│   ├── services/       # 비즈니스 로직
│   ├── static/         # 정적 파일 (CSS, JS)
│   └── templates/      # Jinja2 HTML 템플릿
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
