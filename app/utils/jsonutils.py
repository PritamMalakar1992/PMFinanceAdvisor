from datetime import datetime
from pathlib import Path
import json
from typing import Optional, List, Any


def _to_dict(item: Any) -> dict:
    if hasattr(item, "model_dump"):
        return item.model_dump(mode="json")
    if hasattr(item, "dict"):
        return item.dict()
    if isinstance(item, dict):
        return item
    return {"value": item}

def _add_index(records: List[Any]) -> List[dict]:
    return [
        {"index": i + 1, **_to_dict(item)}
        for i, item in enumerate(records)
    ]

def _build_path(
    base_path: Optional[str],
    folder_name: Optional[str],
    filename: str
) -> Path:
    root = Path(base_path) if base_path else Path.cwd()
    folder = folder_name or "newsdump"

    dir_path = root / folder
    dir_path.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    original = Path(filename)
    stamped_name = f"{original.stem}-{ts}{original.suffix or '.json'}"

    return dir_path / stamped_name

def save_news(
    news_list: List[Any],
    base_path: Optional[str] = None,
    folder_name: Optional[str] = None,
    filename: str = "news.json"
) -> Path:

    file_path = _build_path(base_path, folder_name, filename)
    records = _add_index(news_list)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return file_path