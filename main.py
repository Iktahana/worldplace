import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from starlette.responses import JSONResponse

from src import place, api
from src.api import block
from src.db.mongodb import connect_to_mongodb, close_mongodb_connection

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongodb()
    yield
    await close_mongodb_connection()

DEFAULT_ORIGINS = [
    "http://localhost:63342",
    "http://127.0.0.1:63342",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",   # 若用同源也無妨
]

env_origins = os.getenv("CORS_ALLOW_ORIGINS")
ALLOW_ORIGINS = [o.strip() for o in env_origins.split(",")] if env_origins else DEFAULT_ORIGINS

app = FastAPI(
    redoc_url="/docs",
    title="Place API",
    description="API for managing geographic blocks",
    lifespan=lifespan,
)

# ★ 一律啟用 CORS（不要綁 app.debug）
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,   # 上線請填精確域名；開發可暫時用 ["*"]
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=86400,
)

@app.get("/")
async def root_index():
    return {"message": "Hello World"}

@app.get("/config", response_class=PlainTextResponse)
async def get_googlemap_key():
    return JSONResponse({
        # "GOOGLEMAP_APIKEY": os.environ.get("GOOGLEMAP_APIKEY"),
        "STEP": place.__STEP__,
        "SCALE": place.__SCALE__,
        "allowed_colors": api.__ALLOWED_COLORS__,
    })


app.include_router(block.router)
