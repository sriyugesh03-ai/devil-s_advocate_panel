from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from backend.app.core.config import settings
from backend.app.db.mongo import connect_to_mongo, close_mongo_connection

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("devils_advocate")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} on port {settings.PORT}")
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Stateful multi-agent system to stress-test startup pitches with AI investor personas.",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "port": settings.PORT,
        "llm_provider": settings.DEFAULT_LLM_PROVIDER
    }

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Devil's Advocate Panel API. Pitch your idea and face the gauntlet.",
        "docs_url": "/docs",
        "health_url": "/health"
    }
