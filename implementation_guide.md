# Implementation Guide

Technical implementation details and architecture overview.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Antigravity                        │
│                   Main Orchestrator (main.py)               │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │  Core   │  │  v2.0   │  │ Support │
    │ Modules │  │ Modules │  │ Systems │
    └────┬────┘  └────┬────┘  └────┬────┘
         │             │             │
    ┌────▼────────────▼─────────────▼────┐
    │    Data Layer (Firestore/Storage)  │
    └────────────────────────────────────┘
```

---

## Module Breakdown

### Core Modules (8)

#### 1. News Aggregator
**Purpose**: Collect financial news from multiple sources  
**Dependencies**: `requests`, `feedparser`, `finnhub-python`  
**Data Sources**:
- RSS feeds (Bloomberg, Reuters, Seeking Alpha)
- Finnhub News API
- Turkish news sources (configurable)

**Key Methods**:
- `fetch_rss_news()`: Parses RSS feeds
- `fetch_finnhub_news()`: Gets news from Finnhub API
- `aggregate_all_news()`: Combines all sources

#### 2. LLM Analysis
**Purpose**: Generate AI-powered market insights  
**Dependencies**: `openai`, `requests` (for Perplexity)  
**APIs**: OpenAI GPT-4, Perplexity

**Key Methods**:
- `analyze_with_openai()`: Uses GPT-4 for analysis
- `analyze_with_perplexity()`: Real-time web search analysis
- `generate_market_summary()`: Creates executive summaries

#### 3. Price Integrator
**Purpose**: Fetch real-time price data  
**Dependencies**: `yfinance`, `finnhub-python`  
**Data Sources**: Yahoo Finance, Finnhub

**Key Methods**:
- `get_stock_price()`: Single ticker price
- `get_batch_prices()`: Multiple tickers
- `get_turkish_stocks()`: BIST stocks (.IS suffix)
- `get_forex_rate()`: Currency pairs

#### 4. Ticker Screener
**Purpose**: Filter stocks by criteria  
**Dependencies**: `price_integrator`

**Screens Available**:
- Performance-based (>X% gain)
- Volume spikes
- Value stocks (P/E < 15)
- Dividend yield (>X%)
- Momentum (>X% change)

#### 5. Sentiment Analyzer
**Purpose**: Analyze market sentiment from text  
**Dependencies**: `textblob`, `vaderSentiment`

**Sentiment Scores**:
- **Compound**: -1.0 to +1.0 (overall sentiment)
- **Positive/Negative/Neutral**: Component scores
- **Polarity**: TextBlob alternative measure

#### 6. Sector Backtest
**Purpose**: Analyze sector performance and rotation  
**Sectors Tracked**:
- US: Technology, Finance, Healthcare, Energy, Consumer, Industrial
- Turkey: Banking, Industrial, Energy, Auto

**Key Metrics**:
- Average sector performance
- Breadth (positive/negative stocks)
- Rotation signals

#### 7. Economic Calendar
**Purpose**: Track major economic events  
**Calendars**:
- Turkish CBT meetings (12 dates/year)
- Turkish inflation reports (12 dates/year)
- Fed FOMC meetings (8 dates/year)
- ECB meetings (8 dates/year)

**Methods**:
- `get_upcoming_events()`: Next N days
- `get_event_alerts()`: Events within alert window

#### 8. Main Orchestrator
**Purpose**: Coordinate all modules and generate reports  
**Report Types**:
- Morning Brief
- Midday Update
- Evening Wrap

**Workflow**:
1. Aggregate news
2. Analyze sentiment
3. Fetch prices
4. Check economic calendar
5. Detect macro regime
6. Generate LLM summary
7. Create alerts
8. Format and output

---

### v2.0 Modules (4 Innovative)

#### 1. Macro Regime Detector
**Purpose**: Identify current economic environment  
**Innovation**: Automated regime classification

**Regimes**:
- Goldilocks (↑growth, ↓inflation)
- Inflationary (↑growth, ↑inflation)
- Stagflation (↓growth, ↑inflation)
- Deflationary (↓growth, ↓inflation)
- Reflation (↑growth from low base)

**Usage**:
```python
regime = detector.detect_regime({
    'gdp_growth': 2.8,
    'inflation_rate': 3.2,
    'unemployment': 4.5
})
# Returns: regime name, best assets, confidence
```

#### 2. Geopolitical Monitor
**Purpose**: Track global risks and market impact  
**Innovation**: Automated geopolitical risk scoring

**Risk Categories**:
- Military conflict (1.5x multiplier)
- Trade war (1.2x)
- Political crisis (1.0x)
- Sanctions (1.3x)
- Elections (0.8x)
- Central bank actions (1.4x)

**Risk Levels**: Low → Moderate → High → Critical

#### 3. Portfolio Analyzer
**Purpose**: Calculate portfolio risk metrics  
**Innovation**: Comprehensive risk analysis

**Metrics**:
- **Sharpe Ratio**: (Return - RF) / Volatility
- **Max Drawdown**: Peak-to-trough loss
- **VaR 95%**: 1-day loss potential
- **Herfindahl Index**: Concentration risk

**Asset Allocation**:
- Analyzes by asset class
- Analyzes by sector
- Recommends rebalancing

#### 4. Alert Engine
**Purpose**: Real-time monitoring and notifications  
**Innovation**: Multi-severity, multi-channel system

**Severity Levels**:
1. Info (Log only)
2. Notice (Email)
3. Warning (Email + Slack)
4. Critical (Email + Slack + SMS)
5. Emergency (All + Voice)

**Alert Types**:
- Price movements
- Volume spikes
- News events
- Economic data
- Geopolitical events
- Portfolio risk
- Technical signals

---

## Data Flow

```
1. Scheduled Job (Cloud Scheduler)
         ↓
2. Main Orchestrator triggered
         ↓
3. Parallel data collection:
   - News Aggregator
   - Price Integrator
   - Economic Calendar
         ↓
4. Analysis layer:
   - Sentiment Analyzer
   - Macro Regime Detector
   - Geopolitical Monitor
   - Portfolio Analyzer
         ↓
5. Alert Generation:
   - Alert Engine checks thresholds
         ↓
6. LLM Synthesis:
   - Generate executive summary
         ↓
7. Report Formatting
         ↓
8. Output:
   - Console/Logs
   - Firestore storage
   - Slack/Email delivery
```

---

## API Integration

### Required APIs

| API | Purpose | Cost | Rate Limits |
|-----|---------|------|-------------|
| Finnhub | Price data, news | $0-79/mo | 60 calls/min free |
| OpenAI | LLM analysis | ~$10-30/mo | 3 RPM (free tier) |
| Perplexity | Web search | $20/mo | 5 RPM (standard) |

### Optional APIs

| API | Purpose | Setup |
|-----|---------|-------|
| Slack | Notifications | Create webhook |
| Twilio | SMS alerts | Add credentials |
| SendGrid | Email | Add API key |

---

## Storage Architecture

### Firestore Collections

```
users/
  ├── {user_id}/
  │   ├── email
  │   ├── preferences
  │   └── alert_settings

reports/
  ├── {report_id}/
  │   ├── type (morning/midday/evening)
  │   ├── timestamp
  │   ├── content (JSON)
  │   └── sentiment

alerts/
  ├── {alert_id}/
  │   ├── severity
  │   ├── type
  │   ├── message
  │   ├── acknowledged
  │   └── timestamp

market_data/
  ├── cache/
  │   ├── prices
  │   ├── news
  │   └── sentiment
```

---

## Deployment Architecture

### Cloud Run

**Configuration**:
- Memory: 2GB
- CPU: 1
- Concurrency: 80
- Max instances: 10
- Timeout: 300s

**Endpoints** (future implementation):
- `/api/v1/reports/morning` - Generate morning report
- `/api/v1/reports/midday` - Generate midday update
- `/api/v1/reports/evening` - Generate evening wrap
- `/health` - Health check

### Cloud Scheduler

**Jobs**:
1. Morning Brief: `0 8 * * 1-5` (Europe/Istanbul)
2. Midday Update: `0 13 * * 1-5` (Europe/Istanbul)
3. Evening Wrap: `0 18 * * 1-5` (Europe/Istanbul)
4. Hourly Monitor: `0 * * * 1-5` (Europe/Istanbul)

---

## Extension Points

### Adding New Modules

1. Create `new_module.py` with class
2. Import in `main.py`
3. Initialize in `__init__()`
4. Call in appropriate report

### Adding New Data Sources

1. Add fetcher method to relevant module
2. Update `aggregate_all_news()` or equivalent
3. Handle errors gracefully

### Custom Alerts

```python
# In alert_engine.py
def check_custom_alert(self, ...):
    if condition_met:
        return self.create_alert(
            alert_type='custom',
            severity=3,
            message='Custom alert triggered',
            metadata={...}
        )
```

---

## Performance Optimization

### Caching Strategy
- Cache price data: 5 minutes
- Cache news: 15 minutes
- Cache sentiment: 30 minutes

### Batch Processing
- Fetch prices in batches (not individually)
- Aggregate news before sentiment analysis
- Minimize API calls

### Error Handling
- Graceful degradation (missing data → continue with available)
- Retry logic for API failures
- Logging for debugging

---

## Security Best Practices

1. **Never commit API keys** - Use Secret Manager
2. **Validate inputs** - Sanitize user data
3. **Rate limiting** - Prevent abuse
4. **Secure endpoints** - Use authentication
5. **Monitor access** - Log all API calls

---

## Testing

### Unit Tests (future implementation)
```bash
pytest tests/test_news_aggregator.py
pytest tests/test_sentiment_analyzer.py
```

### Integration Tests
```bash
python main.py morning  # Full workflow test
```

### Performance Tests
- Report generation time: < 60 seconds
- API latency: < 500ms (p95)

---

## Monitoring

### Key Metrics
- Report success rate
- API error rate
- Alert delivery time
- Average report generation time

### Logs to Monitor
- Module initialization
- Data fetching errors
- Alert generation
- Report completion

---

**For deployment instructions, see `deployment_guide.md`**
