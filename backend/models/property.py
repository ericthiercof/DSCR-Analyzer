from pydantic import BaseModel
from typing import Optional

class PropertyResult(BaseModel):
    address: str
    price: int
    monthly_payment: float
    rent: int
    rent_type: str
    dscr: float
    hoa_fee: float
    tax_rate: float
    zpid: str
    zillow_url: str
    insurance_cost: float
    bedrooms: Optional[int]
    bathrooms: Optional[int]