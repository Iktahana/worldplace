from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import block
from src.db.mongodb import connect_to_mongodb, close_mongodb_connection


# 假設這是你現有的連線函數
async def _connect_to_mongodb():
    print("✅ Connected to MongoDB")


async def _close_mongodb_connection():
    print("❌ Closed MongoDB connection")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb_connection()


app = FastAPI(
    redoc_url="/docs",
    title="Place API",
    description="API for managing geographic blocks",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(block.router)
