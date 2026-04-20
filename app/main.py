from app.agents.stock_analyst_agent.stock_picker_agent import pick_stocks_once, pick_stocks_with_consensus, pick_stocks_with_consensus_tool
from app.agents.stock_moderation_agent.stock_picker_consolidation_agent import consolidate_with_consensus
from app.agents.summarizer_agent.summarizer import summarize, summarize_with_iterations
from app.news_services.news_injest_services import NewsAPIService, MarketauxService, FinnhubService, NewsDataService, WorldNewsAPIService
from app.stock_services.nse_stock_info_service import NseService
from app.stock_services.yahoo_stock_info_service import StockService
from app.stock_services.indian_stock_info_service import IndianStockService
from app.utilities.json_utiliti import load_dataframe_from_json, save_json, save_json_without_index, save_dataframe_as_json, save_llm_news_json
from app.utilities.firecrawl_utiliti import FirecrawlService
from app.utilities.screener_scraper import scrape, scrape_from_multi_user
from .configs_constants.configs import Configs
import asyncio
import sys

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    """
    newsapi = NewsAPIService()
    newsdata = NewsDataService()
    marketaux = MarketauxService()
    finnhub = FinnhubService()
    worldnewsapi = WorldNewsAPIService()
    firecrawlservice = FirecrawlService()
    stockService = StockService()
    nse_service = NseService()
    indian_stock_service = IndianStockService()
    
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
    
    if combined:
        save_json(combined)
        print(f"Saved {len(combined)} articles.")
    
    news_list = "\n".join(
    f"Index - {index}: {news_item.news}"
    for index, news_item in enumerate(combined))    
    """
    
    #combined_news = await summarize_with_iterations(news_list, 2)  
    #save_llm_news_json(combined_news, "summarized_news")

    #screener_data_dataframe = scrape()
    #save_dataframe_as_json(screener_data_dataframe)

    #df_final = scrape_from_multi_user()
    #df_final_json = save_dataframe_as_json(df_final, True, "stocks_fundamentals") 
    
    df_final_json = load_dataframe_from_json("stocks_fundamentals-2026-04-17_08-05-PM")
    
    #save_json(await pick_stocks_with_consensus(df_final_json), "final_recomendation")
    save_json(await consolidate_with_consensus(df_final_json), "final_recomendation")

    #print(await indian_stock_service.get_stock_by_name("BALKRISIND"))

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

    """
    serper.dev can be used to extract more news 
    """

if __name__ == "__main__":
    asyncio.run(main())