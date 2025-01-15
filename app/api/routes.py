import datetime
from fastapi import APIRouter, HTTPException
from app.core.ai_service import AIService
from app.core.database import Database
from app.models.schemas import GenerateLetterRequest, GenerateLetterResponse

router = APIRouter()
ai_service = AIService()
db = Database()

@router.post("/generate", response_model=GenerateLetterResponse)
async def generate_letter(request: GenerateLetterRequest):
    try:
        # Generate letter
        content = await ai_service.generate_cover_letter(
            request.job_description,
            request.resume
        )
        
        # Store in database
        metadata = {
            "timestamp": str(datetime.now()),
            "preferences": request.preferences
        }
        
        await db.store_letter(content, metadata)
        
        return GenerateLetterResponse(
            content=content,
            metadata=metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))