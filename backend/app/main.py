from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from backend.app.core.config import settings
from backend.app.core.langsmith import setup_langsmith_tracing
from backend.app.db.mongo import connect_to_mongo, close_mongo_connection
from backend.app.rag.service import rag_service
from backend.app.api.pitches import router as pitches_router
from backend.app.api.sessions import router as sessions_router
from backend.app.api.verdict import router as verdict_router
from backend.app.api.pdf import router as pdf_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("devils_advocate")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} on port {settings.PORT}")
    setup_langsmith_tracing()
    await connect_to_mongo()
    # Pre-index domain knowledge if not already indexed
    try:
        await rag_service.initialize_and_index()
    except Exception as e:
        logger.warning(f"Background RAG initialization warning: {e}")
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

# Register API Routers
app.include_router(pitches_router, prefix="/api")
app.include_router(sessions_router, prefix="/api")
app.include_router(verdict_router, prefix="/api")
app.include_router(pdf_router, prefix="/api")

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
