# Rate Limiter - Integration Guide

## Basic Usage

### Single Stock Quote
```python
from financial_data_fetcher import FinancialDataFetcher

fetcher = FinancialDataFetcher()
quote = fetcher.get_stock_quote('AAPL')
print(f"Price: ${quote['price']}")
```

### Turkish Stocks (BIST)
```python
# Auto-adds .IS suffix
stock = fetcher.get_turkish_stock('GARAN')
print(f"{stock['ticker']}: {stock['price']} TRY")

# Batch fetch
stocks = fetcher.get_turkish_stocks_batch(['GARAN', 'ASELS', 'KCHOL'])
```

### Dividends
```python
divs = fetcher.get_dividend_info('AKBNK.IS')
print(f"Yield: {divs['dividend_yield']}")

history = fetcher.get_dividend_history('KCHOL.IS')
print(f"Payments: {len(history['payments'])}")
```

---

## Direct Rate Limiter Usage

```python
from rate_limiter import RateLimitedAPIClient

client = RateLimitedAPIClient.get_client('finnhub')

def my_api_call():
    return requests.get("https://api.example.com/data")

result, success = client.call_with_cache_and_limit(
    my_api_call,
    query_key="my_data",
    use_cache=True
)
```

---

## Multi-Source Fallback

```python
from rate_limiter import MultiSourceDataFetcher

fetcher = MultiSourceDataFetcher()

# Tries finnhub first, then falls back to yfinance, then alpha_vantage
data, source = fetcher.fetch_with_fallback(
    'stock',
    {
        'finnhub': lambda: finnhub_client.quote('AAPL'),
        'yfinance': lambda: yf.Ticker('AAPL').info,
    },
    'quote_AAPL',
    preferred_source='finnhub'
)
print(f"Got data from: {source}")
```

---

## Decorator Pattern

```python
from rate_limiter import rate_limited_api_call

@rate_limited_api_call('finnhub', use_cache=True)
def get_quote(ticker):
    import finnhub
    client = finnhub.Client(api_key="YOUR_KEY")
    return client.quote(ticker)

# Automatically rate-limited and cached
data = get_quote('AAPL')
```

---

## Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor

tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(fetcher.get_stock_quote, tickers))
```

---

## Cache Configuration

```python
# Custom TTL per call
result, success = client.call_with_cache_and_limit(
    fetch_func,
    "query_key",
    use_cache=True,
    ttl_override=60  # 60 minutes
)

# Clear expired cache
from rate_limiter import DataCache
cache = DataCache()
cache.clear_expired()
```

---

## Monitoring

```python
# Get all statistics
stats = fetcher.get_all_stats()

# Print formatted report
fetcher.print_stats()

# Export to JSON
fetcher.export_stats('api_stats.json')
```

---

## FastAPI Integration

```python
from rate_limiter import RateLimitedAPIClient

@app.get("/stock/{ticker}")
async def get_stock(ticker: str):
    client = RateLimitedAPIClient.get_client('yfinance')
    
    def fetch():
        import yfinance as yf
        return yf.Ticker(ticker).info
    
    result, success = client.call_with_cache_and_limit(
        fetch, f"stock_{ticker}", use_cache=True
    )
    
    if not success:
        raise HTTPException(status_code=503, detail="API unavailable")
    
    return result
```
