from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from typing import List, Dict

class EnhancedAIService:
    def __init__(self, vector_service):
        self.vector_service = vector_service
        self.llm = ChatOpenAI(model="gpt-4")
    
    async def generate_cover_letter(
        self, 
        job_description: str, 
        context_documents: List,
        preferences: Dict = None
    ):
        try:
            # Extract content from context documents
            context = "\n\n".join([
                doc[0]['page_content'] for doc in context_documents
            ])
            
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
            
            chain = prompt | self.llm
            response = await chain.ainvoke({
                "job_description": job_description,
                "context": context,
                "preferences": str(preferences if preferences else {})
            })
            
            return response.content
            
        except Exception as e:
            print(f"Error generating cover letter: {str(e)}")
            raise e