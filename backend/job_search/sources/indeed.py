"""Indeed job search integration."""

import httpx
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
from backend.job_search.sources.base import JobSource


class IndeedSource(JobSource):
    name = "indeed"
    BASE_URL = "https://www.indeed.com"

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
            "q": query,
            "l": location or "",
            "fromage": "14",  # Last 14 days
            "sort": "date",
        }
        if remote_ok:
            params["remotejob"] = "032b3046-06a3-4876-8dfd-474eb5e7ed11"

        listings = []
        try:
            async with httpx.AsyncClient(
                headers={"User-Agent": "BulkJobApp/1.0"},
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                resp = await client.get(f"{self.BASE_URL}/jobs", params=params)
                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, "html.parser")
                job_cards = soup.select("div.job_seen_beacon")

                for card in job_cards[:25]:
                    title_el = card.select_one("h2.jobTitle a, a.jcs-JobTitle")
                    company_el = card.select_one("[data-testid='company-name'], .companyName")
                    location_el = card.select_one("[data-testid='text-location'], .companyLocation")
                    salary_el = card.select_one(".salary-snippet-container, .estimated-salary")
                    snippet_el = card.select_one(".job-snippet, [data-testid='jobDescriptionText']")

                    if not title_el:
                        continue

                    job_url_path = title_el.get("href", "")
                    if job_url_path and not job_url_path.startswith("http"):
                        job_url_path = f"{self.BASE_URL}{job_url_path}"

                    listings.append(
                        JobListing(
                            title=title_el.get_text(strip=True),
                            company=company_el.get_text(strip=True) if company_el else "Unknown",
                            location=location_el.get_text(strip=True) if location_el else "Remote",
                            salary_range=salary_el.get_text(strip=True) if salary_el else None,
                            description=snippet_el.get_text(strip=True) if snippet_el else "",
                            url=job_url_path,
                            source=self.name,
                            easy_apply="easily apply" in card.get_text().lower(),
                        )
                    )
        except Exception:
            pass

        return listings
