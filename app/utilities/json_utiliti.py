from datetime import datetime
from pathlib import Path
import json
from typing import Optional, List, Any
import pandas as pd
from pydantic import FilePath
import os

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
    folder = folder_name or "json_outputs"

    dir_path = root / folder
    dir_path.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y-%m-%d_%I-%M-%p")
    original = Path(filename)
    stamped_name = f"{original.stem}-{ts}{original.suffix or '.json'}"

    return dir_path / stamped_name

def save_json(
    json_list: List[Any],        
    filename: str = "payload.json",
    folder_name: Optional[str] = None,
    base_path: Optional[str] = None
    ) -> Path:

    file_path = _build_path(base_path, folder_name, filename)
    records = _add_index(json_list)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(
            records,
            f,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return file_path

def save_json_without_index(
    data: Any,     
    filename: str = "payload.json",
    folder_name: Optional[str] = None,
    base_path: Optional[str] = None    
    ) -> None:

    file_path = _build_path(base_path, folder_name, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)    

def save_dataframe_as_json(
    df: pd.DataFrame,
    save_in_disk: bool = True,
    filename: str = "payload.json",
    folder_name: Optional[str] = "json_outputs",
    base_path: Optional[str] = None,
    orient: str = "records",
    clean: bool = True
    ) -> None:

    if df is None or df.empty:
        raise ValueError("DataFrame is empty or None")

    file_path = _build_path(base_path, folder_name, filename)

    if clean:
        df = df.copy()

        for col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("%", "", regex=False)
                .str.strip()
            )

            #df[col] = pd.to_numeric(df[col], errors="ignore")
            converted = pd.to_numeric(df[col], errors="coerce")
            df[col] = converted.where(converted.notna(), df[col])

    # All columns after CMP Rs. are not needed for the JSON conversion or in output for return calculation, actual dataframe untouched for further analysis by LLM
    end_idx = df.columns.get_loc("CMP Rs.") + 1
    df_json_data = df.to_dict(orient=orient)
    json_data = df.iloc[:, :end_idx].to_dict(orient=orient)

    if save_in_disk:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(df_json_data, f, indent=4, ensure_ascii=False)

    print(f"JSON saved at: {file_path}")
    return df_json_data      

def save_llm_news_json(
    data: Any,
    save_in_disk: bool = True,
    filename: str = "news_output.json",
    folder_name: Optional[str] = None,
    base_path: Optional[str] = None
    ) -> Path:

    file_path = _build_path(base_path, folder_name, filename)

    # Case 1: Full Pydantic response (NewsAnalysisOutput)
    if hasattr(data, "model_dump"):
        payload = data.model_dump(mode="json", exclude_none=True)

    # Case 2: List of RelevantNewsItem
    elif isinstance(data, list):
        payload = {
            "relevant_news": [
                item.model_dump(mode="json", exclude_none=True)
                if hasattr(item, "model_dump")
                else item
                for item in data
            ]
        }

    else:
        raise ValueError("Unsupported data type for LLM news saving")
    if save_in_disk:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                payload,
                f,
                indent=2,
                ensure_ascii=False,
            )

    return payload    

def load_dataframe_from_json(
    filename: str = "newfile.json",
    folder_name: Optional[str] = "json_outputs"
) -> pd.DataFrame:

    file_path = f"{folder_name}\\{filename}.json"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    df = pd.DataFrame(json_data)

    print(f"DataFrame loaded from: {file_path}")
    return df