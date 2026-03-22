from typing import Dict, Any, Callable, Awaitable
from ..stock_services.indian_stock_info_service import IndianStockService


class IndianStockLLMTools:

    def __init__(self):
        self.service = IndianStockService()

        # Map tool names → executor functions
        self.tool_map: Dict[str, Callable[[Dict], Awaitable[Dict]]] = {
            "get_stock": self.get_stock,
            "search_industry": self.search_industry,
            "trending_stocks": self.trending_stocks,
            "nse_most_active": self.nse_most_active,
            "bse_most_active": self.bse_most_active,
            "price_shockers": self.price_shockers,
            "commodities": self.commodities,
            "mutual_funds": self.mutual_funds,
            "stock_target_price": self.stock_target_price,
            "stock_forecasts": self.stock_forecasts,
            "historical_data": self.historical_data,
            "historical_stats": self.historical_stats,
        }

    # ==============================
    # SAFE EXECUTOR
    # ==============================

    async def _safe_execute(self, func, **kwargs) -> Dict[str, Any]:
        try:
            result = await func(**kwargs)
            return {
                "success": True,
                "data": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # ==============================
    # TOOL IMPLEMENTATIONS
    # ==============================

    async def get_stock(self, input: Dict[str, Any]) -> Dict:
        return await self._safe_execute(
            self.service.get_stock_by_name,
            name=input.get("name")
        )

    async def search_industry(self, input: Dict[str, Any]) -> Dict:
        return await self._safe_execute(
            self.service.search_by_industry,
            query=input.get("query")
        )

    async def trending_stocks(self, input: Dict[str, Any] = {}) -> Dict:
        return await self._safe_execute(
            self.service.get_trending_stocks
        )

    async def nse_most_active(self, input: Dict[str, Any] = {}) -> Dict:
        return await self._safe_execute(
            self.service.get_nse_most_active
        )

    async def bse_most_active(self, input: Dict[str, Any] = {}) -> Dict:
        return await self._safe_execute(
            self.service.get_bse_most_active
        )

    async def price_shockers(self, input: Dict[str, Any] = {}) -> Dict:
        return await self._safe_execute(
            self.service.get_price_shockers
        )

    async def commodities(self, input: Dict[str, Any] = {}) -> Dict:
        return await self._safe_execute(
            self.service.get_commodities
        )

    async def mutual_funds(self, input: Dict[str, Any] = {}) -> Dict:
        return await self._safe_execute(
            self.service.get_mutual_funds
        )

    async def stock_target_price(self, input: Dict[str, Any]) -> Dict:
        return await self._safe_execute(
            self.service.get_stock_target_price,
            stock_id=input.get("stock_id")
        )

    async def stock_forecasts(self, input: Dict[str, Any]) -> Dict:
        return await self._safe_execute(
            self.service.get_stock_forecasts,
            stock_id=input.get("stock_id"),
            measure_code=input.get("measure_code"),
            period_type=input.get("period_type"),
            data_type=input.get("data_type"),
            age=input.get("age"),
        )

    async def historical_data(self, input: Dict[str, Any]) -> Dict:
        return await self._safe_execute(
            self.service.get_historical_data,
            stock_name=input.get("stock_name"),
            period=input.get("period", "5yr"),
            filter=input.get("filter", "default"),
        )

    async def historical_stats(self, input: Dict[str, Any]) -> Dict:
        return await self._safe_execute(
            self.service.get_historical_stats,
            stock_name=input.get("stock_name"),
            stats=input.get("stats"),
        )

    # ==============================
    # TOOL SCHEMA (LLM USES THIS)
    # ==============================

    def get_tool_definitions(self) -> list:
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_stock",
                    "description": "Get stock details by company name (e.g., RELIANCE)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"}
                        },
                        "required": ["name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_industry",
                    "description": "Search stocks by industry",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string"}
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "trending_stocks",
                    "description": "Get trending stocks in Indian market",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "nse_most_active",
                    "description": "Get most active stocks in NSE",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "bse_most_active",
                    "description": "Get most active stocks in BSE",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "price_shockers",
                    "description": "Get stocks with unusual price movements",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "commodities",
                    "description": "Get commodity market data",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "mutual_funds",
                    "description": "Get mutual fund data",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "stock_target_price",
                    "description": "Get analyst target price for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_id": {"type": "string"}
                        },
                        "required": ["stock_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "stock_forecasts",
                    "description": "Get stock forecast data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_id": {"type": "string"},
                            "measure_code": {"type": "string"},
                            "period_type": {"type": "string"},
                            "data_type": {"type": "string"},
                            "age": {"type": "string"}
                        },
                        "required": ["stock_id", "measure_code", "period_type", "data_type", "age"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "historical_data",
                    "description": "Get historical stock price data",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_name": {"type": "string"},
                            "period": {"type": "string"},
                            "filter": {"type": "string"}
                        },
                        "required": ["stock_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "historical_stats",
                    "description": "Get historical statistics for a stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "stock_name": {"type": "string"},
                            "stats": {"type": "string"}
                        },
                        "required": ["stock_name", "stats"]
                    }
                }
            },
        ]

    # ==============================
    # DISPATCHER (FOR AGENT LOOP)
    # ==============================

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict:
        tool = self.tool_map.get(tool_name)

        if not tool:
            return {
                "success": False,
                "error": f"Unknown tool: {tool_name}"
            }

        return await tool(arguments)


        """
        tools = IndianStockLLMTools()
        tool_defs = tools.get_tool_definitions()
        result = await tools.execute_tool(
            tool_name="get_stock",
            arguments={"name": "RELIANCE"}
        )

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "user", "content": "Give me details of Reliance stock"}
            ],
            tools=tool_defs,
            tool_choice="auto"
        )        

        from agents import Agent, function_tool

        tools_wrapper = IndianStockLLMTools()


        @function_tool
        async def get_stock(name: str):
            return await tools_wrapper.get_stock({"name": name})


        @function_tool
        async def trending_stocks():
            return await tools_wrapper.trending_stocks({})

        agent = Agent(
            name="Indian Stock Assistant",
            instructions="You are a stock market assistant for Indian markets.",
            tools=[get_stock, trending_stocks],
        )

        result = agent.run("Give me details about Reliance and trending stocks")

        print(result)

        result = agent.run("Give me details about Reliance and trending stocks")

        print(result)
        """