from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Dict, List
from enum import Enum
from app.agents.generation_analysis import CoverLetter

class DocumentType(str, Enum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    COVER_LETTER = "cover_letter"

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class DocumentRequest(BaseSchema):
    content: str
    doc_type: str
    metadata: Dict[str, str]

class GenerationRequest(BaseSchema):
    job_description: str
    resume_id: str
    resume_content: str  # Add this field
    preferences: Optional[Dict] = Field(default_factory=dict)

class GenerationResponse(BaseSchema):
    content: str
    metadata: Dict
    similar_documents: Optional[List[Dict]] = Field(default_factory=list)

# Skills Analysis Models
class TechnicalSkill(BaseSchema):
    skill: str
    level: str
    years: Optional[float]
    context: str

class SoftSkill(BaseSchema):
    skill: str
    evidence: str

class Achievement(BaseSchema):
    description: str
    metrics: str
    skills_demonstrated: List[str]

class SkillsAnalysis(BaseSchema):
    technical_skills: List[TechnicalSkill]
    soft_skills: List[SoftSkill]
    achievements: List[Achievement]
    metadata: Dict[str, str] = Field(default_factory=dict)

# Requirements Analysis Models
class Requirement(BaseSchema):
    skill: str
    description: str
    years_experience: int = 0

class CultureIndicator(BaseSchema):
    aspect: str
    description: str

class Responsibility(BaseSchema):
    responsibility: str
    description: str

class JobRequirementsResponse(BaseSchema):
    analysis: Dict[str, List[Dict[str, str]]]
    vector_ids: Dict[str, str]

class AnalyzeJobDescriptionRequest(BaseSchema):
    job_description: str
    store_vectors: bool = True

# Request/Response models for routes
class AnalyzeSkillsRequest(BaseSchema):
    content: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class AnalyzeSkillsResponse(BaseSchema):
    analysis: SkillsAnalysis
    vector_ids: Optional[Dict[str, str]] = None

class AnalyzeRequirementsRequest(BaseSchema):
    job_description: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class AnalyzeStrategyRequest(BaseSchema):
    resume_content: str
    job_description: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class GenerateCoverLetterRequest(BaseSchema):
    skills_analysis: Dict
    requirements_analysis: Dict
    strategy: Dict
    preferences: Optional[Dict] = None

class RefineCoverLetterRequest(BaseSchema):
    cover_letter: CoverLetter
    feedback: Dict[str, str]

class GenerationPreferences(BaseSchema):
    """Preferences for cover letter generation."""
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"
    focus_points: Optional[List[str]] = []
    style_guide: Optional[Dict[str, Any]] = {}
    custom_instructions: Optional[str] = None

class JobRequirements(BaseSchema):
    """Job requirements analysis result."""
    core_requirements: List[Requirement]
    nice_to_have: List[Requirement]
    culture_indicators: List[CultureIndicator]
    key_responsibilities: List[Responsibility]

class ATSAnalysisRequest(BaseSchema):
    cover_letter: str
    job_description: str
    requirements_analysis: Dict

class ContentValidationRequest(BaseSchema):
    cover_letter: str
    resume: str
    job_description: str

class TechnicalTermRequest(BaseSchema):
    job_description: str
    cover_letter: str

class ResumeUploadRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ResumeResponse(BaseModel):
    content: str
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = None