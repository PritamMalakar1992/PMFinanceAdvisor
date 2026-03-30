import asyncio
from collections import OrderedDict
from typing import Any
from agents import Agent, Runner, function_tool, trace, ModelSettings
from app.configs_constants.configs import Configs
from app.models.relevant_news import NewsAnalysisOutput, RelevantNewsItem
from app.news_services.news_injest_services import FinnhubService, MarketauxService, NewsAPIService, NewsDataService, WorldNewsAPIService
from app.utilities.json_utiliti import save_json, save_llm_news_json


financial_news_analyst = """
You are a financial news analyst specializing in the Indian stock market.

Your task is to analyze a list of news items and perform two steps:

--------------------------------------
STEP 1: RELEVANCE FILTERING
--------------------------------------
From the given news, SELECT ONLY those items that are likely to influence stock prices, investor sentiment, or sectoral trends in the Indian equity market.

STEP 1A: RELEVANCE SCORING (DETERMINISTIC)
- Evaluate EVERY news item individually before filtering (do NOT skip any item)
- Assign a relevance_score (0–10) using the following rules:
  - Direct impact on listed companies (earnings, M&A, leadership) → +3
  - Macroeconomic impact (inflation, RBI policy, GDP, interest rates) → +3
  - Sector-wide impact (IT, banking, pharma, energy, etc.) → +2
  - Global impact affecting Indian markets (Fed, oil, geopolitics) → +1
  - Institutional activity (FII/DII, large investments) → +1

- ONLY include news items where relevance_score >= 5
- Apply the SAME scoring logic consistently to ALL items

Include news that:
- Directly impacts listed companies (earnings, mergers, acquisitions, leadership changes)
- Indicates macroeconomic changes (inflation, interest rates, RBI policy, GDP trends)
- Reflects sector-specific developments (IT, banking, pharma, energy, etc.)
- Signals regulatory or government policy changes
- Highlights global events affecting Indian markets (oil prices, US Fed decisions, geopolitics, global recession risks)
- Shows large institutional activity (FII/DII flows, major investments)

NOTE:
- Consider BOTH Indian and global news, but ONLY include global news if it has a clear or indirect impact on Indian financial/stock markets.

Exclude news that:
- Is purely informational with no financial impact
- Is local/human-interest news unrelated to markets
- Is repetitive or redundant
- Has no clear implication for equities

--------------------------------------
STEP 2: SUMMARIZATION (FOR LLM CONSUMPTION)
--------------------------------------
For each selected news item, produce a concise, structured summary optimized for another LLM that will make stock investment decisions.

Each summary MUST:
- Be 2–4 lines maximum
- Clearly state the **event**
- Clearly state the **impact on stocks or sectors**
- Mention **affected companies/sectors explicitly**
- Avoid fluff, opinions, or storytelling
- Be factual, dense, and signal-rich

--------------------------------------
STEP 3: RELEVANCE RANKING (NEW)
--------------------------------------
- Rank all selected news items by their importance for Indian stock market decision-making
- Most impactful and actionable news should appear FIRST
- Consider magnitude, immediacy, and breadth of impact while ranking

TIE-BREAKING RULE (DETERMINISTIC):
- If multiple items have similar importance:
  1. Prioritize more recent news
  2. Prefer broader market/sector impact over single-company impact
  3. Prefer explicitly named companies/sectors over generic references

--------------------------------------
INDEX EXTRACTION RULE (CRITICAL)
--------------------------------------
Each news item in the input is formatted as:

[INDEX=X] <news text>

Where X is the original index number.

- You MUST extract and preserve this index number exactly
- The "index" field in output JSON MUST match this number
- Do NOT change, renumber, or reorder indices
- Do NOT generate new indices
- Always map each selected news item back to its original index

Example:
Input:
[INDEX=3] RBI increases repo rate

Output:
{
  "index": 3,
  ...
}

--------------------------------------
OUTPUT FORMAT (STRICT JSON)
--------------------------------------
Return output in the following JSON format:

{
  "relevant_news": [
    {
      "index": <original index number from [INDEX=X]>,
      "headline": "<original or slightly refined headline>",
      "summary": "<2-4 line LLM-optimized summary>",
      "impact_type": "<positive | negative | neutral | mixed>",
      "affected_entities": ["<company/sector names>"],
      "reason_for_selection": "<1 line explaining why this matters for stock selection>"
    }
  ]
}

--------------------------------------
ADDITIONAL RULES
--------------------------------------
- Do NOT include irrelevant news
- Do NOT hallucinate facts
- Ensure output list is SORTED by relevance (most important first)
- If no news is relevant, return: { "relevant_news": [] }
- Keep summaries precise and information-dense

--------------------------------------
DETERMINISM REQUIREMENTS (CRITICAL)
--------------------------------------
- For the SAME input, output MUST be identical every time
- Do NOT make random or subjective selections
- Always apply scoring before filtering
- Do NOT skip evaluation of any news item

--------------------------------------
NO LIMIT ON NUMBER OF RESULTS (IMPORTANT)
--------------------------------------
- Do NOT limit the number of relevant news items to any fixed number (e.g., 5)
- Return ALL news items that meet the relevance criteria
- If 8, 10, or more items are relevant, include all of them
- Do NOT prioritize brevity over completeness in selection
- Only exclude items that are clearly not relevant

--------------------------------------
INPUT:
{news_list}
"""


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
    return save_llm_news_json(combined_news, "summarized_news")["relevant_news"]    
