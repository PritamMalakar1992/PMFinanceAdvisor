import asyncio
from collections import OrderedDict
from typing import List, Any

from agents import Agent, Runner, trace

from app.agents.summarizer_agent.summarizer import analyze_stock_market_news
from app.models.selected_stock import SelectedStock, StockSelectionOutput
from app.utilities.firecrawl_utiliti import firecrawl_search_tool
from app.agents.stock_analyst_agent.prompts import top_trader_agent_prompt, elite_trader_agent_prompt


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
