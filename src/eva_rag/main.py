"""FastAPI application entry point for eva-rag."""
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from eva_rag.config import settings
from eva_rag.api import ingest


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application lifecycle (startup/shutdown)."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    print(f"📍 API available at http://{settings.api_host}:{settings.api_port}{settings.api_prefix}")
    
    yield
    
    # Shutdown
    print(f"🛑 Shutting down {settings.app_name}")


app = FastAPI(
    title="EVA RAG Engine",
    description="""
    ## EVA RAG Document Processing Engine
    
    Intelligent document ingestion pipeline with:
    - **Multi-format support**: PDF, DOCX, TXT
    - **Language detection**: English/French with automatic detection
    - **Semantic chunking**: Intelligent text segmentation
    - **Embeddings**: Azure OpenAI integration
    - **Multi-tenancy**: Tenant and space isolation
    - **Azure-native**: Blob Storage + Cosmos DB + AI Search ready
    
    ### Features
    - 📄 Document upload and processing
    - 🧠 Automatic language detection
    - ✂️ Smart text chunking
    - 🔢 Vector embeddings generation
    - 📊 Metadata tracking
    - 🔍 Ready for semantic search
    
    ### Quick Start
    1. Upload a document via `/api/v1/rag/ingest`
    2. System extracts text, detects language, chunks content
    3. Generates embeddings and stores in Azure
    4. Returns document metadata with processing status
    """,
    version=settings.app_version,
    docs_url=f"{settings.api_prefix}/docs",
    openapi_url=f"{settings.api_prefix}/openapi.json",
    redoc_url=f"{settings.api_prefix}/redoc",
    lifespan=lifespan,
    contact={
        "name": "EVA RAG Team",
        "url": "https://github.com/MarcoPolo483/eva-rag",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"{settings.api_prefix}/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# Register routers
app.include_router(ingest.router, prefix=settings.api_prefix)
