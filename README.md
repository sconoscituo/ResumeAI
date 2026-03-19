# ResumeAI - AI 이력서/자소서 빌더

> 경력을 입력하면 Gemini AI가 직무별 최적화된 이력서와 자기소개서를 자동으로 생성해주는 서비스

## 소개

ResumeAI는 기본 경력 정보를 입력하면 지원하는 직무에 맞춰 Gemini AI가 이력서와 자기소개서를 자동 생성해주는 AI 빌더입니다. ATS(채용 시스템) 최적화 분석과 면접 준비 기능까지 제공합니다.

## 주요 기능

- 경력/학력 입력 → Gemini AI가 직무별 이력서 자동 생성
- 자기소개서 항목별 자동 작성 (성장과정, 지원동기, 직무역량 등)
- ATS 최적화 키워드 분석 (프리미엄)
- PDF 다운로드
- 면접 예상 질문 생성
- 채용공고 URL 입력 → 맞춤 자소서 생성

## 수익 구조

| 플랜 | 가격 | 생성 횟수 | 기능 |
|------|------|-----------|------|
| 무료 | 0원 | 3회 | 기본 이력서/자소서 생성 |
| 프리미엄 | 월 14,900원 | 무제한 | 생성 무제한 + ATS 최적화 분석 + PDF 다운로드 |

## 기술 스택

| 구분 | 기술 |
|------|------|
| Backend | FastAPI, Python 3.11 |
| Database | SQLite (aiosqlite) |
| AI | Google Gemini API |
| PDF | WeasyPrint |
| 배포 | Docker, Docker Compose |

## 설치 및 실행

### 사전 요구사항

- Python 3.11+
- Docker (선택)
- Google Gemini API 키

### 로컬 실행

```bash
# 저장소 클론
git clone https://github.com/your-username/ResumeAI.git
cd ResumeAI

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 GEMINI_API_KEY 입력

# 서버 실행
uvicorn app.main:app --reload --port 8000
```

### Docker 실행

```bash
docker-compose up -d
```

서버 실행 후 http://localhost:8000 접속

## 주요 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `GET` | `/` | 메인 페이지 |
| `GET` | `/api/profiles` | 프로필 목록 조회 |
| `POST` | `/api/profiles` | 프로필 생성 |
| `POST` | `/api/resumes/generate` | AI 이력서 자동 생성 |
| `GET` | `/api/resumes` | 이력서 목록 조회 |
| `GET` | `/api/resumes/{id}` | 이력서 상세 조회 |
| `POST` | `/api/cover-letters/generate` | AI 자소서 자동 생성 |
| `GET` | `/api/cover-letters` | 자소서 목록 조회 |
| `POST` | `/api/analysis/ats` | ATS 적합도 분석 (프리미엄) |
| `GET` | `/api/interviews/questions` | 면접 예상 질문 생성 |
| `GET` | `/api/jobs` | 채용공고 목록 |

## 지원 직무 카테고리

| 분야 | 직무 예시 |
|------|----------|
| 개발/IT | 백엔드, 프론트엔드, 풀스택, 데이터 엔지니어, AI/ML |
| 기획/마케팅 | 서비스 기획, 그로스 마케팅, 콘텐츠 마케팅, 브랜드 마케팅 |
| 디자인 | UI/UX, 그래픽, 제품 디자인, 영상 편집 |
| 경영/사무 | 경영기획, 인사, 재무/회계, 영업, 고객 서비스 |
| 금융 | 투자, 리스크 관리, 핀테크, 보험 |
| 의료/바이오 | 임상, 연구개발, 의료기기, 제약 |
| 제조/생산 | 생산관리, 품질관리, 연구개발, 공정 엔지니어 |

## 환경 변수

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite+aiosqlite:///./resumeai.db
APP_NAME=ResumeAI
APP_VERSION=1.0.0
```

## 라이선스

MIT
