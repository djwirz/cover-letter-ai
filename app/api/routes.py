from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.core.ai_service import EnhancedAIService
from app.core.vector_store import VectorService
from app.core.database import Database
from app.models.schemas import DocumentRequest, DocumentType, GenerationRequest, GenerationResponse
from typing import List

router = APIRouter()

# Initialize services
db = Database()
vector_service = VectorService(db.client)
ai_service = EnhancedAIService(vector_service)

@router.post("/documents", response_model=dict)
async def process_document(request: DocumentRequest):
    try:
        doc_id = await vector_service.process_document(
            request.content,
            request.doc_type,
            request.metadata
        )
        return {"id": doc_id, "status": "processed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=GenerationResponse)
async def generate_cover_letter(request: GenerationRequest):
    try:
        # Get relevant context from both resume and similar job descriptions
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
        
        # Generate letter using combined context
        content = await ai_service.generate_cover_letter(
            job_description=request.job_description,
            context_documents=resume_context + job_context,
            preferences=request.preferences
        )
        
        # Extract metadata safely from context documents
        similar_docs = []
        for doc, score in (resume_context + job_context):
            if isinstance(doc, dict) and 'metadata' in doc:
                similar_docs.append(doc['metadata'])
        
        return GenerationResponse(
            content=content,
            metadata={"timestamp": datetime.utcnow().isoformat()},
            similar_documents=similar_docs
        )
    except Exception as e:
        print(f"Debug - Error details: {str(e)}")  # Add debug logging
        raise HTTPException(status_code=500, detail=str(e))