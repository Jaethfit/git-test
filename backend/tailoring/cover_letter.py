"""Generate tailored cover letters for specific job applications."""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

COVER_LETTER_PROMPT = """Write a professional cover letter for this job application.

Candidate Profile:
Name: {name}
Summary: {summary}
Key Skills: {skills}
Relevant Experience:
{experience}

Job Details:
Title: {job_title}
Company: {company}
Description: {job_description}

Guidelines:
- Keep it under 350 words
- Open with genuine interest in the specific role and company
- Highlight 2-3 most relevant experiences with concrete results
- Connect candidate's skills directly to job requirements
- Close with enthusiasm and a call to action
- Professional but not robotic — sound like a real person
- Do NOT use generic filler phrases like "I'm excited to apply" or "perfect fit"

Return valid JSON:
{{
    "cover_letter": "The full cover letter text",
    "key_talking_points": ["point1", "point2", "point3"]
}}
"""

SCREENING_PROMPT = """Answer these job application screening questions on behalf of the candidate.

Candidate Profile:
{profile}

Screening Questions:
{questions}

Guidelines:
- Answer honestly based on the candidate's actual experience
- Be concise but specific
- If the candidate clearly doesn't meet a requirement, note it honestly rather than fabricating
- Use concrete examples from their experience when possible

Return valid JSON:
{{
    "answers": [
        {{
            "question": "original question",
            "answer": "the answer",
            "confidence": 0.9
        }}
    ]
}}
"""


async def generate_cover_letter(profile: dict, job: dict) -> dict:
    experience_text = "\n".join(
        f"- {exp.get('title', '')} at {exp.get('company', '')}: {exp.get('description', '')}"
        for exp in profile.get("experience", [])[:4]
    )

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert cover letter writer. Always respond with valid JSON only."},
            {
                "role": "user",
                "content": COVER_LETTER_PROMPT.format(
                    name=profile.get("name", ""),
                    summary=profile.get("summary", ""),
                    skills=", ".join(profile.get("skills", [])[:15]),
                    experience=experience_text,
                    job_title=job.get("title", ""),
                    company=job.get("company", ""),
                    job_description=job.get("description", "")[:2000],
                ),
            },
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)


async def answer_screening_questions(profile: dict, questions: list[str]) -> list[dict]:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a job application assistant. Always respond with valid JSON only."},
            {
                "role": "user",
                "content": SCREENING_PROMPT.format(
                    profile=json.dumps(profile, indent=2)[:3000],
                    questions=json.dumps(questions),
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("answers", [])
