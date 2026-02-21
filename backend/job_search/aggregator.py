"""Aggregate job listings from multiple sources."""

import asyncio
from dataclasses import dataclass
from backend.job_search.sources.indeed import IndeedSource
from backend.job_search.sources.linkedin import LinkedInSource
from backend.job_search.sources.greenhouse import GreenhouseSource


@dataclass
class JobListing:
    title: str
    company: str
    location: str
    salary_range: str | None
    description: str
    url: str
    source: str
    external_id: str | None = None
    easy_apply: bool = False
    requires_cover_letter: bool = False
    screening_questions: list | None = None


SOURCES = [
    IndeedSource(),
    LinkedInSource(),
    GreenhouseSource(),
]


async def search_jobs(
    job_title: str,
    keywords: list[str],
    location: str | None = None,
    remote_ok: bool = True,
) -> list[JobListing]:
    """Search all sources concurrently and aggregate results."""

    tasks = [
        source.search(job_title, keywords, location, remote_ok)
        for source in SOURCES
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    all_listings = []
    for result in results:
        if isinstance(result, Exception):
            continue
        all_listings.extend(result)

    # Deduplicate by URL
    seen_urls = set()
    unique_listings = []
    for listing in all_listings:
        if listing.url not in seen_urls:
            seen_urls.add(listing.url)
            unique_listings.append(listing)

    return unique_listings
