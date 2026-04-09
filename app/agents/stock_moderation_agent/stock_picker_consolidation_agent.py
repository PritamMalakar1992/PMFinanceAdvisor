import asyncio
from typing import List

from agents import Agent, Runner, trace

from app.agents.prompts.prompt_collection import judge_agent_prompt, judge_agent_prompt_1, stock_judge_prompt
from app.agents.prompts.prompt_collection_backup import stock_judge_prompt_backup
from app.agents.stock_analyst_agent.stock_picker_agent import pick_stocks_with_consensus_tool
from app.agents.summarizer_agent.summarizer import analyze_stock_market_news
from app.utilities.firecrawl_utiliti import firecrawl_search_tool
from app.models.selected_stock import SelectedStock, StockSelectionOutput

stock_picker_consolidation_agent = Agent(
    name="Stock Picker Judge & Consolidation Agent",
    instructions=stock_judge_prompt_backup, #Old
    #instructions=stock_judge_prompt, #New
    model="gpt-5-mini",
    tools=[pick_stocks_with_consensus_tool, analyze_stock_market_news, firecrawl_search_tool],
    output_type=StockSelectionOutput,
)


async def consolidate_stocks_once(
    dataframe_str: str,
    analyst_output_str: str,
    capital: int = 10000,
) -> StockSelectionOutput:

    input_payload = f"""
    TOTAL_CAPITAL = {capital}

    df_final_json:
    {dataframe_str}

    Analyst Output:
    {analyst_output_str}
    """

    with trace("Stock Consolidation (Judge Single Run)"):
        result = await Runner.run(stock_picker_consolidation_agent, input_payload)
        return result.final_output


async def consolidate_with_consensus(
    dataframe_str: str,
    capital: int = 10000,
    runs: int = 1
) -> List[SelectedStock]:

    tasks = [
        consolidate_stocks_once(dataframe_str, capital)
        for _ in range(runs)
    ]

    results = await asyncio.gather(*tasks)

    final_stocks: List[SelectedStock] = []

    for run_output in results:
        final_stocks.extend(run_output.selected_stocks)

    return final_stocks