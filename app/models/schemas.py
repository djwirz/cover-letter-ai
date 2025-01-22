from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Optional, Dict, List
from enum import Enum

from app.agents.generation_analysis import CoverLetter

class DocumentType(str, Enum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    COVER_LETTER = "cover_letter"

class DocumentRequest(BaseModel):
    model_config = ConfigDict()
    content: str
    doc_type: DocumentType
    metadata: Optional[Dict] = Field(default_factory=dict)

class GenerationRequest(BaseModel):
    model_config = ConfigDict()
    job_description: str
    resume_id: str
    preferences: Optional[Dict] = Field(default_factory=dict)

class GenerationResponse(BaseModel):
    model_config = ConfigDict()
    content: str
    metadata: Dict
    similar_documents: Optional[List[Dict]] = Field(default_factory=list)

# Skills Analysis Models
class TechnicalSkill(BaseModel):
    model_config = ConfigDict()
    skill: str
    level: str
    years: Optional[float]
    context: str

class SoftSkill(BaseModel):
    model_config = ConfigDict()
    skill: str
    evidence: str

class Achievement(BaseModel):
    model_config = ConfigDict()
    description: str
    metrics: str
    skills_demonstrated: List[str]

class SkillsAnalysis(BaseModel):
    model_config = ConfigDict()
    technical_skills: List[TechnicalSkill]
    soft_skills: List[SoftSkill]
    achievements: List[Achievement]
    metadata: Dict[str, str] = Field(default_factory=dict)

# Requirements Analysis Models
class Requirement(BaseModel):
    model_config = ConfigDict()
    skill: str
    description: str
    years_experience: int = 0

class CultureIndicator(BaseModel):
    model_config = ConfigDict()
    aspect: str
    description: str

class Responsibility(BaseModel):
    model_config = ConfigDict()
    responsibility: str
    description: str

class JobRequirementsResponse(BaseModel):
    model_config = ConfigDict()
    analysis: Dict[str, List[Dict[str, str]]]
    vector_ids: Dict[str, str]

class AnalyzeJobDescriptionRequest(BaseModel):
    model_config = ConfigDict()
    job_description: str
    store_vectors: bool = True

# Request/Response models for routes
class AnalyzeSkillsRequest(BaseModel):
    model_config = ConfigDict()
    content: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class AnalyzeSkillsResponse(BaseModel):
    model_config = ConfigDict()
    analysis: SkillsAnalysis
    vector_ids: Optional[Dict[str, str]] = None

class AnalyzeRequirementsRequest(BaseModel):
    model_config = ConfigDict()
    job_description: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class AnalyzeStrategyRequest(BaseModel):
    model_config = ConfigDict()
    resume_content: str
    job_description: str
    metadata: Optional[Dict] = Field(default_factory=dict)

class GenerateCoverLetterRequest(BaseModel):
    skills_analysis: Dict
    requirements_analysis: Dict
    strategy: Dict
    preferences: Optional[Dict] = None

class RefineCoverLetterRequest(BaseModel):
    cover_letter: CoverLetter
    feedback: Dict[str, str]