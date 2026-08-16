import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import analytics, auth, complaints, websockets
from app.services.websocket_manager import ws_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start background Redis pub/sub listener for live WebSocket updates
    # (init_db() is omitted here to prevent multi-worker DDL sequence collisions)
    redis_task = asyncio.create_task(ws_manager.listen_to_redis())
    yield
    # Shutdown: Cancel and await background task cleanup
    redis_task.cancel()
    try:
        await redis_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="AI Smart Campus Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correct prefixes for all API v1 endpoints
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(complaints.router, prefix="/api/v1", tags=["Complaints"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])
app.include_router(websockets.router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "online", "system": "AI Smart Campus Core"}