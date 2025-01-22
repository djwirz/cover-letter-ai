from typing import Annotated
from fastapi import Depends
from app.services.database import Database
from app.services.vector_store import VectorService
from app.services.ai_service import EnhancedAIService
from app.agents.skills_analysis import SkillsAnalysisAgent
from app.agents.requirements_analysis import RequirementsAnalysisAgent
from app.agents.strategy_analysis import CoverLetterStrategyAgent
from app.agents.generation_analysis import CoverLetterGenerationAgent
from app.settings.config import Settings

async def get_db():
    """Dependency for database connection."""
    db = Database()
    try:
        yield db
    finally:
        await db.close()

async def get_vector_service(
    db: Annotated[Database, Depends(get_db)]
) -> VectorService:
    """Dependency for vector store service."""
    return VectorService(db.client)

async def get_ai_service(
    vector_service: Annotated[VectorService, Depends(get_vector_service)]
) -> EnhancedAIService:
    """Dependency for AI service."""
    return EnhancedAIService(vector_service)

async def get_skills_agent() -> SkillsAnalysisAgent:
    """Dependency for skills analysis agent."""
    return SkillsAnalysisAgent()

async def get_requirements_agent() -> RequirementsAnalysisAgent:
    """Dependency for requirements analysis agent."""
    return RequirementsAnalysisAgent()

async def get_strategy_agent(
    vector_service: Annotated[VectorService, Depends(get_vector_service)]
) -> CoverLetterStrategyAgent:
    """Dependency for strategy analysis agent."""
    return CoverLetterStrategyAgent(vector_store=vector_service)

async def get_generation_agent() -> CoverLetterGenerationAgent:
    """Dependency for generation agent."""
    return CoverLetterGenerationAgent()