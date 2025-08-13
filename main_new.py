import logging
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from app.core.config import settings
from app.core.database import create_tables
from app.routers import auth, trading, prices, websocket
from app.services.price_service import price_service
from app.services.websocket_service import websocket_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Trading Simulator...")
    
    create_tables()
    logger.info("Database tables created")
    
    await price_service.start_price_updates()
    await websocket_manager.start_price_broadcast()
    logger.info("Background services started")
    
    yield
    
    logger.info("Shutting down Trading Simulator...")
    await price_service.stop_price_updates()
    await websocket_manager.stop_price_broadcast()
    logger.info("Background services stopped")

app = FastAPI(
    title=settings.project_name,
    version="2.0.0",
    description="Professional Trading Simulator with Real-time Price Updates",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

app.include_router(auth.router, prefix=settings.api_v1_str)
app.include_router(trading.router, prefix=settings.api_v1_str)
app.include_router(prices.router, prefix=settings.api_v1_str)
app.include_router(websocket.router)

@app.get("/")
async def root():
    return {
        "message": "Trading Simulator API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "price_service": "running",
        "websocket_connections": len(websocket_manager.active_connections)
    }

if __name__ == "__main__":
    logger.info("Starting server...")
    uvicorn.run(
        "main_new:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
