import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    def __init__(self):
        self.finnhub_key = settings.FINNHUB_API_KEY
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.perigon_key = settings.PERIGON_API_KEY
        self.massive_key = settings.MASSIVE_API_KEY
        self.prixe_key = settings.PRIXE_API_KEY


        self.finnhub_base = "https://finnhub.io/api/v1"


    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
    async def get_quote(self, ticker: str) -> dict:
        """
        Fetch real-time quote from Finnhub with retry logic.
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.finnhub_base}/quote",
                    params={"symbol": ticker, "token": self.finnhub_key}
                )
                response.raise_for_status()
                data = response.json()
                
                # Normalize response
                return {
                    "ticker": ticker,
                    "price": data.get("c", 0),
                    "change": data.get("d", 0),
                    "change_percent": data.get("dp", 0),
                    "high": data.get("h", 0),
                    "low": data.get("l", 0),
                    "open": data.get("o", 0),
                    "prev_close": data.get("pc", 0)
                }
            except Exception as e:
                logger.error(f"Error fetching quote for {ticker}: {e}")
                raise e

market_data = MarketDataService()
