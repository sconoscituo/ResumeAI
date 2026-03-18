"""채용공고 분석 서비스"""
import ipaddress
import socket
import httpx
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from app.services.gemini import generate_json


def _validate_url(url: str) -> None:
    """SSRF 방지를 위한 URL 유효성 검사"""
    parsed = urlparse(url)

    # http/https 스킴만 허용
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"허용되지 않는 URL 스킴: {parsed.scheme}")

    hostname = parsed.hostname
    if not hostname:
        raise ValueError("유효하지 않은 URL: 호스트명 없음")

    # 명시적으로 차단할 호스트명
    blocked_hosts = {"localhost", "127.0.0.1", "169.254.169.254", "::1"}
    if hostname.lower() in blocked_hosts:
        raise ValueError(f"차단된 호스트: {hostname}")

    # DNS 조회 후 private IP 차단
    try:
        resolved_ip = socket.gethostbyname(hostname)
        ip_obj = ipaddress.ip_address(resolved_ip)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved:
            raise ValueError(f"사설 IP 주소로의 요청은 허용되지 않습니다: {resolved_ip}")
    except (socket.gaierror, ValueError) as e:
        raise ValueError(f"URL 검증 실패: {e}") from e


async def fetch_job_posting(url: str) -> str:
    """URL에서 채용공고 텍스트 추출"""
    _validate_url(url)

    async with httpx.AsyncClient(timeout=15.0, follow_redirects=False) as client:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }
        response = await client.get(url, headers=headers)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    # 스크립트/스타일 제거
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    # 너무 긴 경우 앞 5000자만 사용
    return text[:5000] if len(text) > 5000 else text


async def analyze_job_posting(job_text: str) -> dict:
    """채용공고 AI 분석 - 핵심 요구사항 추출"""
    prompt = f"""다음 채용공고를 분석하여 JSON 형식으로 정보를 추출하세요.

채용공고:
{job_text}

다음 JSON 구조로 응답하세요:
{{
  "company_name": "회사명",
  "position": "직무명",
  "required_skills": ["필수 기술1", "필수 기술2"],
  "preferred_skills": ["우대 기술1", "우대 기술2"],
  "responsibilities": ["주요 업무1", "주요 업무2"],
  "requirements": ["자격 요건1", "자격 요건2"],
  "keywords": ["ATS 핵심 키워드1", "키워드2", "키워드3"],
  "culture_keywords": ["회사 문화 키워드1", "키워드2"],
  "summary": "채용공고 핵심 요약 (2-3문장)"
}}
"""
    result = await generate_json(prompt)
    return result
