import logging
from app.news_services.config import Config
from app.utils.jsonutils import save_news
import asyncio
from typing import List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential
from .firecrawl_search_result import SearchResult

from firecrawl import FirecrawlApp

logger = logging.getLogger(__name__)


async def run_in_thread(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


class FirecrawlService:

    def __init__(self):
        self.client = FirecrawlApp(api_key='fc-00d44bc9742343f3ad4f244aaf247658')

    def _debug_print_response(self, result: Any, label: str) -> None:
        """
        Firecrawl SDK returns pydantic models (e.g., SearchData) instead of plain dicts.
        This helper prints a JSON-like payload for debugging.
        """
        try:
            if hasattr(result, "model_dump"):
                payload = result.model_dump()
            elif hasattr(result, "dict"):
                payload = result.dict()
            else:
                payload = result

            print(f"Firecrawl response received from the http in json format ({label}):", payload)
        except Exception:
            # Never break the flow just because debugging print failed.
            print(f"Firecrawl response received from the http in json format ({label}):", result)

    def _extract_data(self, result: Any, default: Any) -> Any:
        """Extract the SDK `data` field for both dict responses and pydantic models."""
        if isinstance(result, dict):
            return result.get("data", default)
        if hasattr(result, "data"):
            return getattr(result, "data", default)
        return default


    def _format(self, item: Dict[str, Any], category: str) -> SearchResult:
        # Firecrawl SDK returns pydantic model items for search results.
        # Normalize them to dicts so we can safely use `.get(...)`.
        if not isinstance(item, dict):
            if hasattr(item, "model_dump"):
                item = item.model_dump()
            elif hasattr(item, "dict"):
                item = item.dict()

        title = item.get("title") or item.get("headline") or ""
        description = (
            item.get("markdown")
            or item.get("content")
            or item.get("snippet")
            or item.get("description")
            or ""
        )

        news_text = (
            f"Title - {title}, "
            f"Headline - {title}, "
            f"Description - {description[:500]}"
        )

        return SearchResult(
            news=news_text,
            date=item.get("publishedTime") or "",
            category=category
        )


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def FirecrawlSearch(self, query: str, limit: int = 5) -> List[SearchResult]:
        try:
            logger.info(f"Firecrawl search: {query}")

            result = await run_in_thread(
                self.client.search,
                query=query,
                limit=limit
            )

            self._debug_print_response(result, "search")
            # Firecrawl SDK search response is typically a model with `web`/`news`/`images`,
            # not a plain dict with `data`.
            items = None
            if isinstance(result, dict):
                items = result.get("web")
                if items is None:
                    items = result.get("data")
            else:
                items = getattr(result, "web", None)
                if items is None:
                    items = getattr(result, "data", None)

            if items is None:
                items = []

            return [self._format(item, "search") for item in items]

        except Exception as e:
            logger.exception(f"FirecrawlSearch error: {e}")
            return []


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def FirecrawlScrape(self, url: str) -> List[SearchResult]:
        try:
            logger.info(f"Firecrawl scrape: {url}")

            result = await run_in_thread(
                self.client.scrape,
                url=url
            )

            self._debug_print_response(result, "scrape")
            data = self._extract_data(result, {})

            return [self._format(data, "scrape")]

        except Exception as e:
            logger.exception(f"FirecrawlScrape error: {e}")
            return []


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def FirecrawlCrawl(self, url: str, limit: int = 5) -> List[SearchResult]:
        try:
            logger.info(f"Firecrawl crawl: {url}")

            result = await run_in_thread(
                self.client.crawl,
                url=url,
                limit=limit
            )

            self._debug_print_response(result, "crawl")
            data = self._extract_data(result, [])

            return [self._format(item, "crawl") for item in data]

        except Exception as e:
            logger.exception(f"FirecrawlCrawl error: {e}")
            return []


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def FirecrawlBrowse(self, url: str) -> List[SearchResult]:
        try:
            logger.info(f"Firecrawl browse: {url}")

            result = await run_in_thread(
                self.client.scrape,  # browse uses scrape with richer output
                url=url,
                formats=["markdown"]
            )

            self._debug_print_response(result, "browse")
            data = self._extract_data(result, {})

            return [self._format(data, "browse")]

        except Exception as e:
            logger.exception(f"FirecrawlBrowse error: {e}")
            return []