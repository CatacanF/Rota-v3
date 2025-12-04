# Rota-v1 Backend Startup Guide

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd c:\Users\cagda\.gemini\antigravity\playground\sonic-granule
pip install -r requirements.txt
```

### 2. Start the Backend

**Option A: Using Python directly**
```bash
python -m uvicorn app.main:app --reload --port 8000
```

**Option B: Using the startup script (Linux/Mac/Git Bash)**
```bash
chmod +x start.sh
./start.sh
```

**Option C: Using PowerShell**
```powershell
uvicorn app.main:app --reload --port 8000
```

### 3. Verify Backend is Running

Open your browser and visit:
- **Health Check**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 📡 Available Endpoints

### Stocks API (`/api/stocks`)

- `GET /api/stocks/watchlist` - Get all Turkish dividend stocks
- `GET /api/stocks/{ticker}/quote` - Get single stock quote
- `GET /api/stocks/{ticker}/dividends` - Get dividend information
- `GET /api/stocks/multiple?tickers=GARAN.IS,EREGL.IS` - Get multiple quotes

### Calendar API (`/api/calendar`)

- `GET /api/calendar/events` - Get economic calendar events
- Query params: `date`, `country`, `impact`

### Stats API (`/api/stats`)

- `GET /api/stats` - Get API health statistics

### WebSocket

- `WS /ws/quotes` - Real-time stock price updates

## 🧪 Testing Endpoints

### Using curl

```bash
# Health check
curl http://localhost:8000/

# Get watchlist
curl http://localhost:8000/api/stocks/watchlist

# Get single quote
curl http://localhost:8000/api/stocks/GARAN.IS/quote

# Get calendar events
curl http://localhost:8000/api/calendar/events

# Get API stats
curl http://localhost:8000/api/stats
```

### Using Browser

Simply open http://localhost:8000/docs to use the interactive Swagger UI!

## 🔗 Frontend Integration

Once the backend is running on port 8000, your React frontend (running on port 5173) will automatically connect via the Vite proxy configuration.

**Start both servers:**

1. **Terminal 1 - Backend:**
   ```bash
   cd c:\Users\cagda\.gemini\antigravity\playground\sonic-granule
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd c:\Users\cagda\.gemini\antigravity\playground\sonic-granule\frontend
   npm run dev
   ```

3. **Open Browser:**
   - Frontend: http://localhost:5173
   - Backend API Docs: http://localhost:8000/docs

## ✅ Expected Behavior

When both servers are running:
- ✅ Frontend loads without "Failed to load API stats" error
- ✅ Dashboard shows real API statistics
- ✅ Stocks page displays 8 Turkish stocks from backend
- ✅ Calendar shows economic events
- ✅ Stats page displays API health metrics
- ✅ No CORS errors in browser console

## 🐛 Troubleshooting

**Backend won't start:**
- Check if port 8000 is already in use
- Verify Python and uvicorn are installed
- Check for syntax errors in the output

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check Vite proxy configuration in `vite.config.ts`
- Look for CORS errors in browser console

**Import errors:**
- Make sure you're in the correct directory
- Verify `app/__init__.py` and `app/routers/__init__.py` exist
- Check Python path includes the project root

## 📊 Mock Data

The backend currently serves mock data for:
- 8 Turkish stocks (GARAN.IS, EREGL.IS, TUPRS.IS, etc.)
- 8 economic calendar events
- API health statistics

This allows full frontend testing without external API dependencies!
