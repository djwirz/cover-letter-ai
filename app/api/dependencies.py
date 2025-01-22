from typing import Annotated, AsyncGenerator
from fastapi import Depends, Request
from app.services.database import Database
from app.services.vector_service import VectorService
from app.services.ai_service import EnhancedAIService
from app.agents.skills_analysis import SkillsAnalysisAgent
from app.agents.requirements_analysis import RequirementsAnalysisAgent
from app.agents.strategy_analysis import CoverLetterStrategyAgent
from app.agents.generation_analysis import CoverLetterGenerationAgent
from app.settings.config import Settings
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    async for session in request.app.state.db.get_session():
        yield session

async def get_vector_service(request: Request) -> VectorService:
    return request.app.state.vector_service

async def get_ai_service(request: Request) -> EnhancedAIService:
    return request.app.state.ai_service

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