"""Google Gemini API 클라이언트"""
import json
import google.generativeai as genai
from app.config import settings


def get_gemini_client():
    """Gemini 클라이언트 초기화"""
    genai.configure(api_key=settings.GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-1.5-flash")


async def generate_text(prompt: str) -> str:
    """Gemini로 텍스트 생성 (동기 API를 비동기 래핑)"""
    import asyncio
    model = get_gemini_client()

    def _call():
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4096,
            ),
        )
        return response.text

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _call)
    return result


async def generate_json(prompt: str) -> dict:
    """Gemini로 JSON 형식 텍스트 생성 후 파싱"""
    import asyncio
    model = get_gemini_client()

    full_prompt = f"""{prompt}

반드시 순수한 JSON 형식으로만 응답하세요. 마크다운 코드블록(```json ```)을 사용하지 마세요."""

    def _call():
        response = model.generate_content(
            full_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.5,
                max_output_tokens=4096,
            ),
        )
        return response.text

    loop = asyncio.get_running_loop()
    raw = await loop.run_in_executor(None, _call)

    # JSON 파싱 시도
    raw = raw.strip()
    # 마크다운 코드블록 제거
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 빈 딕셔너리 반환
        return {"error": "JSON 파싱 실패", "raw": raw}
