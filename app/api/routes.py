from datetime import datetime, UTC
from typing import Annotated, Dict
from fastapi import APIRouter, HTTPException, Depends
from app.agents import requirements_analysis
from app.services.ai_service import EnhancedAIService, ConcreteAIService
from app.services.vector_store import VectorService
from app.agents.skills_analysis import SkillsAnalysisAgent
from app.agents.requirements_analysis import RequirementsAnalysisAgent
from app.agents.strategy_analysis import CoverLetterStrategyAgent
from app.agents.generation_analysis import CoverLetterGenerationAgent
from app.agents.ats_scanner import ATSScannerAgent
from app.agents.content_validation import ContentValidationAgent
from app.agents.technical_term import TechnicalTermAgent
from app.models.schemas import (
    DocumentRequest, DocumentType, GenerationRequest, GenerationResponse,
    AnalyzeSkillsRequest, AnalyzeRequirementsRequest, AnalyzeStrategyRequest,
    GenerateCoverLetterRequest, RefineCoverLetterRequest, ATSAnalysisRequest,
    ContentValidationRequest, TechnicalTermRequest
)
from app.api.dependencies import (
    get_vector_service, get_ai_service, get_skills_agent,
    get_requirements_agent, get_strategy_agent, get_generation_agent,
    get_ats_scanner_agent, get_content_validation_agent, get_technical_term_agent
)
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/api/documents", response_model=dict)
async def process_document(
    content: str,
    doc_type: str,
    metadata: Dict[str, str],
    ai_service: ConcreteAIService = Depends(get_ai_service)
):
    logger.info("Processing document...")
    result = await ai_service.vector_service.process_document(content, doc_type, metadata)
    logger.info("Document processed with result: %s", result)
    return result

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
    ai_service: Annotated[EnhancedAIService, Depends(get_ai_service)],
    ats_scanner_agent: Annotated[ATSScannerAgent, Depends(get_ats_scanner_agent)],
    content_validation_agent: Annotated[ContentValidationAgent, Depends(get_content_validation_agent)],
    technical_term_agent: Annotated[TechnicalTermAgent, Depends(get_technical_term_agent)],
    requirements_agent: Annotated[RequirementsAnalysisAgent, Depends(get_requirements_agent)]
):
    """Generate a cover letter using context from similar documents."""
    try:
        # Log the incoming request
        print(f"Incoming request: {request.model_dump()}")

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

        # Log the retrieved context
        print(f"Resume context: {resume_context}")
        print(f"Job context: {job_context}")

        # Generate initial cover letter
        content = await ai_service.generate_cover_letter(
            job_description=request.job_description,
            context_documents=resume_context + job_context,
            preferences=request.preferences
        )

        # Log the generated content
        print(f"Generated cover letter content: {content}")

        # Validate cover letter content
        if not content:
            raise HTTPException(status_code=400, detail="Failed to generate cover letter content")

        # ATS Scanning
        requirements_analysis = await requirements_agent.analyze(request.job_description)
        print(f"Requirements analysis: {requirements_analysis}")

        # Debug: Log the inputs to the ATS scanner
        print(f"Input to ATS scanner - Cover Letter: {content}")
        print(f"Input to ATS scanner - Job Description: {request.job_description}")
        print(f"Input to ATS scanner - Requirements Analysis: {requirements_analysis}")

        # Ensure the cover letter content is passed correctly to the ATS scanner
        ats_analysis = await ats_scanner_agent.scan_letter(
            cover_letter=content,  # Pass the generated content directly
            job_description=request.job_description,
            requirements_analysis=requirements_analysis
        )
        print(f"ATS analysis result: {ats_analysis}")

        ats_suggestions = await ats_scanner_agent.suggest_improvements(ats_analysis)
        print(f"ATS suggestions: {ats_suggestions}")

        # Apply ATS suggestions to content
        for suggestion in ats_suggestions:
            # Apply suggestion logic here
            pass

        # Content Validation
        validation_result = await content_validation_agent.validate_content(
            content,
            request.resume_content,  # Use the resume_content field from the request
            request.job_description
        )
        print(f"Content validation result: {validation_result}")

        validation_suggestions = await content_validation_agent.suggest_improvements(validation_result)
        print(f"Validation suggestions: {validation_suggestions}")

        # Apply validation suggestions to content
        for suggestion in validation_suggestions:
            # Apply suggestion logic here
            pass

        # Technical Term Standardization
        term_alignment = await technical_term_agent.standardize_terms(
            request.job_description,
            content
        )
        print(f"Term alignment result: {term_alignment}")

        term_suggestions = await technical_term_agent.suggest_term_updates(term_alignment)
        print(f"Term suggestions: {term_suggestions}")

        # Apply term suggestions to content
        for suggestion in term_suggestions:
            # Apply suggestion logic here
            pass

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
        print(f"Error in generate_cover_letter: {str(e)}")
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

@router.post("/api/analyze/ats")
async def analyze_ats(
    request: ATSAnalysisRequest,
    ats_scanner_agent: Annotated[ATSScannerAgent, Depends(get_ats_scanner_agent)]
):
    """Analyze cover letter for ATS compatibility."""
    try:
        # Add debug logging
        print(f"Processing ATS analysis request: {request.model_dump()}")
        
        result = await ats_scanner_agent.scan_letter(
            request.cover_letter,
            request.job_description,
            request.requirements_analysis
        )
        
        # Add debug logging
        print(f"ATS analysis result: {result}")
        return result
        
    except Exception as e:
        print(f"Error in analyze_ats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/validate/content")
async def validate_content(
    request: ContentValidationRequest,
    content_validator: Annotated[ContentValidationAgent, Depends(get_content_validation_agent)]
):
    """Validate cover letter content."""
    try:
        # Add debug logging
        print(f"Processing content validation request: {request.model_dump()}")
        
        validation_result = await content_validator.validate_content(
            request.cover_letter,
            request.resume,
            request.job_description
        )
        
        # Add debug logging
        print(f"Content validation result: {validation_result}")
        return validation_result
        
    except Exception as e:
        print(f"Error in validate_content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/standardize/terms")
async def standardize_terms(
    request: TechnicalTermRequest,
    technical_term_agent: Annotated[TechnicalTermAgent, Depends(get_technical_term_agent)]
):
    """Standardize technical terms in the cover letter."""
    try:
        # Add debug logging
        print(f"Processing request: {request.model_dump()}")
        
        # Validate input
        if not request.job_description or not request.cover_letter:
            raise HTTPException(status_code=400, detail="Job description and cover letter are required")

        term_alignment = await technical_term_agent.standardize_terms(
            request.job_description,
            request.cover_letter
        )
        
        # Add debug logging
        print(f"Term alignment result: {term_alignment}")
        return term_alignment
        
    except Exception as e:
        print(f"Error in standardize_terms: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))