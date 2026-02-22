"""Greenhouse ATS job board integration.

Greenhouse has a public job board API that many tech companies use.
This source searches across multiple known Greenhouse-powered boards.
"""

import httpx
from backend.job_search.sources.base import JobSource

# Well-known companies using Greenhouse boards
GREENHOUSE_BOARDS = [
    "airbnb", "coinbase", "discord", "figma", "notion",
    "stripe", "twitch", "hashicorp", "cloudflare", "datadog",
    "gusto", "netlify", "plaid", "brex", "ramp",
]


class GreenhouseSource(JobSource):
    name = "greenhouse"
    API_BASE = "https://boards-api.greenhouse.io/v1/boards"

    async def search(
        self,
        job_title: str,
        keywords: list[str],
        location: str | None,
        remote_ok: bool,
    ) -> list:
        from backend.job_search.aggregator import JobListing

        search_terms = {job_title.lower()} | {k.lower() for k in keywords}
        listings = []

        async with httpx.AsyncClient(timeout=15.0) as client:
            for board in GREENHOUSE_BOARDS:
                try:
                    resp = await client.get(f"{self.API_BASE}/{board}/jobs", params={"content": "true"})
                    if resp.status_code != 200:
                        continue

                    data = resp.json()
                    for job in data.get("jobs", []):
                        title_lower = job.get("title", "").lower()
                        content = job.get("content", "").lower()

                        # Check if any search term appears in title or content
                        if not any(term in title_lower or term in content for term in search_terms):
                            continue

                        job_location = ""
                        if job.get("location", {}).get("name"):
                            job_location = job["location"]["name"]

                        if location and location.lower() not in job_location.lower():
                            if not remote_ok:
                                continue

                        listings.append(
                            JobListing(
                                title=job.get("title", ""),
                                company=board.capitalize(),
                                location=job_location or "Not specified",
                                salary_range=None,
                                description=job.get("content", "")[:500],
                                url=job.get("absolute_url", ""),
                                source=f"greenhouse:{board}",
                                external_id=str(job.get("id", "")),
                                easy_apply=True,  # Greenhouse API supports direct apply
                                requires_cover_letter="cover letter" in content,
                            )
                        )
                except Exception:
                    continue

        return listings
