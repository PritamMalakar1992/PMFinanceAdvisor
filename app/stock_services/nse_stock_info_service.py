import logging
from typing import Dict, Any, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential


class NSEConfig:
    BASE_URL = "https://www.nseindia.com"
    API_URL = f"{BASE_URL}/api"

class NSEConstants:
    DEFAULT_TIMEOUT = 10
    MAX_RETRIES = 5


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("NSEService")


class AsyncHttpClient:

    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """Singleton client with connection pooling"""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=NSEConstants.DEFAULT_TIMEOUT,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "application/json, text/plain, */*",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": NSEConfig.BASE_URL,
                    "Connection": "keep-alive",
                },
                follow_redirects=True,
            )

            try:
                await cls._client.get(NSEConfig.BASE_URL)
                logger.info("NSE session initialized")
            except Exception as e:
                logger.exception("Failed to initialize NSE session")
                raise

        return cls._client

    @staticmethod
    @retry(
        stop=stop_after_attempt(NSEConstants.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
    )
    async def get(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:

        url = f"{NSEConfig.API_URL}{endpoint}"

        try:
            client = await AsyncHttpClient.get_client()

            response = await client.get(url, params=params)

            if response.status_code in (401, 403, 429):
                logger.warning(f"NSE blocked / rate limited: {url}")
                raise Exception("Retryable NSE block")

            response.raise_for_status()

            return response.json()

        except httpx.TimeoutException:
            logger.error(f"Timeout error: {url}")
            raise

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {url}")
            raise

        except Exception as e:
            logger.exception(f"Unexpected error: {url} | {e}")
            raise


class NseService:

    async def get_market_status_from_nse(self) -> Dict:
        return await AsyncHttpClient.get("/marketStatus")

    async def get_all_indices_from_nse(self) -> Dict:
        return await AsyncHttpClient.get("/allIndices")

    async def get_equity_stock_indices_from_nse(self, index: str = "NIFTY 50") -> Dict:
        return await AsyncHttpClient.get(
            "/equity-stockIndices",
            {"index": index}
        )

    async def get_quote_equity_from_nse(self, symbol: str = "RELIANCE") -> Dict:
        return await AsyncHttpClient.get(
            "/quote-equity",
            {"symbol": symbol}
        )

    async def get_quote_trade_info_from_nse(self, symbol: str = "TCS") -> Dict:
        return await AsyncHttpClient.get(
            "/quote-equity",
            {
                "symbol": symbol,
                "section": "trade_info"
            }
        )

    async def get_top_gainers_from_nse(self) -> Dict:
        return await AsyncHttpClient.get(
            "/live-analysis-variations",
            {"index": "gainers"}
        )

    async def get_top_losers_from_nse(self) -> Dict:
        return await AsyncHttpClient.get(
            "/live-analysis-variations",
            {"index": "losers"}
        )

    async def get_market_snapshot_from_nse(self) -> Dict[str, Any]:
        import asyncio

        try:
            results = await asyncio.gather(
                self.getMarketStatus(),
                self.getAllIndices(),
                self.getEquityStockIndices(),
                self.getTopGainers(),
                self.getTopLosers(),
                return_exceptions=True
            )

            return {
                "market_status": results[0] if not isinstance(results[0], Exception) else {},
                "indices": results[1] if not isinstance(results[1], Exception) else {},
                "nifty50": results[2] if not isinstance(results[2], Exception) else {},
                "gainers": results[3] if not isinstance(results[3], Exception) else {},
                "losers": results[4] if not isinstance(results[4], Exception) else {},
            }

        except Exception as e:
            logger.exception(f"Snapshot aggregation failed: {e}")
            return {}