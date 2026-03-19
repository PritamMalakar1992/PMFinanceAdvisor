import asyncio
from cgitb import reset
import sys
from app.news_services.services import NewsAPIService, MarketauxService, FinnhubService, NewsDataService, WorldNewsAPIService

from app.utils.jsonutils import save_news
from app.news_services.config import Config

async def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    newsapi = NewsAPIService()
    newsdata = NewsDataService()
    marketaux = MarketauxService()
    finnhub = FinnhubService()
    worldnewsapi = WorldNewsAPIService()

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
    
    """ 
    results = await asyncio.gather(
        
        # Single API call, need to make this configurable
        #newsapi.NewsAPIIndiaHeadline(),
        #newsdata.NewsDataAPIIndiaHeadline(),
        #marketaux.MarketauxAPIIndiaBusiness(),
        #finnhub.FinnhubAPIIndiaBusiness(),
        #worldnewsapi.WorldNewsAPIIndiaHeadline()
        
        newsapi.StartInjestFromNewsAPI(),
        newsdata.StartInjestFromNewsData(),
        marketaux.StartInjestFromMarketauxAPI(),
        finnhub.StartInjestFromFinnhubAPI(),
        worldnewsapi.StartInjestFromWorldNewsAPI()
    )

    """

    combined = [item for sublist in results for item in sublist]

    #for news in combined[:10]:
    for news in combined:
        print(news)

    save_news(combined)

if __name__ == "__main__":
    asyncio.run(main())