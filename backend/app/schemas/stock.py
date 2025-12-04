from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StockBase(BaseModel):
    ticker: str
    company_name: str
    sector: str

class StockCreate(StockBase):
    pass

class Stock(StockBase):
    created_at: datetime

    class Config:
        from_attributes = True

class StockPrice(BaseModel):
    ticker: str
    price: float
    change: float
    change_percent: float
    volume: int
    timestamp: datetime

    class Config:
        from_attributes = True
