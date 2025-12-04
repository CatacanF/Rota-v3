from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.market_data import market_data
from app.schemas.stock import StockPrice
from typing import List

router = APIRouter()

@router.get("/{ticker}/quote", response_model=StockPrice)
async def get_stock_quote(ticker: str, db: AsyncSession = Depends(get_db)):
    """
    Get real-time stock quote.
    """
    try:
        # 1. Try to get from external API
        quote = await market_data.get_quote(ticker)
        
        # 2. (Optional) Save to DB here or rely on background worker
        # For now, we just return the live data
        return {
            "ticker": quote["ticker"],
            "price": quote["price"],
            "change": quote["change"],
            "change_percent": quote["change_percent"],
            "volume": 0, # Finnhub basic quote doesn't always have volume
            "timestamp": "2023-12-05T10:00:00Z" # Placeholder, should be real time
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/watchlist", response_model=List[StockPrice])
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    """
    Get quotes for the default watchlist.
    """
    watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    results = []
    for ticker in watchlist:
        try:
            quote = await market_data.get_quote(ticker)
            results.append({
                "ticker": quote["ticker"],
                "price": quote["price"],
                "change": quote["change"],
                "change_percent": quote["change_percent"],
                "volume": 0,
                "timestamp": "2023-12-05T10:00:00Z"
            })
        except Exception:
            continue # Skip failed fetches
    return results
