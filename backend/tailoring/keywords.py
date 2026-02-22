"""Tailor resume keywords per job listing to maximize ATS match rates."""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

KEYWORD_PROMPT = """You are an ATS (Applicant Tracking System) optimization expert.

Given the candidate's current resume keywords and a specific job description, identify keyword adjustments to maximize ATS compatibility.

Candidate's current skills/keywords:
{current_keywords}

Job Description:
{job_description}

Return valid JSON:
{{
    "keywords_to_add": ["keyword1", "keyword2"],
    "keywords_to_emphasize": ["existing_keyword1"],
    "suggested_skill_rewordings": {{
        "original_term": "job_posting_term"
    }},
    "ats_score_before": 65,
    "ats_score_after": 88,
    "explanation": "Brief explanation of changes"
}}

Rules:
- Only suggest keywords the candidate can honestly claim (based on their existing skills)
- Reword existing skills to match the job posting's language (e.g., "JS" -> "JavaScript")
- Do NOT fabricate skills the candidate doesn't have
"""


async def tailor_keywords(resume_skills: list[str], job_description: str) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an ATS optimization expert. Always respond with valid JSON only."},
            {
                "role": "user",
                "content": KEYWORD_PROMPT.format(
                    current_keywords=json.dumps(resume_skills),
                    job_description=job_description[:3000],
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
