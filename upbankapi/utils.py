from datetime import datetime
from typing import Optional, Any, Dict


class Filters(dict):
    def __init__(self, page_size: int = None, limit: int = None, filters: Dict = None):
        super().__init__()
        if page_size:
            if limit and limit < page_size:
                page_size = limit
            self["page[size]"] = page_size
        if filters:
            for k, v in filters.items():
                self.filter(k, v)

    def filter(self, name: str, value: Optional[Any]):
        if value is None:
            return
        if isinstance(value, datetime):
            value = value.astimezone().isoformat()
        self[f"filter[{name}]"] = value
        return self
