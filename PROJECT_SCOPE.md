# Bulk Job Application App — Project Scope

## What It Is

A 6-stage autonomous job application pipeline. Upload your resume, the AI identifies your career paths, finds matching jobs across multiple boards, scores them, tailors your resume per job, writes cover letters, and optionally submits applications — all hands-free.

## The Pipeline

| Stage | What Happens |
|-------|-------------|
| 1. Parse | Extract resume text (PDF/DOCX), LLM structures it and identifies multiple career paths ("I see management AND commercial pilot — want to search both?") |
| 2. Discover | Scrape job boards (Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google Jobs) + Workday employer portals + direct career sites. Deduplicate by URL |
| 3. Enrich | Fetch full job descriptions — JSON-LD first, CSS selectors second, AI extraction as fallback |
| 4. Score | AI rates every job 1-10 against your profile. Only jobs above threshold proceed |
| 5. Tailor | Per-job resume rewrite (reorder experience, emphasize relevant skills, add keywords). Never fabricates. Per-job cover letter. Answer screening questions with AI |
| 6. Auto-Apply | Browser automation navigates forms, fills fields, uploads docs, submits. Live progress dashboard |

## Two Modes

- **Full Pipeline** — All 6 stages, discovery through submission. Requires Chrome + Playwright.
- **Discovery + Tailoring Only** — Stages 1-5. AI prepares everything, you submit manually with the tailored materials.

## Tech Stack (What We Have)

- **FastAPI** + async SQLAlchemy (SQLite) — API and persistence
- **OpenAI (GPT-4o / 4o-mini)** — resume parsing, scoring, tailoring, cover letters
- **BeautifulSoup + httpx** — job board scraping (Indeed, LinkedIn)
- **Greenhouse API** — 15 preconfigured employer boards
- **Playwright** — browser automation (installed, not yet wired)
- **pdfplumber / python-docx** — document extraction

## What We're Adding (from ApplyPilot)

### More Job Sources
- **python-jobspy** for unified scraping across Indeed, LinkedIn, Glassdoor, ZipRecruiter, Google Jobs (replaces our individual scrapers)
- **Workday employer portals** — configurable registry (ApplyPilot ships 48)
- **Direct career sites** — custom extractors with a config-driven site registry

### Enrichment Stage (New)
- 3-tier cascade for full job descriptions: JSON-LD structured data → CSS selector patterns → AI-powered extraction
- Currently we only get snippet-level data from search results

### Smarter Scoring
- Structured profile (work authorization, compensation, experience, skills, resume facts) powers scoring — not just raw resume text
- Configurable score threshold to control what proceeds to tailoring

### Auto-Apply Engine (The Big One)
- Playwright-driven form navigation and submission
- Detect form type, fill personal info + work history, upload tailored resume + cover letter
- Answer screening questions with AI
- Optional CAPTCHA solving (CapSolver integration)
- Parallel workers (`-w 4` flag) — multiple Chrome instances
- Dry-run mode — fill forms without submitting
- Live progress dashboard

### CLI Interface
- `init` — one-time setup: resume, profile, preferences, API keys
- `doctor` — verify setup, show what's installed/missing
- `run` — execute stages 1-5 (discover → tailor)
- `apply` — execute stage 6 (browser submission)
- Parallel flag (`-w N`) for discovery/enrichment and apply stages

### Configuration Files
- `profile.json` — structured personal data (contact, work auth, compensation, experience, skills, resume facts, EEO defaults)
- `searches.yaml` — job search queries, target titles, locations, boards
- `employers.yaml` — Workday employer registry
- `sites.yaml` — direct career sites, blocked sites, manual ATS domains
- `.env` — API keys and runtime config

## User Flow

1. **Upload resume** → AI extracts and structures it
2. **Career path detection** → AI identifies paths, presents them conversationally with a text box for user to confirm/adjust/add
3. **Multiple pipelines run in parallel** — each career path gets its own search
4. **Results screen** — two lanes: auto-apply eligible vs. human-review cards
5. **Per-card actions** — individual submit + "Submit All" batch button
6. **Tracking dashboard** — timestamps, status pipeline, progress charts

## What We Already Have Built

- Resume extraction + LLM-powered career path detection
- Job search from Indeed, LinkedIn, Greenhouse (individual scrapers)
- Job aggregation with deduplication
- Match scoring with GPT-4o-mini (skills, experience, title match)
- Keyword tailoring for ATS
- Cover letter generation
- Screening question answering
- Database models (Resume → Pipeline → Job → Application)
- Auto-apply eligibility detection (field exists, logic not wired)

## What Needs Building

1. **python-jobspy integration** — replace individual scrapers with unified library
2. **Enrichment module** — 3-tier description fetching
3. **Profile system** — structured `profile.json` powering scoring and form fill
4. **Config-driven site registry** — `employers.yaml`, `sites.yaml`, `searches.yaml`
5. **Applicator engine** — Playwright form detection, filling, submission (module exists but is empty)
6. **Worker parallelism** — thread pool for discovery, enrichment, and apply stages
7. **CLI commands** — `init`, `doctor`, `run`, `apply` with flags
8. **Live dashboard** — real-time progress during auto-apply
9. **Dry-run mode** — fill without submitting
10. **CAPTCHA integration** — optional CapSolver support
