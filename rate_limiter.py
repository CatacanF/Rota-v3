"""
Rate Limiter System for Financial Data APIs
Enhanced version with thread safety, circuit breaker, and singleton pattern.
Handles rate limits for Yahoo Finance, Finnhub, Alpha Vantage, and other sources

Author: Financial Data Management System
Version: 2.0.0
"""

import time
import json
import sqlite3
import logging
import random
from functools import wraps
from datetime import datetime, timedelta
from collections import deque
from typing import Any, Callable, Dict, Optional, List, Tuple
from threading import Lock, RLock
from contextlib import contextmanager
from enum import Enum, auto

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

class RateLimitConfig:
    """Configuration for different API sources"""
    
    CONFIGS = {
        'yahoo_finance': {
            'requests_per_second': 2,
            'max_retries': 5,
            'backoff_factor': 1.5,
            'cache_ttl_minutes': 15,
            'timeout': 10,
        },
        'finnhub': {
            'requests_per_second': 5,  # Free tier: 30/sec, but we're conservative
            'max_retries': 3,
            'backoff_factor': 2,
            'cache_ttl_minutes': 10,
            'timeout': 10,
        },
        'alpha_vantage': {
            'requests_per_second': 0.2,  # 5 per minute (free tier)
            'max_retries': 3,
            'backoff_factor': 2,
            'cache_ttl_minutes': 30,
            'timeout': 15,
        },
        'iex_cloud': {
            'requests_per_second': 100,
            'max_retries': 3,
            'backoff_factor': 1.5,
            'cache_ttl_minutes': 5,
            'timeout': 10,
        },
        'yfinance': {
            'requests_per_second': 2,  # Conservative for stability
            'max_retries': 3,
            'backoff_factor': 1.5,
            'cache_ttl_minutes': 15,
            'timeout': 10,
        },
        'default': {
            'requests_per_second': 2,
            'max_retries': 3,
            'backoff_factor': 1.5,
            'cache_ttl_minutes': 10,
            'timeout': 10,
        }
    }
    
    @classmethod
    def get_config(cls, source: str) -> Dict[str, Any]:
        """Get configuration for a specific source"""
        return cls.CONFIGS.get(source, cls.CONFIGS['default'])
    
    @classmethod
    def register_source(cls, source: str, config: Dict[str, Any]):
        """Register a new source configuration"""
        cls.CONFIGS[source] = {**cls.CONFIGS['default'], **config}


# =============================================================================
# CIRCUIT BREAKER
# =============================================================================

class CircuitState(Enum):
    CLOSED = auto()    # Normal operation
    OPEN = auto()      # Failing, reject requests
    HALF_OPEN = auto() # Testing if service recovered


class CircuitBreaker:
    """
    Circuit Breaker pattern to prevent cascading failures.
    Opens after consecutive failures, allows recovery attempts.
    """
    
    def __init__(self, 
                 failure_threshold: int = 5, 
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._last_failure_time: Optional[float] = None
        self._lock = Lock()
    
    @property
    def state(self) -> CircuitState:
        with self._lock:
            if self._state == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if self._last_failure_time and \
                   time.time() - self._last_failure_time >= self.recovery_timeout:
                    self._state = CircuitState.HALF_OPEN
            return self._state
    
    def record_success(self):
        """Record a successful call"""
        with self._lock:
            self._failure_count = 0
            self._state = CircuitState.CLOSED
    
    def record_failure(self):
        """Record a failed call"""
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            
            if self._failure_count >= self.failure_threshold:
                self._state = CircuitState.OPEN
                logger.warning(f"Circuit breaker OPENED after {self._failure_count} failures")
    
    def can_execute(self) -> bool:
        """Check if a call can be made"""
        return self.state != CircuitState.OPEN
    
    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.can_execute():
                raise Exception("Circuit breaker is OPEN - service unavailable")
            
            try:
                result = func(*args, **kwargs)
                self.record_success()
                return result
            except self.expected_exception as e:
                self.record_failure()
                raise
        return wrapper


# =============================================================================
# TOKEN BUCKET RATE LIMITER
# =============================================================================

class TokenBucketRateLimiter:
    """
    Token Bucket algorithm for rate limiting.
    Thread-safe with proper lock handling.
    """
    
    def __init__(self, requests_per_second: float, max_tokens: int = 10):
        self.rps = requests_per_second
        self.max_tokens = max_tokens
        self._tokens = float(max_tokens)
        self._last_update = time.time()
        self._lock = RLock()  # Reentrant lock for nested calls
    
    @property
    def tokens(self) -> float:
        with self._lock:
            return self._tokens
    
    def _refill(self):
        """Refill tokens based on elapsed time (must be called with lock held)"""
        now = time.time()
        elapsed = now - self._last_update
        self._tokens = min(self.max_tokens, self._tokens + elapsed * self.rps)
        self._last_update = now
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens from the bucket.
        Returns True if acquired, False if timeout exceeded.
        """
        start_time = time.time()
        
        while True:
            with self._lock:
                self._refill()
                
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return True
            
            # Check timeout outside the lock
            if timeout is not None and (time.time() - start_time) >= timeout:
                return False
            
            # Calculate wait time (outside lock)
            wait_time = min(0.05, tokens / self.rps / 10)
            time.sleep(wait_time)
    
    def wait_if_needed(self, tokens: int = 1):
        """Block until tokens are available"""
        self.acquire(tokens, timeout=None)
    
    @contextmanager
    def rate_limit(self, tokens: int = 1):
        """Context manager for rate limiting"""
        self.wait_if_needed(tokens)
        yield


# =============================================================================
# DATA CACHE
# =============================================================================

class DataCache:
    """
    SQLite-based caching system for API responses.
    Thread-safe with connection-per-call pattern.
    """
    
    def __init__(self, db_path: str = 'data/stock_data_cache.db'):
        self.db_path = db_path
        self._init_lock = Lock()
        self._ensure_directory()
        self._init_database()
    
    def _ensure_directory(self):
        """Ensure the data directory exists"""
        import os
        dir_path = os.path.dirname(self.db_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a new database connection (thread-safe)"""
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_database(self):
        """Initialize cache database"""
        with self._init_lock:
            try:
                with self._get_connection() as conn:
                    conn.execute('''
                        CREATE TABLE IF NOT EXISTS api_cache (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            source TEXT NOT NULL,
                            query_key TEXT NOT NULL,
                            data TEXT NOT NULL,
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                            ttl_minutes INTEGER DEFAULT 15,
                            UNIQUE(source, query_key)
                        )
                    ''')
                    
                    conn.execute('''
                        CREATE INDEX IF NOT EXISTS idx_source_query 
                        ON api_cache(source, query_key)
                    ''')
                    
                    conn.execute('''
                        CREATE INDEX IF NOT EXISTS idx_timestamp 
                        ON api_cache(timestamp)
                    ''')
                    
                    conn.commit()
                    logger.info(f"Cache database initialized at {self.db_path}")
            except Exception as e:
                logger.error(f"Error initializing cache database: {e}")
    
    def get(self, source: str, query_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached data if still valid"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    '''SELECT data, timestamp, ttl_minutes 
                       FROM api_cache 
                       WHERE source = ? AND query_key = ?
                       ORDER BY timestamp DESC LIMIT 1
                    ''',
                    (source, query_key)
                )
                row = cursor.fetchone()
                
                if row:
                    data_json = row['data']
                    timestamp_str = row['timestamp']
                    ttl = row['ttl_minutes']
                    
                    timestamp = datetime.fromisoformat(timestamp_str)
                    age = datetime.now() - timestamp
                    
                    if age < timedelta(minutes=ttl):
                        logger.debug(f"Cache hit for {source}:{query_key}")
                        return json.loads(data_json)
                    else:
                        # Delete expired entry
                        conn.execute(
                            'DELETE FROM api_cache WHERE source = ? AND query_key = ?',
                            (source, query_key)
                        )
                        conn.commit()
                        logger.debug(f"Cache expired for {source}:{query_key}")
        except Exception as e:
            logger.error(f"Error retrieving cache: {e}")
        
        return None
    
    def set(self, source: str, query_key: str, data: Any, 
            ttl_minutes: int = 15) -> bool:
        """Cache API response"""
        try:
            # Handle non-JSON-serializable data
            if hasattr(data, 'to_dict'):
                data = data.to_dict()
            
            with self._get_connection() as conn:
                conn.execute(
                    '''INSERT OR REPLACE INTO api_cache 
                       (source, query_key, data, ttl_minutes, timestamp) 
                       VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''',
                    (source, query_key, json.dumps(data, default=str), ttl_minutes)
                )
                conn.commit()
                logger.debug(f"Cached {source}:{query_key} for {ttl_minutes} minutes")
                return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def clear_expired(self) -> int:
        """Clear expired cache entries, returns number deleted"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute('''
                    DELETE FROM api_cache 
                    WHERE datetime(timestamp, '+' || ttl_minutes || ' minutes') < datetime('now')
                ''')
                deleted = cursor.rowcount
                conn.commit()
                if deleted > 0:
                    logger.info(f"Cleared {deleted} expired cache entries")
                return deleted
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
    
    def clear_source(self, source: str) -> int:
        """Clear all cache entries for a specific source"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    'DELETE FROM api_cache WHERE source = ?', (source,)
                )
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Cleared {deleted} cache entries for {source}")
                return deleted
        except Exception as e:
            logger.error(f"Error clearing source cache: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute('SELECT COUNT(*) as total FROM api_cache')
                total = cursor.fetchone()['total']
                
                cursor = conn.execute('''
                    SELECT source, COUNT(*) as count 
                    FROM api_cache 
                    GROUP BY source
                ''')
                by_source = {row['source']: row['count'] for row in cursor.fetchall()}
                
                # Get cache hit rate estimate (entries accessed recently)
                cursor = conn.execute('''
                    SELECT COUNT(*) as recent FROM api_cache 
                    WHERE datetime(timestamp) > datetime('now', '-1 hour')
                ''')
                recent = cursor.fetchone()['recent']
                
                return {
                    'total_entries': total,
                    'by_source': by_source,
                    'recent_entries': recent,
                    'db_path': self.db_path
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}


# =============================================================================
# API CALL TRACKER
# =============================================================================

class APICallTracker:
    """
    Tracks API calls to monitor usage patterns.
    Thread-safe with efficient deque operations.
    """
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self._calls = deque(maxlen=max_history)
        self._lock = Lock()
        
        # Quick counters for common stats
        self._success_count = 0
        self._failure_count = 0
        self._rate_limit_count = 0
        self._cache_hit_count = 0
    
    def record(self, source: str, endpoint: str, status: str, 
               response_time: float = 0.0, error: Optional[str] = None):
        """Record an API call"""
        with self._lock:
            self._calls.append({
                'timestamp': datetime.now().isoformat(),
                'source': source,
                'endpoint': endpoint,
                'status': status,
                'response_time': response_time,
                'error': error
            })
            
            # Update quick counters
            if status == 'success':
                self._success_count += 1
            elif status == 'cache_hit':
                self._cache_hit_count += 1
            elif 'rate' in status.lower():
                self._rate_limit_count += 1
            else:
                self._failure_count += 1
    
    def get_stats(self, source: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics for API calls"""
        with self._lock:
            if source:
                calls = [c for c in self._calls if c['source'] == source]
            else:
                calls = list(self._calls)
        
        if not calls:
            return {
                'total_calls': 0,
                'success': 0,
                'failed': 0,
                'rate_limited': 0,
                'cache_hits': 0,
                'avg_response_time': 0,
                'success_rate': 0
            }
        
        total = len(calls)
        success = sum(1 for c in calls if c['status'] == 'success')
        cache_hits = sum(1 for c in calls if c['status'] == 'cache_hit')
        rate_limited = sum(1 for c in calls if 'rate' in str(c.get('status', '')).lower())
        
        response_times = [c['response_time'] for c in calls if c['response_time'] > 0]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            'total_calls': total,
            'success': success,
            'failed': total - success - cache_hits,
            'rate_limited': rate_limited,
            'cache_hits': cache_hits,
            'avg_response_time': round(avg_response_time, 3),
            'success_rate': round((success + cache_hits) / total * 100, 1) if total > 0 else 0
        }
    
    def get_recent_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors"""
        with self._lock:
            errors = [c for c in self._calls if c.get('error')]
            return list(errors)[-limit:]


# =============================================================================
# MAIN API CLIENT
# =============================================================================

class RateLimitedAPIClient:
    """
    Main API client with rate limiting, caching, retry logic, and circuit breaker.
    Uses singleton pattern for efficiency.
    """
    
    # Singleton registry
    _clients: Dict[str, 'RateLimitedAPIClient'] = {}
    _registry_lock = Lock()
    
    # Shared resources
    _shared_cache: Optional[DataCache] = None
    _shared_tracker: Optional[APICallTracker] = None
    
    def __init__(self, source: str, db_path: str = 'data/stock_data_cache.db'):
        self.source = source
        config = RateLimitConfig.get_config(source)
        
        self.limiter = TokenBucketRateLimiter(
            config['requests_per_second'],
            max_tokens=max(10, int(config['requests_per_second'] * 10))
        )
        
        # Use shared cache and tracker
        if RateLimitedAPIClient._shared_cache is None:
            RateLimitedAPIClient._shared_cache = DataCache(db_path)
        if RateLimitedAPIClient._shared_tracker is None:
            RateLimitedAPIClient._shared_tracker = APICallTracker()
        
        self.cache = RateLimitedAPIClient._shared_cache
        self.tracker = RateLimitedAPIClient._shared_tracker
        
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=config['max_retries'] + 2,
            recovery_timeout=60
        )
        
        self.max_retries = config['max_retries']
        self.backoff_factor = config['backoff_factor']
        self.cache_ttl = config['cache_ttl_minutes']
        self.timeout = config['timeout']
    
    @classmethod
    def get_client(cls, source: str, db_path: str = 'data/stock_data_cache.db') -> 'RateLimitedAPIClient':
        """Get or create a client instance (singleton pattern)"""
        with cls._registry_lock:
            if source not in cls._clients:
                cls._clients[source] = cls(source, db_path)
            return cls._clients[source]
    
    @classmethod
    def reset_clients(cls):
        """Reset all client instances (mainly for testing)"""
        with cls._registry_lock:
            cls._clients.clear()
            cls._shared_cache = None
            cls._shared_tracker = None
    
    def call_with_cache_and_limit(
        self,
        func: Callable,
        query_key: str,
        *args,
        use_cache: bool = True,
        ttl_override: Optional[int] = None,
        **kwargs
    ) -> Tuple[Optional[Any], bool]:
        """
        Execute API call with caching and rate limiting.
        Returns (data, success) tuple.
        """
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            logger.warning(f"⚡ {self.source}: Circuit breaker OPEN, rejecting request")
            self.tracker.record(self.source, query_key, 'circuit_open')
            return None, False
        
        # Try cache first
        if use_cache:
            cached_data = self.cache.get(self.source, query_key)
            if cached_data is not None:
                self.tracker.record(self.source, query_key, 'cache_hit', 0)
                return cached_data, True
        
        # Apply rate limiting
        self.limiter.wait_if_needed()
        
        # Retry logic with exponential backoff
        last_error = None
        ttl = ttl_override or self.cache_ttl
        
        for attempt in range(self.max_retries):
            try:
                api_start = time.time()
                result = func(*args, **kwargs)
                response_time = time.time() - api_start
                
                # Record success
                self.circuit_breaker.record_success()
                self.tracker.record(self.source, query_key, 'success', response_time)
                
                # Cache successful result
                if use_cache and result is not None:
                    self.cache.set(self.source, query_key, result, ttl)
                
                logger.info(f"✓ {self.source}: {query_key} (attempt {attempt + 1}, {response_time:.2f}s)")
                return result, True
            
            except Exception as e:
                last_error = str(e)
                error_lower = last_error.lower()
                
                # Check for rate limit error
                is_rate_limit = any(x in error_lower for x in [
                    'rate limit', '429', 'too many requests', 'quota', 'exceeded'
                ])
                
                if is_rate_limit:
                    self.tracker.record(
                        self.source, query_key, 'rate_limited', error=last_error
                    )
                    
                    if attempt < self.max_retries - 1:
                        # Exponential backoff with jitter
                        wait_time = (self.backoff_factor ** attempt) * (1 + random.uniform(0, 0.2))
                        logger.warning(
                            f"⚠ {self.source}: Rate limited. "
                            f"Retry {attempt + 1}/{self.max_retries} in {wait_time:.1f}s"
                        )
                        time.sleep(wait_time)
                    continue
                else:
                    self.circuit_breaker.record_failure()
                    self.tracker.record(
                        self.source, query_key, 'error', error=last_error
                    )
                    logger.error(f"✗ {self.source}: {query_key} - {last_error}")
                    return None, False
        
        # All retries exhausted
        self.circuit_breaker.record_failure()
        logger.error(
            f"✗ {self.source}: {query_key} failed after {self.max_retries} retries. "
            f"Last error: {last_error}"
        )
        return None, False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        return {
            'source': self.source,
            'api_stats': self.tracker.get_stats(self.source),
            'cache_stats': self.cache.get_stats(),
            'circuit_breaker': {
                'state': self.circuit_breaker.state.name,
                'failure_count': self.circuit_breaker._failure_count
            },
            'rate_limiter': {
                'rps': self.limiter.rps,
                'current_tokens': round(self.limiter.tokens, 2),
                'max_tokens': self.limiter.max_tokens
            }
        }


# =============================================================================
# DECORATOR
# =============================================================================

def rate_limited_api_call(source: str, use_cache: bool = True, ttl_minutes: Optional[int] = None):
    """
    Decorator for API calls with automatic rate limiting.
    
    Usage:
        @rate_limited_api_call('finnhub')
        def get_stock_data(ticker):
            return finnhub_client.quote(ticker)
    """
    def decorator(func: Callable) -> Callable:
        client = RateLimitedAPIClient.get_client(source)
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique query key from function name and arguments
            args_str = '_'.join(str(a) for a in args)
            kwargs_str = '_'.join(f"{k}={v}" for k, v in sorted(kwargs.items()))
            query_key = f"{func.__name__}_{args_str}_{kwargs_str}".replace(' ', '_')
            
            result, success = client.call_with_cache_and_limit(
                func,
                query_key,
                *args,
                use_cache=use_cache,
                ttl_override=ttl_minutes,
                **kwargs
            )
            
            if not success:
                return None
            return result
        
        return wrapper
    return decorator


# =============================================================================
# MULTI-SOURCE DATA FETCHER
# =============================================================================

class MultiSourceDataFetcher:
    """
    Fetches data from multiple sources with intelligent fallback.
    Automatically switches to alternative sources when primary fails.
    """
    
    def __init__(self):
        self.sources = {
            'stock': ['finnhub', 'yfinance', 'alpha_vantage', 'iex_cloud'],
            'crypto': ['coingecko', 'alpha_vantage'],
            'forex': ['yfinance', 'alpha_vantage'],
            'economic': ['fred', 'world_bank']
        }
        self._clients: Dict[str, RateLimitedAPIClient] = {}
    
    def get_client(self, source: str) -> RateLimitedAPIClient:
        """Get or create client for source"""
        if source not in self._clients:
            self._clients[source] = RateLimitedAPIClient.get_client(source)
        return self._clients[source]
    
    def fetch_with_fallback(
        self, 
        data_type: str,
        fetch_funcs: Dict[str, Callable],
        query_key: str,
        preferred_source: Optional[str] = None
    ) -> Tuple[Optional[Any], Optional[str]]:
        """
        Fetch data with automatic fallback between sources.
        Returns (data, source_used) tuple.
        """
        sources_to_try = self.sources.get(data_type, ['default'])
        
        # Move preferred source to front
        if preferred_source and preferred_source in sources_to_try:
            sources_to_try = [preferred_source] + [s for s in sources_to_try if s != preferred_source]
        
        for source in sources_to_try:
            if source not in fetch_funcs:
                continue
                
            try:
                client = self.get_client(source)
                result, success = client.call_with_cache_and_limit(
                    fetch_funcs[source],
                    f"{query_key}_{source}",
                    use_cache=True
                )
                
                if success and result:
                    return result, source
                    
            except Exception as e:
                logger.warning(f"Failed to fetch from {source}: {e}")
                continue
        
        logger.error(f"All sources exhausted for {query_key}")
        return None, None
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get statistics from all clients"""
        return {
            source: client.get_stats()
            for source, client in self._clients.items()
        }


# =============================================================================
# API MONITOR
# =============================================================================

class APIMonitor:
    """Monitor API usage and performance across all sources"""
    
    def __init__(self, sources: Optional[List[str]] = None):
        if sources is None:
            sources = ['finnhub', 'yfinance', 'alpha_vantage']
        
        self.sources = sources
        self._clients = {
            source: RateLimitedAPIClient.get_client(source) 
            for source in sources
        }
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all sources"""
        stats = {}
        for source, client in self._clients.items():
            stats[source] = client.get_stats()
        return stats
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all sources"""
        status = {}
        for source, client in self._clients.items():
            circuit_state = client.circuit_breaker.state
            api_stats = client.tracker.get_stats(source)
            
            status[source] = {
                'healthy': circuit_state == CircuitState.CLOSED,
                'circuit_state': circuit_state.name,
                'success_rate': api_stats.get('success_rate', 0),
                'recent_errors': client.tracker.get_recent_errors(3)
            }
        return status
    
    def print_stats(self):
        """Print formatted statistics to console"""
        print("\n" + "=" * 80)
        print("📊 API USAGE STATISTICS")
        print("=" * 80)
        
        all_stats = self.get_all_stats()
        
        for source, stats in all_stats.items():
            api_s = stats.get('api_stats', {})
            cache_s = stats.get('cache_stats', {})
            cb_s = stats.get('circuit_breaker', {})
            rl_s = stats.get('rate_limiter', {})
            
            print(f"\n🔹 {source.upper()}")
            print("-" * 40)
            print(f"   Calls: {api_s.get('total_calls', 0)} | "
                  f"Success Rate: {api_s.get('success_rate', 0)}%")
            print(f"   Cache Hits: {api_s.get('cache_hits', 0)} | "
                  f"Rate Limited: {api_s.get('rate_limited', 0)}")
            print(f"   Circuit: {cb_s.get('state', 'UNKNOWN')} | "
                  f"Tokens: {rl_s.get('current_tokens', 0)}/{rl_s.get('max_tokens', 0)}")
        
        # Cache summary
        if all_stats:
            first_source = list(all_stats.values())[0]
            cache_stats = first_source.get('cache_stats', {})
            print(f"\n📦 CACHE: {cache_stats.get('total_entries', 0)} entries")
        
        print("\n" + "=" * 80)
    
    def export_stats(self, filename: str = 'api_stats.json'):
        """Export statistics to JSON file"""
        stats = self.get_all_stats()
        with open(filename, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        logger.info(f"Stats exported to {filename}")


# =============================================================================
# FASTAPI INTEGRATION
# =============================================================================

def get_rate_limiter_dependency(source: str = 'default'):
    """
    FastAPI dependency for rate-limited client.
    
    Usage:
        @app.get("/stock/{ticker}")
        async def get_stock(ticker: str, client = Depends(get_rate_limiter_dependency('finnhub'))):
            ...
    """
    def dependency():
        return RateLimitedAPIClient.get_client(source)
    return dependency


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("=" * 60)
    print("Rate Limiter System v2.0 - Initialized")
    print("=" * 60)
    
    # Create clients for different sources
    finnhub_client = RateLimitedAPIClient.get_client('finnhub')
    yfinance_client = RateLimitedAPIClient.get_client('yfinance')
    
    print(f"\n📋 Finnhub Config: {RateLimitConfig.get_config('finnhub')}")
    print(f"📋 YFinance Config: {RateLimitConfig.get_config('yfinance')}")
    
    # Clear expired cache
    cache = finnhub_client.cache
    cache.clear_expired()
    
    # Show stats
    monitor = APIMonitor(['finnhub', 'yfinance', 'alpha_vantage'])
    monitor.print_stats()
    
    print("\n✅ Rate limiter ready for use!")
    print("   Import with: from rate_limiter import RateLimitedAPIClient, rate_limited_api_call")
