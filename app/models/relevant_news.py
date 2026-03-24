from pydantic import BaseModel, Field
from typing import List, Literal


class RelevantNewsItem(BaseModel):
    headline: str = Field(..., description="Original news headline")

    summary: str = Field(
        ...,
        description="2-4 line concise summary optimized for LLM consumption, including event and stock/sector impact"
    )

    impact_type: Literal["positive", "negative", "neutral", "mixed"] = Field(
        ...,
        description="Overall expected market impact"
    )

    affected_entities: List[str] = Field(
        ...,
        description="List of impacted companies, sectors, or indices (e.g., 'HDFC Bank', 'IT sector')"
    )

    reason_for_selection: str = Field(
        ...,
        description="One-line explanation of why this news is relevant for stock selection"
    )


class NewsAnalysisOutput(BaseModel):
    relevant_news: List[RelevantNewsItem] = Field(
        ...,
        description="List of filtered and summarized relevant news items"
    )