from datetime import datetime, UTC
from typing import Annotated
from fastapi import APIRouter, HTTPException, Depends
from app.services.ai_service import EnhancedAIService
from app.services.vector_store import VectorService
from app.agents.skills_analysis import SkillsAnalysisAgent
from app.agents.requirements_analysis import RequirementsAnalysisAgent
from app.agents.strategy_analysis import CoverLetterStrategyAgent
from app.agents.generation_analysis import CoverLetterGenerationAgent
from app.models.schemas import (
    DocumentRequest,
    DocumentType,
    GenerationRequest,
    GenerationResponse,
    AnalyzeSkillsRequest,
    AnalyzeRequirementsRequest,
    AnalyzeStrategyRequest,
    GenerateCoverLetterRequest,
    RefineCoverLetterRequest
)
from app.api.dependencies import (
    get_vector_service,
    get_ai_service,
    get_skills_agent,
    get_requirements_agent,
    get_strategy_agent,
    get_generation_agent
)

# Create router without prefix (it will be added in main.py)
router = APIRouter()

@router.post("/api/documents", response_model=dict)
async def process_document(
    request: DocumentRequest,
    vector_service: Annotated[VectorService, Depends(get_vector_service)]
):
    """Process and store a document in the vector database."""
    try:
        doc_id = await vector_service.process_document(
            request.content,
            request.doc_type,
            request.metadata
        )
        return {"id": doc_id, "status": "processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/analyze/skills")
async def analyze_skills(
    request: AnalyzeSkillsRequest,
    skills_agent: Annotated[SkillsAnalysisAgent, Depends(get_skills_agent)]
):
    """Analyze skills from a resume or other document."""
    try:
        analysis = await skills_agent.analyze(request.content)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/analyze/requirements")
async def analyze_requirements(
    request: AnalyzeRequirementsRequest,
    requirements_agent: Annotated[RequirementsAnalysisAgent, Depends(get_requirements_agent)]
):
    """Analyze requirements from a job description."""
    try:
        analysis = await requirements_agent.analyze(request.job_description)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/analyze/strategy")
async def analyze_strategy(
    request: AnalyzeStrategyRequest,
    skills_agent: Annotated[SkillsAnalysisAgent, Depends(get_skills_agent)],
    requirements_agent: Annotated[RequirementsAnalysisAgent, Depends(get_requirements_agent)],
    strategy_agent: Annotated[CoverLetterStrategyAgent, Depends(get_strategy_agent)]
):
    """Generate a cover letter strategy based on skills and requirements analysis."""
    try:
        skills_analysis = await skills_agent.analyze(request.resume_content)
        requirements_analysis = await requirements_agent.analyze(request.job_description)
        strategy = await strategy_agent.develop_strategy(
            skills_analysis,
            requirements_analysis
        )
        return strategy
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate", response_model=GenerationResponse)
async def generate_cover_letter(
    request: GenerationRequest,
    vector_service: Annotated[VectorService, Depends(get_vector_service)],
    ai_service: Annotated[EnhancedAIService, Depends(get_ai_service)]
):
    """Generate a cover letter using context from similar documents."""
    try:
        # Get relevant context
        resume_context = await vector_service.get_relevant_context(
            request.job_description,
            doc_type=DocumentType.RESUME,
            limit=3
        )
        job_context = await vector_service.get_relevant_context(
            request.job_description,
            doc_type=DocumentType.JOB_DESCRIPTION,
            limit=2
        )

        # Generate letter
        content = await ai_service.generate_cover_letter(
            job_description=request.job_description,
            context_documents=resume_context + job_context,
            preferences=request.preferences
        )

        # Process metadata
        similar_docs = [
            doc['metadata'] for doc, _ in (resume_context + job_context)
            if isinstance(doc, dict) and 'metadata' in doc
        ]

        return GenerationResponse(
            content=content,
            metadata={"timestamp": datetime.now(UTC).isoformat()},
            similar_documents=similar_docs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/generate/cover-letter")
async def generate_cover_letter_content(
    request: GenerateCoverLetterRequest,
    generation_agent: Annotated[CoverLetterGenerationAgent, Depends(get_generation_agent)]
):
    """Generate a cover letter using the generation analysis agent."""
    try:
        cover_letter = await generation_agent.generate(
            request.skills_analysis,
            request.requirements_analysis,
            request.strategy,
            request.preferences
        )
        return cover_letter
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/refine/cover-letter")
async def refine_cover_letter(
    request: RefineCoverLetterRequest,
    generation_agent: Annotated[CoverLetterGenerationAgent, Depends(get_generation_agent)]
):
    """Refine an existing cover letter based on feedback."""
    try:
        refined_letter = await generation_agent.refine_letter(
            request.cover_letter,
            request.feedback
        )
        return refined_letter
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))