from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    city: str
    state: str
    down_payment: float
    interest_rate: float
    min_price: int
    max_price: int
    username: str = "api_user"