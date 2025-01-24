from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.settings.config import settings
from app.services.database import Database
from app.services.vector_service import VectorService
from app.services.ai_service import ConcreteAIService
from app.agents.utils.logging import setup_logger

logger = setup_logger("Main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting application")
    
    # Initialize services
    database = Database()
    vector_service = VectorService()
    ai_service = ConcreteAIService(vector_service)
    
    try:
        await database.initialize()
        await vector_service.initialize()
        await ai_service.initialize()
        
        # Add services to app state
        app.state.db = database
        app.state.vector_service = vector_service
        app.state.ai_service = ai_service
        
        logger.info("Services initialized")
        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {str(e)}")
        raise
    finally:
        logger.info("Shutting down application")
        await ai_service.close()
        await vector_service.close()
        await database.close()

app = FastAPI(
    title="Cover Letter AI",
    description="AI-powered cover letter generation system",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}