from typing import List, Dict, Optional
from datetime import date as Date, datetime, timezone
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models.news_data import News
from ..configs_constants.configs import Configs
from ..configs_constants import constants as C

import httpx
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("NewsService")


class AsyncHttpClient:

    @staticmethod
    @retry(
        stop=stop_after_attempt(C.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def get(url: str, params: Dict) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=C.DEFAULT_TIMEOUT) as client:
                response = await client.get(url, params=params)

                if response.status_code == 429:
                    logger.warning(f"Rate limit hit: {url}")
                    raise Exception("Rate limit exceeded")

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout error: {url}")
            raise

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise


def format_news_old(source: str, category: str, articles: List[Dict]) -> List[Dict]:
    return [
        {
            "source": source,
            "category": category,
            "news": a.get("title") or a.get("headline"),
            "date": a.get("publishedAt") or a.get("published_at") or a.get("datetime")
        }
        for a in articles
    ]

def format_news(source: str, category: str, articles: List[Dict]) -> List[News]:
    formatted = []

    for a in articles:
        title = a.get("title") or a.get("headline") or ""
        headline = (
            a.get("headline")
            or a.get("title")
            or a.get("description")
            or ""
        )
        description = (
            a.get("description")
            or a.get("content")
            or a.get("summary")
            or ""
        )

        date = (
            a.get("publishedAt")
            or a.get("published_at")
            or a.get("datetime")
            or a.get("pubDate")
            or ""
        )

        parsed_date: Date
        if isinstance(date, Date) and not isinstance(date, datetime):
            parsed_date = date
        elif isinstance(date, datetime):
            parsed_date = date.date()
        elif isinstance(date, (int, float)):
            parsed_date = datetime.fromtimestamp(date, tz=timezone.utc).date()
        elif isinstance(date, str):
            s = date.strip()
            if not s:
                parsed_date = datetime.now(timezone.utc).date()
            else:
                iso = s.replace("Z", "+00:00")
                try:
                    parsed_date = datetime.fromisoformat(iso).date()
                except ValueError:
                    try:
                        parsed_date = Date.fromisoformat(s[:10])
                    except ValueError:
                        parsed_date = datetime.now(timezone.utc).date()
        else:
            parsed_date = datetime.now(timezone.utc).date()

        # Pritam - Commented to lower LLM cost
        news_text = (
            #f"Title - {title}, "            
            #f"Headline - {headline}, "
            f"{description}"
        )

        """
        news_text = (
            f"Title - {title}, "            
            f"Headline - {headline}, "
            f"Description - {description}"
        )
        """
        formatted.append(
            News(
                news=news_text,
                date=parsed_date,
                source=source,
                category=category
            )
        )

    return formatted


class NewsDataService:

    async def _fetch(self, country: str, category: str) -> List[Dict]:
        params = {
            "apikey": Configs.NEWSDATA_KEY,
            "country": country,
            "category": category,
            "language": "en"
        }

        try:
            data = await AsyncHttpClient.get(C.NEWSDATA_BASE_URL, params)
            return data.get("results", [])
        except Exception:
            return []

    async def _newsDataAPIWorldHeadline(self):
        data = await self._fetch("us", "top")
        return format_news("newsdata", "headline", data)

    async def _newsDataAPIWorldBusiness(self):
        data = await self._fetch("us", "business")
        return format_news("newsdata", "business", data)

    async def _newsDataAPIWorldFinance(self):
        data = await self._fetch("us", "business")
        return format_news("newsdata", "finance", data)

    async def _newsDataAPIIndiaHeadline(self):
        data = await self._fetch("in", "top")
        return format_news("newsdata", "headline", data)

    async def _newsDataAPIIndiaBusiness(self):
        data = await self._fetch("in", "business")
        return format_news("newsdata", "business", data)

    async def _newsDataAPIIndiaFinance(self):
        data = await self._fetch("in", "business")
        return format_news("newsdata", "finance", data)

    async def start_injest_from_newsdata(self) -> Dict[str, List]:
        results=await asyncio.gather(
            # Pritam - Commented to lower LLM cost
            #self._newsDataAPIWorldHeadline(),
            self._newsDataAPIWorldFinance(),
            #self._newsDataAPIIndiaBusiness(),
            #self._newsDataAPIIndiaHeadline(),
            #self._newsDataAPIIndiaBusiness(),
            self._newsDataAPIIndiaFinance()
        )
        
        return [item for sublist in results for item in sublist]

class NewsAPIService:

    async def _fetch(self, country: str, category: str) -> List[Dict]:
        params = {
            "country": country,
            "category": category,
            "apiKey": Configs.NEWSAPI_KEY
        }

        try:
            data = await AsyncHttpClient.get(C.NEWSAPI_BASE_URL, params)
            return data.get("articles", [])
        except Exception:
            return []
    
    async def _newsAPIWorldHeadline(self):
        return format_news("newsapi", "headline", await self._fetch("us", "general"))
    
    async def _newsAPIWorldBusiness(self):
        return format_news("newsapi", "business", await self._fetch("us", "business"))

    async def _newsAPIWorldFinance(self):
        return format_news("newsapi", "finance", await self._fetch("us", "business"))

    async def _newsAPIIndiaHeadline(self):
        return format_news("newsapi", "headline", await self._fetch("in", "general"))

    async def _newsAPIIndiaBusiness(self):
        return format_news("newsapi", "business", await self._fetch("in", "business"))

    async def _newsAPIIndiaFinance(self):
        return format_news("newsapi", "finance", await self._fetch("in", "business"))    

    async def start_injest_from_newsapi(self) -> Dict[str, List]:
        results=await asyncio.gather(
            # Pritam - Commented to lower LLM cost
            #self._newsAPIWorldHeadline(),
            #self._newsAPIWorldBusiness(),
            self._newsAPIWorldFinance(),
            #self._newsAPIIndiaHeadline(),
            #self._newsAPIIndiaBusiness(),
            self._newsAPIIndiaFinance()
        )
        
        return [item for sublist in results for item in sublist]


class MarketauxService:

    async def _fetch(self, country: Optional[str] = None) -> List[Dict]:
        params = {
            "api_token": Configs.MARKETAUX_KEY,
            "limit": 10,
            "language": "en"
        }

        if country:
            params["countries"] = country

        try:
            data = await AsyncHttpClient.get(C.MARKETAUX_BASE_URL, params)
            return data.get("data", [])
        except Exception:
            return []

    async def _marketauxAPIWorldHeadline(self):
        return format_news("marketaux", "headline", await self._fetch())

    async def _marketauxAPIWorldBusiness(self):
        return format_news("marketaux", "business", await self._fetch())

    async def _marketauxAPIWorldFinance(self):
        return format_news("marketaux", "finance", await self._fetch())

    async def _marketauxAPIIndiaHeadline(self):
        return format_news("marketaux", "headline", await self._fetch("in"))

    async def _marketauxAPIIndiaBusiness(self):
        return format_news("marketaux", "business", await self._fetch("in"))

    async def _marketauxAPIIndiaFinance(self):
        return format_news("marketaux", "finance", await self._fetch("in"))

    async def start_injest_from_marketauxapi(self) -> Dict[str, List]:
        results=await asyncio.gather(
            # Pritam - Commented to lower LLM cost
            #self._marketauxAPIWorldHeadline(),
            self._marketauxAPIWorldFinance(),
            #self._marketauxAPIWorldBusiness(),
            #self._marketauxAPIIndiaHeadline(),
            #self._marketauxAPIIndiaBusiness(),
            self._marketauxAPIIndiaFinance()
        )
        
        return [item for sublist in results for item in sublist]

class FinnhubService:

    async def _fetch(self) -> List[Dict]:
        params = {
            "category": "general",
            "token": Configs.FINNHUB_KEY
        }

        try:
            return await AsyncHttpClient.get(C.FINNHUB_BASE_URL, params)
        except Exception:
            return []

    def _filter_india(self, articles: List[Dict]) -> List[Dict]:
        return [a for a in articles if "india" in (a.get("headline") or "").lower()]

    async def _finnhubAPIWorldHeadline(self):
        return format_news("finnhub", "headline", await self._fetch())

    async def _finnhubAPIWorldBusiness(self):
        return format_news("finnhub", "business", await self._fetch())

    async def _finnhubAPIWorldFinance(self):
        return format_news("finnhub", "finance", await self._fetch())

    async def _finnhubAPIIndiaHeadline(self):
        return format_news("finnhub", "headline", self._filter_india(await self._fetch()))

    async def _finnhubAPIIndiaBusiness(self):
        return format_news("finnhub", "business", self._filter_india(await self._fetch()))

    async def _finnhubAPIIndiaFinance(self):
        return format_news("finnhub", "finance", self._filter_india(await self._fetch()))

    async def start_injest_from_finnhubapi(self) -> Dict[str, List]:
        results=await asyncio.gather(
            # Pritam - Commented to lower LLM cost
            #self._finnhubAPIWorldHeadline(),
            self._finnhubAPIWorldFinance(),
            #self._finnhubAPIWorldBusiness(),
            #self._finnhubAPIIndiaHeadline(),
            #self._finnhubAPIIndiaBusiness(),
            self._finnhubAPIIndiaFinance()
        )
        
        return [item for sublist in results for item in sublist]        

class WorldNewsAPIService:

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _search_news(self, country: str) -> List[Dict]:

        params = {
            "api-key": Configs.WORLDNEWSAPI_KEY,
            "source-country": country,
            "language": "en",
            "category": "business,technology"
        }

        try:
            async with httpx.AsyncClient(timeout=C.DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    "https://api.worldnewsapi.com/search-news",
                    params=params
                )

                if response.status_code == 429:
                    logger.warning("WorldNewsAPI rate limit hit (search-news)")
                    raise Exception("Rate limit exceeded")

                response.raise_for_status()
                data = response.json()

                return data.get("news", [])

        except Exception as e:
            logger.exception(f"WorldNewsAPI search error: {e}")
            return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
    async def _top_news(self, country: str) -> List[Dict]:

        params = {
            "api-key": Configs.WORLDNEWSAPI_KEY,
            "source-country": country,
            "language": "en"
        }


        try:
            async with httpx.AsyncClient(timeout=C.DEFAULT_TIMEOUT) as client:
                response = await client.get(
                    "https://api.worldnewsapi.com/top-news",
                    params=params
                )

                if response.status_code == 429:
                    logger.warning("WorldNewsAPI rate limit hit (top-news)")
                    raise Exception("Rate limit exceeded")

                response.raise_for_status()
                data = response.json()

                articles = []
                for cluster in data.get("top_news", []):
                    for item in cluster.get("news", []):
                        articles.append(item)

                return articles

        except Exception as e:
            logger.exception(f"WorldNewsAPI top-news error: {e}")
            return []

    async def _worldNewsAPIIndiaBusFin(self, country: str = "in"):
        data = await self._search_news(country)
        return format_news("worldnewsapi", "business_finance", data)

    async def _worldNewsAPIWorldBusFin(self, country: str = "us"):
        data = await self._search_news(country)
        return format_news("worldnewsapi", "business_finance", data)

    async def _worldNewsAPIIndiaHeadline(self, country: str = "in"):
        data = await self._top_news(country)
        return format_news("worldnewsapi", "headline", data)

    async def _worldNewsAPIWorldHeadline(self, country: str = "us"):
        data = await self._top_news(country)
        return format_news("worldnewsapi", "headline", data)

    async def start_injest_from_worldnewsapi(self) -> Dict[str, List]:
        results=await asyncio.gather(
            # Pritam - Commented to lower LLM cost
            #self._worldNewsAPIWorldHeadline(),
            self._worldNewsAPIWorldBusFin(),            
            #self._worldNewsAPIIndiaHeadline(),
            self._worldNewsAPIIndiaBusFin()
        )
        
        return [item for sublist in results for item in sublist]        