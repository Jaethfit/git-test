"""LLM-powered resume analysis: parse structured data and detect career pipelines."""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

PARSE_RESUME_PROMPT = """You are a resume analysis expert. Given the raw text of a resume, extract structured data and identify ALL distinct career paths this person could pursue.

Return valid JSON with this exact structure:
{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "location": "City, State",
  "summary": "Brief professional summary",
  "skills": ["skill1", "skill2"],
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or Present",
      "description": "Brief description",
      "skills_used": ["skill1", "skill2"]
    }
  ],
  "education": [
    {
      "degree": "Degree",
      "institution": "School Name",
      "year": "YYYY"
    }
  ],
  "certifications": ["cert1", "cert2"],
  "pipelines": [
    {
      "job_title": "Suggested Job Title to search for",
      "reasoning": "Why this person qualifies for this career path",
      "relevant_experience_years": 5,
      "key_keywords": ["keyword1", "keyword2", "keyword3"],
      "confidence": 0.95
    }
  ]
}

IMPORTANT for the "pipelines" field:
- Identify EVERY distinct career path, not just the most recent one
- Someone with management experience AND a pilot license has TWO pipelines
- Someone with software engineering AND data science skills has TWO pipelines
- Include the specific job titles that would appear on job boards
- Rank by confidence (how competitive this person would be)
- Include relevant keywords that job postings in this field typically use

Resume text:
"""


async def analyze_resume(resume_text: str) -> dict:
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a resume parsing expert. Always respond with valid JSON only."},
            {"role": "user", "content": PARSE_RESUME_PROMPT + resume_text},
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result


CONFIRM_PIPELINES_PROMPT = """The user has uploaded their resume. Based on the analysis, these career pipelines were identified:

{pipelines}

The user responded with: "{user_message}"

Based on the user's response, return an updated JSON array of pipelines they want to pursue.
- If the user confirms all, return them all
- If the user wants to add a new career path, add it with appropriate keywords
- If the user wants to remove one, remove it
- If the user wants to modify titles or keywords, update them

Return valid JSON: {{"pipelines": [...]}}
"""


async def refine_pipelines(pipelines: list, user_message: str) -> list:
    pipelines_text = json.dumps(pipelines, indent=2)

    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a career advisor. Always respond with valid JSON only."},
            {
                "role": "user",
                "content": CONFIRM_PIPELINES_PROMPT.format(
                    pipelines=pipelines_text, user_message=user_message
                ),
            },
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("pipelines", pipelines)
