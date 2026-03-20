import asyncio
from cgitb import reset
import sys
from app.news_services.services import NewsAPIService, MarketauxService, FinnhubService, NewsDataService, WorldNewsAPIService
from app.stock_services import nse_service
from app.stock_services.stock_service import StockService
from app.stock_services.nse_service import NSEService

from app.utils.jsonutils import save_news
from app.utils.firecrawl_service import FirecrawlService

from app.news_services.config import Config

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    newsapi = NewsAPIService()
    newsdata = NewsDataService()
    marketaux = MarketauxService()
    finnhub = FinnhubService()
    worldnewsapi = WorldNewsAPIService()
    firecrawlservice = FirecrawlService()
    stockService = StockService()
    nse_service = NSEService()

    API_TASKS = {
        "USE_NEWSAPI": newsapi.StartInjestFromNewsAPI,
        "USE_NEWSDATA": newsdata.StartInjestFromNewsData,
        "USE_MARKETAUX": marketaux.StartInjestFromMarketauxAPI,
        "USE_FINNHUB": finnhub.StartInjestFromFinnhubAPI,
        "USE_WORLDNEWSAPI": worldnewsapi.StartInjestFromWorldNewsAPI,
    }

    tasks = [
        func()
        for key, func in API_TASKS.items()
        if getattr(Config, key, False)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    #print(await stockService.IndexInfo());

    #res1 = await firecrawlservice.FirecrawlSearch("India stock market news", 5)
    #res2 = await firecrawlservice.FirecrawlScrape("https://example.com")
    #res3 = await firecrawlservice.FirecrawlCrawl("https://example.com", limit=3)
    #res4 = await firecrawlservice.FirecrawlBrowse("https://example.com")

    #print(res1)

    #print(await nse_service.getMarketStatus())
    #print(await nse_service.getAllIndices())
    print(await nse_service.getEquityStockIndices('BANKNIFTY'))

    """
    print(await nse_service.getAllIndices())
    print(await nse_service.getEquityStockIndices())
    print(await nse_service.getQuoteEquity("INFY"))
    print(await nse_service.getQuoteTradeInfo("TCS"))
    print(await nse_service.getTopGainers())
    print(await nse_service.getTopLosers())
    """
    snapshot = await nse_service.getMarketSnapshot()
    print(snapshot)

    combined = [item for sublist in results for item in sublist]

    #for news in combined[:10]:
    #for news in combined:
        #print(news)
    
    if combined:
        save_news(combined)
        print(f"Saved {len(combined)} articles.")
    else:
        print("No news to save.")

if __name__ == "__main__":
    asyncio.run(main())