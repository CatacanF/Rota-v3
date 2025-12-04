# Rate Limiter - Setup Guide

## Quick Start (30 seconds)

### 1. Dependencies
```bash
pip install finnhub-python yfinance requests pandas
```

### 2. Set API Keys
Add to your `.env` file:
```env
FINNHUB_API_KEY=your_key_here
ALPHA_VANTAGE_API_KEY=your_key_here
```

### 3. Use It
```python
from financial_data_fetcher import FinancialDataFetcher

fetcher = FinancialDataFetcher()
quote = fetcher.get_stock_quote('AAPL')
print(f"Price: ${quote['price']}")
```

---

## Files Created

| File | Purpose |
|------|---------|
| `rate_limiter.py` | Core rate limiting engine |
| `financial_data_fetcher.py` | Ready-to-use data fetcher |
| `data/stock_data_cache.db` | SQLite cache (auto-created) |

---

## Rate Limits by Source

| Source | Rate Limit | Cache TTL |
|--------|-----------|-----------|
| Finnhub | 5 req/sec | 10 min |
| Yahoo Finance | 2 req/sec | 15 min |
| Alpha Vantage | 5 req/min | 30 min |
| IEX Cloud | 100 req/sec | 5 min |

---

## Monitoring

### API Endpoints
```
GET  /api/rate-limit/stats   - View statistics
GET  /api/rate-limit/health  - Check circuit breakers
GET  /api/cache/stats        - Cache statistics
POST /api/cache/clear        - Clear expired cache
```

### In Code
```python
fetcher.print_stats()  # Print usage report
fetcher.export_stats('stats.json')  # Export to file
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Rate limit errors | Increase cache TTL, reduce request frequency |
| Cache not working | Check `data/` folder permissions |
| API key errors | Verify `.env` file is loaded |

---

## Run Tests
```bash
# Verify imports
python -c "from rate_limiter import RateLimitedAPIClient; print('OK')"

# Start API server
python -m uvicorn api:app --reload
```
