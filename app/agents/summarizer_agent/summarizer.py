import asyncio
from collections import OrderedDict
from typing import Any
from agents import Agent, Runner, function_tool, trace, ModelSettings
from app.agents.prompts.prompt_collection import financial_news_analyst
from app.configs_constants.configs import Configs
from app.models.relevant_news import NewsAnalysisOutput, RelevantNewsItem
from app.news_services.news_injest_services import FinnhubService, MarketauxService, NewsAPIService, NewsDataService, WorldNewsAPIService
from app.utilities.json_utiliti import save_json, save_llm_news_json

summarizer_agent = Agent(
    name="Financial News Analyst",
    instructions=financial_news_analyst,
    #tools=tools,
    #handoffs=handoffs,
    model="gpt-4o-mini",
    output_type=NewsAnalysisOutput,
    model_settings=ModelSettings(temperature=0))

async def summarize(message: str):
    with trace("Automated Summarizer"):
        result = await Runner.run(summarizer_agent, message)
        return result.final_output.relevant_news

async def summarize_with_iterations(news_list: str, runs: int = 1):
    tasks = [summarize(news_list) for _ in range(runs)]
    results = await asyncio.gather(*tasks)

    combined_dict = OrderedDict[Any, RelevantNewsItem]()

    for run_output in results:
        for item in run_output.relevant_news:
            idx = item.index

            if idx not in combined_dict:
                combined_dict[idx] = item

    combined_news = list[RelevantNewsItem](combined_dict.values())
    return combined_news    

@function_tool
async def analyze_stock_market_news(runs: int = 1):
    """
    Analyzes financial news to identify items that can impact the Indian stock market, then returns structured, 
    concise summaries ranked by relevance and potential effect on specific stocks or sectors.
    """
    newsapi = NewsAPIService()
    newsdata = NewsDataService()
    marketaux = MarketauxService()
    finnhub = FinnhubService()
    worldnewsapi = WorldNewsAPIService()
    
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
    
    combined_news= await summarize(news_list)  
    return save_llm_news_json(combined_news, False, "summarized_news")["relevant_news"]    
