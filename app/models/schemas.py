from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, List
from enum import Enum

class DocumentType(str, Enum):
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    COVER_LETTER = "cover_letter"

class DocumentRequest(BaseModel):
    content: str
    doc_type: DocumentType
    metadata: Optional[Dict] = Field(default_factory=dict)

class GenerationRequest(BaseModel):
    job_description: str
    resume_id: str
    preferences: Optional[Dict] = Field(default_factory=dict)

class GenerationResponse(BaseModel):
    content: str
    metadata: Dict
    similar_documents: Optional[List[Dict]] = Field(default_factory=list)

class TechnicalSkill(BaseModel):
    skill: str
    level: str
    years: Optional[float]
    context: str

class SoftSkill(BaseModel):
    skill: str
    evidence: str

class Achievement(BaseModel):
    description: str
    metrics: str
    skills_demonstrated: List[str]

class SkillsAnalysis(BaseModel):
    technical_skills: List[TechnicalSkill]
    soft_skills: List[SoftSkill]
    achievements: List[Achievement]
    metadata: Dict[str, str]

class Requirement(BaseModel):
    skill: str
    description: str
    years_experience: int = 0

class CultureIndicator(BaseModel):
    aspect: str
    description: str

class Responsibility(BaseModel):
    responsibility: str
    description: str

class JobRequirementsResponse(BaseModel):
    analysis: Dict[str, List[Dict[str, str]]]
    vector_ids: Dict[str, str]

class AnalyzeJobDescriptionRequest(BaseModel):
    job_description: str
    store_vectors: bool = True