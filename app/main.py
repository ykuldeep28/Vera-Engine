from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import init_db
from app.routes import health, context, tick, reply

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite database schema on startup
    init_db()
    yield

app = FastAPI(
    title="Vera Engine",
    version="1.2.0",
    description="Rule Engine & Deterministic Scoring for Vera Assistant",
    lifespan=lifespan
)

app.include_router(health.router)
app.include_router(context.router)
app.include_router(tick.router)
app.include_router(reply.router)
