"""LinkedIn job search integration."""

import httpx
from bs4 import BeautifulSoup
from backend.job_search.sources.base import JobSource


class LinkedInSource(JobSource):
    name = "linkedin"
    BASE_URL = "https://www.linkedin.com/jobs/search"

    async def search(
        self,
        job_title: str,
        keywords: list[str],
        location: str | None,
        remote_ok: bool,
    ) -> list:
        from backend.job_search.aggregator import JobListing

        query = f"{job_title} {' '.join(keywords)}"
        params = {
            "keywords": query,
            "location": location or "United States",
            "position": "1",
            "pageNum": "0",
            "sortBy": "DD",  # Sort by date
        }
        if remote_ok:
            params["f_WT"] = "2"  # Remote filter

        listings = []
        try:
            async with httpx.AsyncClient(
                headers={
                    "User-Agent": "BulkJobApp/1.0",
                },
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                resp = await client.get(self.BASE_URL, params=params)
                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, "html.parser")
                job_cards = soup.select("div.base-card, li.result-card")

                for card in job_cards[:25]:
                    title_el = card.select_one("h3.base-search-card__title, .result-card__title")
                    company_el = card.select_one("h4.base-search-card__subtitle, .result-card__subtitle")
                    location_el = card.select_one(".job-search-card__location, .result-card__meta")
                    link_el = card.select_one("a.base-card__full-link, a.result-card__full-card-link")

                    if not title_el or not link_el:
                        continue

                    listings.append(
                        JobListing(
                            title=title_el.get_text(strip=True),
                            company=company_el.get_text(strip=True) if company_el else "Unknown",
                            location=location_el.get_text(strip=True) if location_el else "Remote",
                            salary_range=None,
                            description="",
                            url=link_el.get("href", ""),
                            source=self.name,
                            easy_apply=False,
                        )
                    )
        except Exception:
            pass

        return listings
