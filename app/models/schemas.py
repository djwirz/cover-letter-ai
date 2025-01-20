from pydantic import BaseModel, Field
from typing import Optional, Dict, List
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