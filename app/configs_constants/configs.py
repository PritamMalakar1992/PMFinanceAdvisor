import os
from dotenv import load_dotenv

load_dotenv()

def env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in {"1", "true", "yes", "y", "on"}

class Configs:
    NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
    MARKETAUX_KEY = os.getenv("MARKETAUX_KEY")
    FINNHUB_KEY = os.getenv("FINNHUB_KEY")
    NEWSDATA_KEY = os.getenv("NEWSDATA_KEY")
    WORLDNEWSAPI_KEY = os.getenv("WORLDNEWSAPI_KEY")
    FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
    
    # Configurable News Provider
    USE_NEWSAPI = env_bool("USE_NEWSAPI")
    USE_NEWSDATA = env_bool("USE_NEWSDATA")
    USE_WORLDNEWSAPI = env_bool("USE_WORLDNEWSAPI")
    USE_MARKETAUX = env_bool("USE_MARKETAUX")
    USE_FINNHUB = env_bool("USE_FINNHUB")

    SCREENER_USER = os.getenv("SCREENER_USER")
    SCREENER_PSWD = os.getenv("SCREENER_PSWD")