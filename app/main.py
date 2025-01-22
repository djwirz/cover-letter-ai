from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.routes import router
from app.settings.config import Settings
from app.services.database import Database
from app.services.vector_service import VectorService
from app.services.ai_service import EnhancedAIService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize services
    settings = Settings()
    
    # Database initialization
    database = Database(settings)
    await database.initialize()
    
    # Vector service initialization
    vector_service = VectorService(settings)
    await vector_service.initialize()
    
    # AI service initialization
    ai_service = EnhancedAIService(settings, vector_service)
    
    # Add services to app state
    app.state.db = database
    app.state.vector_service = vector_service
    app.state.ai_service = ai_service
    
    yield
    
    # Cleanup
    await database.close()
    await vector_service.close()
    await ai_service.close()

app = FastAPI(
    title="Cover Letter AI",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="")