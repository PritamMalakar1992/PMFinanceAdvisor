from datetime import date
from pydantic import BaseModel

class News(BaseModel):
    news: str
    date: date
    source: str
    category: str

class NewsList(BaseModel):
    newslist: list[News]    