import asyncio
from collections import OrderedDict
from typing import List, Any
from agents import Agent, Runner, function_tool, trace, ModelSettings
from app.agents.summarizer_agent.summarizer import analyze_stock_market_news
from app.models.selected_stock import SelectedStock, StockSelectionOutput
from app.utilities.firecrawl_utiliti import firecrawl_search_tool
from app.agents.prompts.prompt_collection import top_trader_agent_prompt, elite_trader_agent_prompt
from app.utilities.json_utiliti import save_dataframe_as_json, save_json
from app.utilities.screener_scraper import scrape_from_multi_user


stock_picker_agent = Agent(
    name="Top Short-Term Stock Trader",
    instructions=top_trader_agent_prompt,
    #instructions=elite_trader_agent_prompt,
    model="gpt-5-mini",
    tools=[analyze_stock_market_news, firecrawl_search_tool],
    output_type=StockSelectionOutput,
    #model_settings=ModelSettings(temperature=0)
)

async def pick_stocks_once(dataframe_str: str, n: int = 5, capital: int = 10000) -> StockSelectionOutput:
    input_payload = f"""
    N = {n}
    TOTAL_CAPITAL = {capital}

    DATAFRAME:
    {dataframe_str}
    """

    with trace("Stock Picker Single Run"):
        result = await Runner.run(stock_picker_agent, input_payload)
        return result.final_output

async def pick_stocks_with_consensus(
    dataframe_str: str,
    n: int = 5,
    capital: int = 10000,
    runs: int = 1
    ) -> List[SelectedStock]:

    tasks = [
        pick_stocks_once(dataframe_str, n, capital)
        for _ in range(runs)
    ]

    results = await asyncio.gather(*tasks)

    combined_dict: OrderedDict[Any, SelectedStock] = OrderedDict()

    for run_output in results:
        for stock in run_output.selected_stocks:
            key = stock.name

            if key not in combined_dict:
                combined_dict[key] = stock

    return list(combined_dict.values())


@function_tool
async def pick_stocks_with_consensus_tool(
    n: int = 5,
    capital: int = 10000,
    runs: int = 1
    ) -> List[SelectedStock]:

    """
    TOOL DESCRIPTION

    generate_high_conviction_trades identifies high-probability BUY and SELL (short) opportunities in the Indian stock market with potential for ≥12% price movement within 1–3 days.

    It focuses only on explosive setups driven by strong momentum, earnings shocks, volatility expansion, and confirmed breakout/breakdown signals, while rejecting weak, low-volatility, or late-entry trades.

    The tool:
    - Scores and filters stocks using momentum, earnings, technicals, and risk factors
    - Validates ≥12% move feasibility using volatility and confirmation rules
    - Selects only high-confidence trades (confidence ≥70)
    - Assigns target prices (BUY: +12–25%, SELL: -15–25%)
    - Allocates capital efficiently (100% default, up to 125% in high conviction cases)
    - Integrates market sentiment and news for final confidence adjustment

    OUTPUT:
    Returns selected stocks with direction (BUY/SELL), target price, confidence, capital allocation, position size, and reasoning.

    Only high-conviction, fast-moving, and technically confirmed trades are included.
    """
    
    df_final = scrape_from_multi_user()
    df_final_json = save_dataframe_as_json(df_final, "stocks_from_child_agents")

    result = await pick_stocks_with_consensus(df_final_json, n, capital, runs)

    save_json(result, "final_recomendation_from_child_agents")
    return result