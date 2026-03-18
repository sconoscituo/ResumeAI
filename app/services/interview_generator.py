"""면접 예상 질문 생성 서비스"""
from app.services.gemini import generate_json


# 질문 유형 분류
QUESTION_CATEGORIES = {
    "technical": "기술 면접",
    "personality": "인성 면접",
    "experience": "경험 기반 면접",
}


async def generate_interview_questions(profile_data: dict, cover_letter_content: str = "") -> dict:
    """자소서 + 이력서 기반으로 면접 예상 질문 10개와 모범답변 생성"""

    # 프로필 요약 텍스트 구성
    skills_str = ", ".join(profile_data.get("skills_list", []))
    careers_str = "\n".join(
        f"- {c['company_name']} / {c['position']} ({c['start_date']}~{c['end_date']}): {c.get('description', '')}"
        for c in profile_data.get("careers", [])
    )
    projects_str = "\n".join(
        f"- {p['project_name']} ({p.get('role', '')}): {p.get('description', '')}"
        for p in profile_data.get("projects", [])
    )
    educations_str = "\n".join(
        f"- {e['school_name']} {e.get('degree', '')} {e.get('major', '')}"
        for e in profile_data.get("educations", [])
    )

    prompt = f"""당신은 면접 전문가입니다. 아래 지원자 정보를 바탕으로 면접 예상 질문 10개와 각 질문에 대한 모범답변을 생성해주세요.

[지원자 기본 정보]
이름: {profile_data.get('name', '')}
한 줄 소개: {profile_data.get('summary', '')}
기술 스택: {skills_str}

[학력]
{educations_str or '정보 없음'}

[경력 사항]
{careers_str or '경력 없음'}

[프로젝트]
{projects_str or '프로젝트 없음'}

[자기소개서 내용]
{cover_letter_content or '자기소개서 없음'}

아래 JSON 형식으로 정확히 10개의 질문을 생성하세요.
각 질문은 반드시 세 가지 카테고리 중 하나에 속해야 합니다:
- technical: 기술 면접 (기술 스택, 프로젝트, 문제해결 방식)
- personality: 인성 면접 (가치관, 팀워크, 성격)
- experience: 경험 기반 면접 (실제 경험, STAR 기법 답변 유도)

기술 면접 4개, 인성 면접 3개, 경험 기반 면접 3개를 반드시 포함하세요.
모범답변은 200~300자 내외로 구체적이고 설득력 있게 작성하세요.

{{
  "questions": [
    {{
      "id": 1,
      "category": "technical",
      "question": "질문 내용",
      "model_answer": "모범답변",
      "tips": "면접 팁 (1~2문장)"
    }}
  ]
}}"""

    result = await generate_json(prompt)

    # 결과 검증 및 카테고리 레이블 추가
    questions = result.get("questions", [])
    for q in questions:
        cat = q.get("category", "personality")
        q["category_label"] = QUESTION_CATEGORIES.get(cat, "인성 면접")

    return {
        "questions": questions,
        "total": len(questions),
        "categories": QUESTION_CATEGORIES,
    }
