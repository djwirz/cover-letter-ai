from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class Requirement(BaseModel):
    skill: str
    description: str
    years_experience: int = Field(default=0)

class CultureIndicator(BaseModel):
    aspect: str
    description: str

class Responsibility(BaseModel):
    responsibility: str
    description: str

class JobRequirements(BaseModel):
    core_requirements: List[Requirement] = Field(
        description="List of essential skills/requirements with description and years of experience"
    )
    nice_to_have: List[Requirement] = Field(
        description="List of preferred but not mandatory skills/qualifications"
    )
    culture_indicators: List[CultureIndicator] = Field(
        description="Company culture aspects mentioned in the job description"
    )
    key_responsibilities: List[Responsibility] = Field(
        description="Main job duties and responsibilities"
    )

class RequirementsAnalysisAgent:
    """Agent for analyzing job descriptions to extract structured requirements data."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.output_parser = PydanticOutputParser(pydantic_object=JobRequirements)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert job requirements analyzer. Extract and categorize 
            information from job descriptions into structured data. Focus on:
            
            1. Core requirements: Essential technical skills, education, and experience
            - Include skill name, description, and years of experience if specified
            2. Nice-to-have skills: Preferred qualifications that aren't mandatory
            - Include skill name and description
            3. Culture indicators: Work environment, values, and company culture mentions
            - Include aspect name and detailed description
            4. Key responsibilities: Main duties and expectations
            - Include responsibility title and detailed description
            
            Structure each component according to their respective schemas."""),
            ("human", "Please analyze the following job description:\n\n{job_description}"),
            ("system", "Format the output as follows:\n{format_instructions}")
        ])

    async def analyze(self, job_description: str) -> JobRequirements:
        """
        Analyze a job description and extract structured requirements data.
        
        Args:
            job_description (str): The job description text to analyze
            
        Returns:
            JobRequirements: Structured data containing the analyzed requirements
        """
        try:
            formatted_prompt = self.prompt.format_messages(
                job_description=job_description,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            return self.output_parser.parse(response.content)
            
        except Exception as e:
            raise Exception(f"Error analyzing job description: {str(e)}")

    async def analyze_and_vectorize(self, job_description: str, vector_store) -> Dict:
        """
        Analyze job description and store the vectorized results.
        
        Args:
            job_description (str): The job description text
            vector_store: Vector store instance for storing embeddings
            
        Returns:
            Dict: Analysis results and vector store reference
        """
        # Analyze the job description
        requirements = await self.analyze(job_description)
        
        # Prepare data for vectorization
        vectors_data = {
            "core_requirements": " ".join([
                f"{req.skill} ({req.years_experience}+ years): {req.description}"
                for req in requirements.core_requirements
            ]),
            "nice_to_have": " ".join([
                f"{skill.skill}: {skill.description}"
                for skill in requirements.nice_to_have
            ]),
            "culture_indicators": " ".join([
                f"{indicator.aspect}: {indicator.description}"
                for indicator in requirements.culture_indicators
            ]),
            "key_responsibilities": " ".join([
                f"{resp.responsibility}: {resp.description}"
                for resp in requirements.key_responsibilities
            ])
        }
        
        # Store in vector database
        vector_ids = {}
        for category, text in vectors_data.items():
            vector_id = await vector_store.add_vectors(
                text=text,
                metadata={
                    "type": "job_requirement",
                    "category": category
                }
            )
            vector_ids[category] = vector_id
            
        return {
            "analysis": requirements.model_dump(),
            "vector_ids": vector_ids
        }