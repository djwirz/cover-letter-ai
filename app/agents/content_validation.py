from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class ValidationIssue(BaseModel):
    """Represents a content validation issue."""
    type: str = Field(description="Type of issue (unsupported_claim, inconsistency, etc)")
    severity: str = Field(description="high/medium/low impact")
    location: str = Field(description="Where in the letter the issue appears")
    description: str = Field(description="Detailed description of the issue")
    suggestion: str = Field(description="Suggested fix")

class ValidationResult(BaseModel):
    """Complete validation analysis results."""
    issues: List[ValidationIssue] = Field(default_factory=list)
    supported_claims: List[Dict[str, str]] = Field(
        description="Claims that are properly supported by the resume"
    )
    requirement_coverage: Dict[str, bool] = Field(
        description="Which job requirements are addressed"
    )
    confidence_score: float = Field(ge=0, le=1)

class ContentValidationAgent:
    """
    Validates cover letter content against resume and job requirements for 
    accuracy and supportability.
    """
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.output_parser = PydanticOutputParser(pydantic_object=ValidationResult)
        
    async def validate_content(
        self,
        cover_letter: str,
        resume: str,
        job_description: str
    ) -> ValidationResult:
        """
        Validates cover letter content against resume and job requirements.
        """
        try:
            # Handle None values first
            if any(doc is None for doc in [cover_letter, resume, job_description]):
                raise Exception("Error during content validation: None values are not allowed")
                
            # Then handle empty strings
            if not all([cover_letter.strip(), resume.strip(), job_description.strip()]):
                raise ValueError("All input documents are required")
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a content validation expert. Analyze this cover letter 
                for accuracy and supportability against the provided resume and job requirements.
                
                Focus on:
                1. Verifying all claims are supported by resume content
                2. Ensuring job requirements are properly addressed
                3. Identifying any inconsistencies or exaggerations
                4. Checking for factual accuracy
                
                Provide structured validation results."""),
                ("human", """Cover Letter:
                {cover_letter}
                
                Resume:
                {resume}
                
                Job Description:
                {job_description}
                
                Validate content and provide detailed analysis.
                {format_instructions}
                """)
            ])
            
            messages = prompt.format_messages(
                cover_letter=cover_letter,
                resume=resume,
                job_description=job_description,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(messages)
            return self.output_parser.parse(response.content)
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Error during content validation: {str(e)}")

    async def suggest_improvements(
        self,
        validation_result: ValidationResult
    ) -> List[Dict]:
        """
        Generate specific suggestions for improving content accuracy.
        """
        suggestions = []
        
        for issue in validation_result.issues:
            suggestions.append({
                "issue_type": issue.type,
                "location": issue.location,
                "suggestion": issue.suggestion,
                "priority": issue.severity
            })
            
        return sorted(suggestions, key=lambda x: x["priority"])