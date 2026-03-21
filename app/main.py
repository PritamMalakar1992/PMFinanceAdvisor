from app.news_services.news_injest_services import NewsAPIService, MarketauxService, FinnhubService, NewsDataService, WorldNewsAPIService
from app.stock_services.nse_stock_info_service import NseService
from app.stock_services.yahoo_stock_info_service import StockService
from app.stock_services.nse_stock_info_service import NseService
from app.utilities.json_utiliti import save_json, save_json_without_index
from app.utilities.firecrawl_utiliti import FirecrawlService
from app.utilities.screener_scraper import scrape
from app.utilities.screener_scraper_without_selenium import scrape_without_selenium
from .configs_constants.configs import Configs
import asyncio
import sys

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
    nse_service = NseService()

    API_TASKS = {
        "USE_NEWSAPI": newsapi.start_injest_from_newsapi,
        "USE_NEWSDATA": newsdata.start_injest_from_newsdata,
        "USE_MARKETAUX": marketaux.start_injest_from_marketauxapi,
        "USE_FINNHUB": finnhub.start_injest_from_finnhubapi,
        "USE_WORLDNEWSAPI": worldnewsapi.start_injest_from_worldnewsapi,
    }

    tasks = [
        func()
        for key, func in API_TASKS.items()
        if getattr(Configs, key, False)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
    combined = [item for sublist in results for item in sublist]

    #for news in combined[:10]:
    #for news in combined:
        #print(news)
    
    if combined:
        save_json(combined)
        print(f"Saved {len(combined)} articles.")


    screener_data_dataframe=scrape()
    print(screener_data_dataframe)

    #print(await stockService.index_info_from_yahoo());
    #print(await stockService.stock_details_from_yahoo());
    #print(await stockService.stock_historical_ddetails_from_yahoo());
    
    #print(await firecrawlservice.firecrawl_search("India stock market news", 5))
    #print(await firecrawlservice.firecrawl_scrape("https://example.com"))
    #print(await firecrawlservice.firecrawl_crawl("https://example.com", limit=3))
    #print(await firecrawlservice.firecrawl_browse("https://example.com"))

    #firecrawl_search_data = await firecrawlservice.firecrawl_search("India stock market news", 5)
    #firecrawl_search_json_data = [item.__dict__ for item in firecrawl_search_data]
    #save_json_without_index(firecrawl_search_json_data,'firecrawl_search_data')

    #print(await nse_service.get_market_status_from_nse())
    #print(await nse_service.get_all_indices_from_nse())
    #print(await nse_service.get_equity_stock_indices_from_nse())
    #print(await nse_service.get_quote_equity_from_nse("INFY"))
    #print(await nse_service.get_quote_trade_info_from_nse("TCS"))
    #print(await nse_service.get_top_gainers_from_nse())
    #print(await nse_service.get_top_losers_from_nse())
    #print(await nse_service.get_market_snapshot_from_nse())

    #market_status_data=await nse_service.get_quote_equity_from_nse()
    #save_json_without_index(market_status_data,'market_status_data')

if __name__ == "__main__":
    asyncio.run(main())