"""ResumeAI 구독 플랜"""
from enum import Enum

class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"          # 월 9,900원 - 무제한 이력서, AI 첨삭
    PREMIUM = "premium"  # 월 19,900원 - 면접 코칭, 취업 멘토링

PLAN_LIMITS = {
    PlanType.FREE:    {"resumes_per_month": 2, "ai_feedback": False, "interview_coaching": False, "template_count": 3},
    PlanType.PRO:     {"resumes_per_month": 30,"ai_feedback": True,  "interview_coaching": False, "template_count": 20},
    PlanType.PREMIUM: {"resumes_per_month": 999,"ai_feedback": True, "interview_coaching": True,  "template_count": 999},
}

PLAN_PRICES_KRW = {PlanType.FREE: 0, PlanType.PRO: 9900, PlanType.PREMIUM: 19900}
