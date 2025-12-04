from app.api.v1.endpoints import websocket, stocks, stats

api_router = APIRouter()
api_router.include_router(websocket.router, prefix="/ws", tags=["websockets"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])

