"""채용공고 자동 수집 서비스 (사람인/잡코리아 RSS 기반)"""
import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional
import httpx

from app.services.gemini import generate_json


# RSS 피드 URL 목록
SARAMIN_RSS = "https://www.saramin.co.kr/zf_user/rss/feed?job_category=1&paid_fl=n&search_salary=0&search_area=&search_edu=0&search_exp=0&sort=RD&search_optional_item=n&search_local=0&rec_idx=&search_careertype=&panel_type=&search_date=&panel_count=&mini_priorty=&search_keyword={keyword}"
JOBKOREA_RSS = "https://www.jobkorea.co.kr/Search/?stext={keyword}&tabType=recruit&Page_No=1"


async def fetch_saramin_rss(keyword: str, limit: int = 10) -> list[dict]:
    """사람인 RSS에서 채용공고 수집"""
    url = SARAMIN_RSS.format(keyword=keyword)
    jobs = []

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()
            root = ET.fromstring(resp.text)

            channel = root.find("channel")
            if channel is None:
                return jobs

            items = channel.findall("item")[:limit]
            for item in items:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                desc = item.findtext("description", "").strip()
                pub_date = item.findtext("pubDate", "").strip()

                # 회사명 추출 (제목 패턴: "직무 - 회사명")
                company = ""
                if " - " in title:
                    parts = title.rsplit(" - ", 1)
                    title_clean = parts[0].strip()
                    company = parts[1].strip()
                else:
                    title_clean = title

                jobs.append({
                    "title": title_clean,
                    "company": company,
                    "url": link,
                    "description": desc,
                    "deadline": pub_date,
                    "source": "사람인",
                })
    except Exception:
        pass

    return jobs


async def fetch_jobs_by_keyword(keyword: str, limit: int = 10) -> list[dict]:
    """키워드 기반 채용공고 수집 (사람인 RSS)"""
    jobs = await fetch_saramin_rss(keyword, limit)

    # RSS에서 충분히 가져오지 못한 경우 더미 데이터로 보완
    if len(jobs) < 3:
        jobs.extend(_get_fallback_jobs(keyword))

    return jobs[:limit]


def _get_fallback_jobs(keyword: str) -> list[dict]:
    """RSS 접근 실패 시 Gemini로 생성한 샘플 채용공고 반환"""
    # 실제 크롤링이 차단되거나 실패할 경우를 대비한 안전망
    return [
        {
            "title": f"{keyword} 개발자",
            "company": "테크스타트업",
            "url": "https://www.saramin.co.kr",
            "description": f"{keyword} 경험 보유자 우대. 팀워크와 커뮤니케이션 능력 중시.",
            "deadline": datetime.now().strftime("%Y-%m-%d"),
            "source": "샘플",
        }
    ]


async def calculate_match_score(profile_data: dict, job: dict) -> int:
    """프로필과 채용공고의 매칭 점수 계산 (0~100)"""
    skills_list = profile_data.get("skills_list", [])
    skills_str = ", ".join(skills_list)
    job_desc = f"{job.get('title', '')} {job.get('description', '')}"

    prompt = f"""지원자 기술 스택과 채용공고를 비교해서 매칭 점수를 0~100 사이 정수로만 평가하세요.

지원자 기술 스택: {skills_str}
경력: {len(profile_data.get('careers', []))}개 회사
프로젝트: {len(profile_data.get('projects', []))}개

채용공고:
제목: {job.get('title', '')}
회사: {job.get('company', '')}
내용: {job_desc[:300]}

아래 JSON 형식으로만 응답하세요:
{{"score": 75, "reason": "매칭 이유 한 문장"}}"""

    try:
        result = await generate_json(prompt)
        score = int(result.get("score", 50))
        return max(0, min(100, score))
    except Exception:
        return 50


async def fetch_jobs_with_matching(keyword: str, profile_data: Optional[dict] = None, limit: int = 10) -> list[dict]:
    """채용공고 수집 + 프로필 매칭 점수 계산"""
    jobs = await fetch_jobs_by_keyword(keyword, limit)

    if profile_data:
        # 매칭 점수 병렬 계산
        scores = await asyncio.gather(
            *[calculate_match_score(profile_data, job) for job in jobs],
            return_exceptions=True,
        )
        for job, score in zip(jobs, scores):
            job["matched_score"] = score if isinstance(score, int) else 50
        # 매칭 점수 내림차순 정렬
        jobs.sort(key=lambda x: x.get("matched_score", 0), reverse=True)
    else:
        for job in jobs:
            job["matched_score"] = 0

    return jobs
