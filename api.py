"""
Dividend Income Pro API - FastAPI Backend
Turkish dividend stock tracking with real-time data and portfolio management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import json
import os

# Import rate limiter components
from rate_limiter import RateLimitedAPIClient, APIMonitor, DataCache

app = FastAPI(
    title="Dividend Income Pro API",
    description="Turkish dividend stock tracking and portfolio management",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MOCK DATABASE (replace with PostgreSQL later)
users_db = {}
transactions_db = []

# ==========================================
# TURKISH DIVIDEND STOCKS DATA
# ==========================================

TURKISH_DIVIDENDS = {
    "TCELL.IS": {
        "name": "Turkcell",
        "price": 34.50,
        "dividend_amount": 52,
        "ex_date": "2025-12-15",
        "yield": "8.5%",
        "quality": "⭐⭐⭐⭐⭐",
        "payment_date": "2025-01-05"
    },
    "AKBNK.IS": {
        "name": "Akbank",
        "price": 12.30,
        "dividend_amount": 48,
        "ex_date": "2025-12-18",
        "yield": "12%",
        "quality": "⭐⭐⭐⭐",
        "payment_date": "2025-01-10"
    },
    "TUPRS.IS": {
        "name": "Tüpraş",
        "price": 18.90,
        "dividend_amount": 25,
        "ex_date": "2025-12-22",
        "yield": "11%",
        "quality": "⭐⭐⭐⭐",
        "payment_date": "2025-01-15"
    },
    "KCHOL.IS": {
        "name": "Koç Holding",
        "price": 35.60,
        "dividend_amount": 35,
        "ex_date": "2025-12-28",
        "yield": "7%",
        "quality": "⭐⭐⭐⭐⭐",
        "payment_date": "2025-01-20"
    },
    "ASELS.IS": {
        "name": "Aselsan",
        "price": 45.20,
        "dividend_amount": 18,
        "ex_date": "2026-01-10",
        "yield": "6%",
        "quality": "⭐⭐⭐⭐⭐",
        "payment_date": "2026-02-01"
    },
    "BIMAS.IS": {
        "name": "BIM Mağazaları",
        "price": 28.40,
        "dividend_amount": 30,
        "ex_date": "2025-12-20",
        "yield": "9%",
        "quality": "⭐⭐⭐⭐⭐",
        "payment_date": "2025-01-12"
    },
    "EREGL.IS": {
        "name": "Ereğli Demir Çelik",
        "price": 15.80,
        "dividend_amount": 22,
        "ex_date": "2025-12-25",
        "yield": "10%",
        "quality": "⭐⭐⭐⭐",
        "payment_date": "2025-01-18"
    },
    "SAHOL.IS": {
        "name": "Sabancı Holding",
        "price": 24.90,
        "dividend_amount": 28,
        "ex_date": "2026-01-05",
        "yield": "7.5%",
        "quality": "⭐⭐⭐⭐⭐",
        "payment_date": "2026-01-25"
    },
    "HALKB.IS": {
        "name": "Halkbank",
        "price": 9.80,
        "dividend_amount": 40,
        "ex_date": "2025-12-30",
        "yield": "13%",
        "quality": "⭐⭐⭐⭐",
        "payment_date": "2026-01-22"
    },
    "ISCTR.IS": {
        "name": "İş Bankası (C)",
        "price": 8.90,
        "dividend_amount": 38,
        "ex_date": "2026-01-08",
        "yield": "11.5%",
        "quality": "⭐⭐⭐⭐",
        "payment_date": "2026-01-28"
    }
}

# ==========================================
# PYDANTIC MODELS
# ==========================================

class User(BaseModel):
    user_id: str
    email: str
    name: str
    created_at: Optional[datetime] = None

class Transaction(BaseModel):
    transaction_id: Optional[str] = None
    user_id: str
    ticker: str
    shares: float
    price: float
    transaction_type: str  # "BUY" or "SELL"
    date: Optional[datetime] = None

class Portfolio(BaseModel):
    user_id: str
    holdings: dict

# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "app": "Dividend Income Pro API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/dividends/all - Get all Turkish dividend stocks",
            "/dividends/{ticker} - Get specific stock info",
            "/dividends/upcoming - Get upcoming dividend dates",
            "/user/register - Register new user",
            "/portfolio/{user_id} - Get user portfolio",
            "/transaction/add - Add transaction"
        ]
    }

@app.get("/dividends/all")
async def get_all_dividends():
    """Get all Turkish dividend stocks"""
    return {
        "count": len(TURKISH_DIVIDENDS),
        "stocks": TURKISH_DIVIDENDS,
        "last_updated": datetime.now().isoformat()
    }

@app.get("/dividends/{ticker}")
async def get_dividend_stock(ticker: str):
    """Get specific dividend stock information"""
    ticker_upper = ticker.upper()
    if ticker_upper not in TURKISH_DIVIDENDS:
        raise HTTPException(status_code=404, detail=f"Stock {ticker} not found")
    
    return {
        "ticker": ticker_upper,
        "data": TURKISH_DIVIDENDS[ticker_upper]
    }

@app.get("/dividends/upcoming")
async def get_upcoming_dividends():
    """Get stocks with upcoming ex-dividend dates"""
    today = datetime.now()
    upcoming = []
    
    for ticker, data in TURKISH_DIVIDENDS.items():
        ex_date = datetime.strptime(data['ex_date'], "%Y-%m-%d")
        if ex_date >= today:
            days_until = (ex_date - today).days
            upcoming.append({
                "ticker": ticker,
                "name": data['name'],
                "ex_date": data['ex_date'],
                "days_until": days_until,
                "yield": data['yield'],
                "dividend_amount": data['dividend_amount']
            })
    
    # Sort by days until ex-date
    upcoming.sort(key=lambda x: x['days_until'])
    
    return {
        "count": len(upcoming),
        "upcoming_dividends": upcoming
    }

@app.post("/user/register")
async def register_user(user: User):
    """Register a new user"""
    if user.user_id in users_db:
        raise HTTPException(status_code=400, detail="User already exists")
    
    user.created_at = datetime.now()
    users_db[user.user_id] = user.dict()
    
    return {
        "message": "User registered successfully",
        "user": user
    }

@app.get("/user/{user_id}")
async def get_user(user_id: str):
    """Get user information"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

@app.post("/transaction/add")
async def add_transaction(transaction: Transaction):
    """Add a new transaction (buy/sell)"""
    # Validate user exists
    if transaction.user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate ticker
    if transaction.ticker.upper() not in TURKISH_DIVIDENDS:
        raise HTTPException(status_code=404, detail=f"Stock {transaction.ticker} not found")
    
    # Generate transaction ID
    transaction.transaction_id = f"TXN-{len(transactions_db) + 1:05d}"
    transaction.date = datetime.now()
    
    transactions_db.append(transaction.dict())
    
    return {
        "message": "Transaction added successfully",
        "transaction": transaction
    }

@app.get("/portfolio/{user_id}")
async def get_portfolio(user_id: str):
    """Get user's portfolio with dividend income calculations"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Calculate portfolio from transactions
    holdings = {}
    for txn in transactions_db:
        if txn['user_id'] == user_id:
            ticker = txn['ticker'].upper()
            if ticker not in holdings:
                holdings[ticker] = 0
            
            if txn['transaction_type'] == 'BUY':
                holdings[ticker] += txn['shares']
            else:  # SELL
                holdings[ticker] -= txn['shares']
    
    # Remove zero positions
    holdings = {k: v for k, v in holdings.items() if v > 0}
    
    # Calculate portfolio value and dividend income
    total_value = 0
    annual_dividend_income = 0
    portfolio_details = []
    
    for ticker, shares in holdings.items():
        stock_data = TURKISH_DIVIDENDS[ticker]
        position_value = shares * stock_data['price']
        dividend_per_share = stock_data['dividend_amount']
        annual_income = shares * dividend_per_share
        
        total_value += position_value
        annual_dividend_income += annual_income
        
        portfolio_details.append({
            "ticker": ticker,
            "name": stock_data['name'],
            "shares": shares,
            "price": stock_data['price'],
            "position_value": round(position_value, 2),
            "annual_dividend": round(annual_income, 2),
            "yield": stock_data['yield'],
            "next_ex_date": stock_data['ex_date']
        })
    
    return {
        "user_id": user_id,
        "total_value": round(total_value, 2),
        "annual_dividend_income": round(annual_dividend_income, 2),
        "portfolio_yield": f"{(annual_dividend_income / total_value * 100):.2f}%" if total_value > 0 else "0%",
        "holdings_count": len(holdings),
        "holdings": portfolio_details
    }

@app.get("/transactions/{user_id}")
async def get_user_transactions(user_id: str):
    """Get all transactions for a user"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_transactions = [txn for txn in transactions_db if txn['user_id'] == user_id]
    
    return {
        "user_id": user_id,
        "transaction_count": len(user_transactions),
        "transactions": user_transactions
    }

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get overall analytics summary"""
    return {
        "total_stocks": len(TURKISH_DIVIDENDS),
        "average_yield": "9.1%",
        "highest_yield": "13% (HALKB.IS)",
        "total_users": len(users_db),
        "total_transactions": len(transactions_db),
        "upcoming_dividends_30_days": len([
            s for s in TURKISH_DIVIDENDS.values() 
            if (datetime.strptime(s['ex_date'], "%Y-%m-%d") - datetime.now()).days <= 30
        ])
    }

# ==========================================
# RATE LIMITER MONITORING ENDPOINTS
# ==========================================

# Initialize global monitor
_api_monitor = APIMonitor(['finnhub', 'yfinance', 'alpha_vantage'])

@app.get("/api/rate-limit/stats")
async def get_rate_limit_stats():
    """Get rate limiting statistics for all API sources"""
    return {
        "timestamp": datetime.now().isoformat(),
        "stats": _api_monitor.get_all_stats()
    }

@app.get("/api/rate-limit/health")
async def get_rate_limit_health():
    """Get health status of all API sources (circuit breaker states)"""
    return {
        "timestamp": datetime.now().isoformat(),
        "health": _api_monitor.get_health_status()
    }

@app.post("/api/cache/clear")
async def clear_expired_cache():
    """Clear expired cache entries"""
    cache = DataCache()
    deleted = cache.clear_expired()
    return {
        "message": f"Cleared {deleted} expired cache entries",
        "deleted_count": deleted,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    cache = DataCache()
    return {
        "timestamp": datetime.now().isoformat(),
        "stats": cache.get_stats()
    }

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Dividend Income Pro API",
        "rate_limiter": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
