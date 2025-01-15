from pydantic import BaseModel
from typing import Optional, Dict

class GenerateLetterRequest(BaseModel):
    job_description: str
    resume: str
    preferences: Optional[Dict] = None

class GenerateLetterResponse(BaseModel):
    content: str
    metadata: Dict