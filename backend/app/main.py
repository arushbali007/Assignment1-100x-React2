from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api import auth, sources, content, trends, style_profiles, drafts, newsletter_sends
from app.services.scheduler_service import scheduler_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    # Startup
    scheduler_service.start()
    yield
    # Shutdown
    scheduler_service.stop()


app = FastAPI(
    title="CreatorPulse API",
    description="Backend API for CreatorPulse - Newsletter Curator",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(sources.router)
app.include_router(content.router)
app.include_router(trends.router)
app.include_router(style_profiles.router)
app.include_router(drafts.router)
app.include_router(newsletter_sends.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to CreatorPulse API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
