import logging
from typing import Dict, Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from ..configs_constants import constants as C
from ..configs_constants.configs import Configs


# ==============================
# LOGGING
# ==============================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger = logging.getLogger("IndianStockService")


# ==============================
# HTTP CLIENT
# ==============================

class AsyncHttpClient:

    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=C.INDIAN_STOCK_DEFAULT_TIMEOUT,
                headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "X-API-KEY": Configs.INDIAN_STOCK_API_KEY,
                    "Connection": "keep-alive",
                },
                follow_redirects=True,
            )

            try:
                await cls._client.get(C.INDIAN_STOCK_BASE_URL)
                logger.info("IndianAPI session initialized")
            except Exception:
                logger.exception("Failed to initialize session")
                raise

        return cls._client

    @staticmethod
    @retry(
        stop=stop_after_attempt(C.INDIAN_STOCK_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:

        url = f"{C.INDIAN_STOCK_BASE_URL}{endpoint}"

        try:
            client = await AsyncHttpClient.get_client()
            response = await client.get(url, params=params)

            if response.status_code in (401, 403, 429):
                logger.warning(f"Blocked / rate limited: {url}")
                raise Exception("Retryable block")

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.exception(f"Error: {url} | {e}")
            raise


# ==============================
# SERVICE (ONLY DOC APIs)
# ==============================

class IndianStockService:

    # -----------------------------------
    # 1. STOCK DETAILS
    # -----------------------------------
    async def get_stock_by_name(self, name: str) -> Dict:
        """
        GET /stock?name=
        """
        return await AsyncHttpClient.get(
            "/stock",
            {"name": name}
        )

    # -----------------------------------
    # 2. INDUSTRY SEARCH
    # -----------------------------------
    async def search_by_industry(self, query: str) -> Dict:
        """
        GET /industry_search?query=
        """
        return await AsyncHttpClient.get(
            "/industry_search",
            {"query": query}
        )

    # -----------------------------------
    # 3. TRENDING STOCKS
    # -----------------------------------
    async def get_trending_stocks(self) -> Dict:
        """
        GET /trending
        """
        return await AsyncHttpClient.get("/trending")

    # -----------------------------------
    # 4. 52 WEEK HIGH / LOW
    # -----------------------------------
    async def get_52_week_high_low(self) -> Dict:
        """
        GET /fetch_52_week_high_low_data
        """
        return await AsyncHttpClient.get(
            "/fetch_52_week_high_low_data"
        )

    # -----------------------------------
    # 5. NSE MOST ACTIVE
    # -----------------------------------
    async def get_nse_most_active(self) -> Dict:
        """
        GET /NSE_most_active
        """
        return await AsyncHttpClient.get("/NSE_most_active")

    # -----------------------------------
    # 6. BSE MOST ACTIVE
    # -----------------------------------
    async def get_bse_most_active(self) -> Dict:
        """
        GET /BSE_most_active
        """
        return await AsyncHttpClient.get("/BSE_most_active")

    # -----------------------------------
    # 7. MUTUAL FUNDS
    # -----------------------------------
    async def get_mutual_funds(self) -> Dict:
        """
        GET /mutual_funds
        """
        return await AsyncHttpClient.get("/mutual_funds")

    # -----------------------------------
    # 8. PRICE SHOCKERS
    # -----------------------------------
    async def get_price_shockers(self) -> Dict:
        """
        GET /price_shockers
        """
        return await AsyncHttpClient.get("/price_shockers")

    # -----------------------------------
    # 9. COMMODITIES
    # -----------------------------------
    async def get_commodities(self) -> Dict:
        """
        GET /commodities
        """
        return await AsyncHttpClient.get("/commodities")

    # -----------------------------------
    # 10. ANALYST TARGET PRICE
    # -----------------------------------
    async def get_stock_target_price(self, stock_id: str) -> Dict:
        """
        GET /stock_target_price?stock_id=
        """
        return await AsyncHttpClient.get(
            "/stock_target_price",
            {"stock_id": stock_id}
        )

    # -----------------------------------
    # 11. STOCK FORECASTS
    # -----------------------------------
    async def get_stock_forecasts(
        self,
        stock_id: str,
        measure_code: str,
        period_type: str,
        data_type: str,
        age: str
    ) -> Dict:
        """
        GET /stock_forecasts
        """
        return await AsyncHttpClient.get(
            "/stock_forecasts",
            {
                "stock_id": stock_id,
                "measure_code": measure_code,
                "period_type": period_type,
                "data_type": data_type,
                "age": age
            }
        )

    # -----------------------------------
    # 12. HISTORICAL DATA
    # -----------------------------------
    async def get_historical_data(
        self,
        stock_name: str,
        period: str = "5yr",
        filter: str = "default"
    ) -> Dict:
        """
        GET /historical_data
        """
        return await AsyncHttpClient.get(
            "/historical_data",
            {
                "stock_name": stock_name,
                "period": period,
                "filter": filter
            }
        )

    # -----------------------------------
    # 13. HISTORICAL STATS
    # -----------------------------------
    async def get_historical_stats(
        self,
        stock_name: str,
        stats: str
    ) -> Dict:
        """
        GET /historical_stats
        """
        return await AsyncHttpClient.get(
            "/historical_stats",
            {
                "stock_name": stock_name,
                "stats": stats
            }
        )