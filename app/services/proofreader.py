"""자소서 맞춤법 검사 및 문체 교정 서비스"""
import difflib
from app.services.gemini import generate_json, generate_text


async def proofread_text(original_text: str) -> dict:
    """Gemini API로 맞춤법/문법/문체 교정 후 원본과 비교"""

    prompt = f"""당신은 한국어 교정 전문가입니다. 아래 자기소개서 텍스트를 교정해주세요.

교정 기준:
1. 맞춤법 오류 수정 (띄어쓰기, 철자 등)
2. 문법 오류 수정 (조사, 어미 등)
3. 문체 개선 (자연스러운 표현, 중복 표현 제거)
4. 어색한 표현 수정 (직역투, 번역투 제거)
5. 자기소개서에 적합한 격식체 유지

[원본 텍스트]
{original_text}

아래 JSON 형식으로 응답하세요:
{{
  "corrected": "교정된 전체 텍스트",
  "corrections": [
    {{
      "original": "원본 표현",
      "corrected": "교정된 표현",
      "reason": "교정 이유"
    }}
  ],
  "summary": "교정 요약 (총 N개 수정, 주요 교정 사항)"
}}"""

    result = await generate_json(prompt)

    corrected_text = result.get("corrected", original_text)
    corrections = result.get("corrections", [])
    summary = result.get("summary", "교정 완료")

    # diff 생성 (줄 단위 비교)
    diff_lines = _generate_diff(original_text, corrected_text)

    return {
        "original": original_text,
        "corrected": corrected_text,
        "corrections": corrections,
        "diff": diff_lines,
        "summary": summary,
        "correction_count": len(corrections),
    }


def _generate_diff(original: str, corrected: str) -> list[dict]:
    """원본과 교정본의 diff를 생성 (줄 단위)"""
    original_lines = original.splitlines(keepends=True)
    corrected_lines = corrected.splitlines(keepends=True)

    diff = list(difflib.unified_diff(
        original_lines,
        corrected_lines,
        fromfile="원본",
        tofile="교정본",
        lineterm="",
    ))

    result = []
    for line in diff:
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            result.append({"type": "header", "text": line})
        elif line.startswith("+"):
            result.append({"type": "added", "text": line[1:]})
        elif line.startswith("-"):
            result.append({"type": "removed", "text": line[1:]})
        else:
            result.append({"type": "unchanged", "text": line[1:] if line.startswith(" ") else line})

    return result
