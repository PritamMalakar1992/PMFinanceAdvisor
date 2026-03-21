from typing import List, Dict
import logging
import asyncio
import yfinance as yf

logger = logging.getLogger(__name__)


async def run_in_thread(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


class StockService:

    async def index_info_from_yahoo(self, symbol: str = "^NSEI") -> Dict:
        try:
            ticker = yf.Ticker(symbol)

            info = await run_in_thread(lambda: ticker.info)
            hist = await run_in_thread(lambda: ticker.history(period="1d"))

            if hist.empty:
                return {}

            return {
                "index": symbol,
                "name": info.get("shortName"),
                "price": float(hist["Close"].iloc[-1]),
                "high": float(hist["High"].iloc[-1]),
                "low": float(hist["Low"].iloc[-1]),
                "open": float(hist["Open"].iloc[-1]),
                "volume": float(hist["Volume"].iloc[-1]),
            }

        except Exception as e:
            logger.exception(f"YahooIndexInfo error: {e}")
            return {}

    async def stock_details_from_yahoo(self, symbol: str = "RELIANCE.NS") -> Dict:
        try:
            ticker = yf.Ticker(symbol)

            info = await run_in_thread(lambda: ticker.info)
            hist = await run_in_thread(lambda: ticker.history(period="1d"))

            if hist.empty:
                return {}

            return {
                "symbol": symbol,
                "price": float(hist["Close"].iloc[-1]),
                "high": float(hist["High"].iloc[-1]),
                "low": float(hist["Low"].iloc[-1]),
                "marketCap": info.get("marketCap"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "peRatio": info.get("trailingPE"),
                "eps": info.get("trailingEps"),
                "revenue": info.get("totalRevenue"),
                "52WeekHigh": info.get("fiftyTwoWeekHigh"),
                "52WeekLow": info.get("fiftyTwoWeekLow"),
            }

        except Exception as e:
            logger.exception(f"YahooStockDetails error: {e}")
            return {}

    async def stock_historical_ddetails_from_yahoo(self, symbol: str = "RELIANCE.NS", period: str = "5y") -> List[Dict]:
        try:
            ticker = yf.Ticker(symbol)

            hist = await run_in_thread(lambda: ticker.history(period=period))

            result = []
            for idx, row in hist.iterrows():
                result.append({
                    "date": str(idx),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": float(row["Volume"]),
                })

            return result

        except Exception as e:
            logger.exception(f"YahooHistorical error: {e}")
            return []