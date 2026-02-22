"""Score and rank job listings against a candidate's resume profile."""

import json
from openai import AsyncOpenAI
from backend.config import OPENAI_API_KEY
from backend.job_search.aggregator import JobListing

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SCORING_PROMPT = """You are a job matching expert. Score how well this candidate matches this job listing.

Candidate Profile:
{profile}

Job Listing:
Title: {job_title}
Company: {company}
Description: {description}

Score the match on these dimensions (0-100 each):
1. skills_match: How well do the candidate's skills align with the job requirements?
2. experience_match: Does the candidate have the right level and type of experience?
3. title_match: How close is the job title to what the candidate is looking for?
4. overall: Weighted overall score (skills 40%, experience 35%, title 25%)

Also determine:
- auto_apply_eligible: true if the job is a strong match (overall >= 80) and the listing supports easy apply
- requires_cover_letter: true if the job description mentions or implies a cover letter is needed
- key_gaps: list of skills/qualifications the candidate is missing

Return valid JSON:
{{
    "skills_match": 85,
    "experience_match": 90,
    "title_match": 75,
    "overall": 84,
    "auto_apply_eligible": true,
    "requires_cover_letter": false,
    "key_gaps": ["AWS certification", "5+ years leadership"]
}}
"""


async def score_job(profile: dict, listing: JobListing, pipeline_keywords: list[str]) -> dict:
    profile_summary = json.dumps(
        {
            "target_title": profile.get("target_title", ""),
            "skills": profile.get("skills", []),
            "experience": profile.get("experience", []),
            "certifications": profile.get("certifications", []),
            "keywords": pipeline_keywords,
        },
        indent=2,
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a job matching expert. Always respond with valid JSON only."},
            {
                "role": "user",
                "content": SCORING_PROMPT.format(
                    profile=profile_summary,
                    job_title=listing.title,
                    company=listing.company,
                    description=listing.description[:2000],
                ),
            },
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    result = json.loads(response.choices[0].message.content)

    # Override auto_apply based on listing capabilities
    if not listing.easy_apply:
        result["auto_apply_eligible"] = False
    if listing.requires_cover_letter:
        result["requires_cover_letter"] = True

    return result


async def score_and_rank_jobs(
    profile: dict,
    listings: list[JobListing],
    pipeline_keywords: list[str],
    min_score: float = 50.0,
) -> list[tuple[JobListing, dict]]:
    """Score all listings and return sorted by overall score, filtered by minimum."""
    import asyncio

    # Score all jobs concurrently (in batches to avoid rate limits)
    batch_size = 10
    scored = []

    for i in range(0, len(listings), batch_size):
        batch = listings[i : i + batch_size]
        tasks = [score_job(profile, listing, pipeline_keywords) for listing in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for listing, result in zip(batch, results):
            if isinstance(result, Exception):
                continue
            if result.get("overall", 0) >= min_score:
                scored.append((listing, result))

    scored.sort(key=lambda x: x[1].get("overall", 0), reverse=True)
    return scored
