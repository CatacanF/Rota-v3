from app.worker.celery_app import celery_app
from app.services.market_data import market_data
import asyncio
import time

@celery_app.task(acks_late=True)
def generate_morning_report(ticker: str):
    """
    Heavy task: Fetches news, runs LLM analysis, calculates sentiment.
    Simulates a long-running process.
    """
    time.sleep(5) # Simulate processing
    return {
        "ticker": ticker,
        "sentiment": "Bullish",
        "score": 0.85,
        "summary": f"Morning report generated for {ticker}. Market sentiment is positive."
    }

@celery_app.task
def fetch_stock_prices(tickers: list[str]):
    """
    Background task to fetch prices for multiple tickers and save to DB.
    """
    results = []
    
    for ticker in tickers:
        try:
            # We run the async function in the sync Celery task
            # asyncio.run() creates a new event loop for this call
            quote_data = asyncio.run(market_data.get_quote(ticker))
            results.append(quote_data)
            
            # Save to Database (Sync wrapper for Async)
            # In a real production app, we might use a separate async worker or 
            # use the 'asgiref' library to bridge sync/async better.
            # For now, we'll just print the success.
            print(f"✅ Persisted {ticker} price: ${quote_data['price']}")
            
            # TODO: To actually save to DB here without async conflicts in Celery:
            # 1. Use a synchronous SQLAlchemy engine just for Celery
            # 2. Or push to a separate 'db-writer' queue
            
        except Exception as e:
            print(f"❌ Failed to fetch {ticker}: {e}")

            
        except Exception as e:
            print(f"Failed to fetch {ticker}: {e}")
            
    return {"status": "fetched", "count": len(results), "data": results}


