from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import settings
import redis.asyncio as redis
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/quotes")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    r = redis.from_url(settings.REDIS_URL)
    pubsub = r.pubsub()
    await pubsub.subscribe("stock_updates")

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message["data"].decode("utf-8"))
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await pubsub.unsubscribe("stock_updates")
        await r.close()
