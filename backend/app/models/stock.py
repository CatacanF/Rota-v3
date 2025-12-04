from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger
from sqlalchemy.sql import func
from app.db.base import Base

class Stock(Base):
    __tablename__ = "stocks"

    ticker = Column(String, primary_key=True, index=True)
    company_name = Column(String)
    sector = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class StockPrice(Base):
    """
    Time-series data for stock prices.
    Optimized for TimescaleDB (hypertable).
    """
    __tablename__ = "stock_prices"

    time = Column(DateTime(timezone=True), primary_key=True, index=True)
    ticker = Column(String, primary_key=True, index=True) # Composite PK
    price = Column(Float)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(BigInteger)
