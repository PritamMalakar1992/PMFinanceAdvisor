from typing import List, Dict, Any
from agents import function_tool
from tenacity import retry, stop_after_attempt, wait_exponential
from ..configs_constants.configs import Configs
from ..models.search_result import SearchResult
import asyncio
import logging

from firecrawl import FirecrawlApp

logger = logging.getLogger(__name__)

async def run_in_thread(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)

class FirecrawlService:

    def __init__(self):
        self.client = FirecrawlApp(api_key=Configs.FIRECRAWL_API_KEY)

    def _debug_print_response(self, result: Any, label: str) -> None:

        try:
            if hasattr(result, "model_dump"):
                payload = result.model_dump()
            elif hasattr(result, "dict"):
                payload = result.dict()
            else:
                payload = result

            print(f"Firecrawl response received from the http in json format ({label}):", payload)
        except Exception:
            print(f"Firecrawl response received from the http in json format ({label}):", result)

    def _extract_data(self, result: Any, default: Any) -> Any:
        if isinstance(result, dict):
            return result.get("data", default)
        if hasattr(result, "data"):
            return getattr(result, "data", default)
        return default


    def _format(self, item: Dict[str, Any], category: str) -> SearchResult:
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
            #f"Description - {description[:500]}"
            f"Description - {description}"
        )

        return SearchResult(
            news=news_text,
            date=item.get("publishedTime") or "",
            category=category
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=2))
    async def firecrawl_search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Performs an internet search for any query and returns relevant, up-to-date information from web sources, 
        including real-time topics like "latest India stock market news" as well as general knowledge queries.
        """
        try:
            logger.info(f"Firecrawl search: {query}")

            result = await run_in_thread(
                self.client.search,
                query=query,
                limit=limit
            )

            #self._debug_print_response(result, "search")
            
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
    async def firecrawl_scrape(self, url: str) -> List[SearchResult]:
        try:
            logger.info(f"Firecrawl scrape: {url}")

            result = await run_in_thread(
                self.client.scrape,
                url=url
            )

            #self._debug_print_response(result, "scrape")
            data = self._extract_data(result, {})

            return [self._format(data, "scrape")]

        except Exception as e:
            logger.exception(f"FirecrawlScrape error: {e}")
            return []


    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def firecrawl_crawl(self, url: str, limit: int = 1) -> List[SearchResult]:
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
    async def firecrawl_browse(self, url: str) -> List[SearchResult]:
        try:
            logger.info(f"Firecrawl browse: {url}")

            result = await run_in_thread(
                self.client.scrape,
                url=url,
                formats=["markdown"]
            )

            #self._debug_print_response(result, "browse")
            data = self._extract_data(result, {})

            return [self._format(data, "browse")]

        except Exception as e:
            logger.exception(f"FirecrawlBrowse error: {e}")
            return []

@function_tool
async def firecrawl_search_tool(query: str = "India stock market news"):
    tools_instance = FirecrawlService()
    return await tools_instance.firecrawl_search(query)