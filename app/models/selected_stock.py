from typing import List
from pydantic import BaseModel, Field


class SelectedStock(BaseModel):
    name: str = ""
    cmp: float = 0.0
    score: float = 0.0
    confidence: float = 0.0
    investment_amount: float = 0.0
    shares: float = 0.0
    allocation_ratio: int = 0   # ✅ FIXED (integer % only)
    reason: str = ""
    buy_or_Sell: str = ""
    target_price: str = ""
    comments_from_judge: str = ""


class StockSelectionOutput(BaseModel):
    selected_stocks: List[SelectedStock] = Field(default_factory=list)