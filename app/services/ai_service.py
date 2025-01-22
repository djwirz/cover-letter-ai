from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict
from app.settings.config import Settings
from app.services.vector_service import VectorService

class EnhancedAIService:
    def __init__(self, settings: Settings, vector_service: VectorService):
        self.settings = settings
        self.vector_service = vector_service
        self.model = None
    
    async def initialize(self):
        """Initialize AI model and resources"""
        self.model = ChatOpenAI(model="gpt-4")
    
    async def close(self):
        """Cleanup AI service resources"""
        self.model = None
    
    async def generate_response(self, prompt: str, context: dict) -> str:
        """Generate AI response with context"""
        try:
            template = """You are an expert cover letter writer. 
            Use the provided examples and context to generate a compelling letter.
            Maintain professionalism while showcasing relevant experience.

            Job Description: {job_description}
            
            Relevant Context:
            {context}
            
            Preferences: {preferences}
            
            Generate a cover letter that:
            1. Matches the tone and requirements of the job description
            2. Incorporates relevant experience from the context
            3. Is specific and tailored to this role
            """
            
            prompt = ChatPromptTemplate.from_template(template)
            
            chain = prompt | self.model
            response = await chain.ainvoke({
                "job_description": prompt,
                "context": context,
                "preferences": str(context.get('preferences', {}))
            })
            
            return response.content
            
        except Exception as e:
            print(f"Error generating cover letter: {str(e)}")
            raise e
    
    async def analyze_requirements(self, text: str) -> dict:
        """Analyze job requirements"""
        # Implementation of analyze_requirements method
        pass