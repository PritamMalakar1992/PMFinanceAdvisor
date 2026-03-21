from pydantic import BaseModel, Field

class SearchResult(BaseModel):
    news: str = Field(..., description="LLM formatted news string")
    source: str = "firecrawl"
    category: str