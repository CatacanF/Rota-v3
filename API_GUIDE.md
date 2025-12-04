# Dividend Income Pro API - Quick Start

## 🎯 What This API Does

Track Turkish dividend stocks, manage portfolios, and calculate dividend income automatically!

### Features:
- **10 High-Yield Turkish Stocks** (AKBNK, TUPRS, TCELL, etc.)
- **Portfolio Management** (buy/sell tracking)
- **Dividend Income Calculator**
- **Upcoming Ex-Dividend Dates**
- **Real-time Analytics**

---

## 🚀 Quick Start

### 1. Install Dependencies
```powershell
pip install fastapi uvicorn pydantic
```

### 2. Run the API
```powershell
cd c:\Users\cagda\.gemini\antigravity\playground\sonic-granule
python api.py
```

### 3. Access the API
- **API Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

---

## 📊 Available Endpoints

### Get All Dividend Stocks
```
GET /dividends/all
```
Returns all 10 Turkish dividend stocks with yields, ex-dates, and quality ratings.

### Get Upcoming Dividends
```
GET /dividends/upcoming
```
Returns stocks with upcoming ex-dividend dates, sorted by days until.

### Get Specific Stock
```
GET /dividends/TCELL.IS
```
Returns detailed info for a specific stock.

### Register User
```
POST /user/register
Body: {
  "user_id": "user123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### Add Transaction
```
POST /transaction/add
Body: {
  "user_id": "user123",
  "ticker": "AKBNK.IS",
  "shares": 100,
  "price": 12.30,
  "transaction_type": "BUY"
}
```

### Get Portfolio
```
GET /portfolio/user123
```
Returns complete portfolio with dividend income calculations.

### Get Analytics
```
GET /analytics/summary
```
Returns overall system analytics.

---

## 📈 Turkish Dividend Stocks Included

| Ticker | Name | Yield | Ex-Date | Quality |
|--------|------|-------|---------|---------|
| HALKB.IS | Halkbank | 13% | 2025-12-30 | ⭐⭐⭐⭐ |
| AKBNK.IS | Akbank | 12% | 2025-12-18 | ⭐⭐⭐⭐ |
| ISCTR.IS | İş Bankası | 11.5% | 2026-01-08 | ⭐⭐⭐⭐ |
| TUPRS.IS | Tüpraş | 11% | 2025-12-22 | ⭐⭐⭐⭐ |
| EREGL.IS | Ereğli Demir | 10% | 2025-12-25 | ⭐⭐⭐⭐ |
| BIMAS.IS | BIM | 9% | 2025-12-20 | ⭐⭐⭐⭐⭐ |
| TCELL.IS | Turkcell | 8.5% | 2025-12-15 | ⭐⭐⭐⭐⭐ |
| SAHOL.IS | Sabancı | 7.5% | 2026-01-05 | ⭐⭐⭐⭐⭐ |
| KCHOL.IS | Koç Holding | 7% | 2025-12-28 | ⭐⭐⭐⭐⭐ |
| ASELS.IS | Aselsan | 6% | 2026-01-10 | ⭐⭐⭐⭐⭐ |

---

## 💡 Example Usage

### Calculate Dividend Income

1. **Register User:**
```bash
curl -X POST http://localhost:8000/user/register \
  -H "Content-Type: application/json" \
  -d '{"user_id":"investor1","email":"investor@example.com","name":"Turkish Investor"}'
```

2. **Buy Some Stocks:**
```bash
# Buy 100 shares of Akbank
curl -X POST http://localhost:8000/transaction/add \
  -H "Content-Type: application/json" \
  -d '{"user_id":"investor1","ticker":"AKBNK.IS","shares":100,"price":12.30,"transaction_type":"BUY"}'

# Buy 50 shares of Turkcell
curl -X POST http://localhost:8000/transaction/add \
  -H "Content-Type: application/json" \
  -d '{"user_id":"investor1","ticker":"TCELL.IS","shares":50,"price":34.50,"transaction_type":"BUY"}'
```

3. **Check Portfolio:**
```bash
curl http://localhost:8000/portfolio/investor1
```

**Output:**
```json
{
  "user_id": "investor1",
  "total_value": 2955.00,
  "annual_dividend_income": 7400.00,
  "portfolio_yield": "250.42%",
  "holdings_count": 2,
  "holdings": [...]
}
```

---

## 🔗 Integration with Antigravity

This API complements the main Antigravity system:

- **main.py** generates daily reports
- **api.py** provides real-time dividend tracking API
- Both can run simultaneously

### Run Both Services:
```powershell
# Terminal 1: Main Antigravity
python main.py morning

# Terminal 2: Dividend API
python api.py
```

---

## 🎯 Next Steps

1. **Test the API** - Visit http://localhost:8000/docs
2. **Create your portfolio** - Register and add transactions
3. **Track dividends** - Monitor upcoming ex-dates
4. **Deploy to Cloud** - Use same GCP setup as main system

---

## 🔐 Production Notes

For production deployment:
- Replace in-memory database with PostgreSQL/Firestore
- Add authentication (JWT tokens)
- Integrate with real-time price feeds
- Add rate limiting
- Enable HTTPS

---

**Your dividend income tracking API is ready to run!** 🚀
