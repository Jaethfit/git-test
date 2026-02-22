"""Base class for job search sources."""

from abc import ABC, abstractmethod


class JobSource(ABC):
    name: str = "base"

    @abstractmethod
    async def search(
        self,
        job_title: str,
        keywords: list[str],
        location: str | None,
        remote_ok: bool,
    ) -> list:
        pass
