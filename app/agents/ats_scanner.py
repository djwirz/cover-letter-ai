from typing import Dict, List, Optional
from pydantic import BaseModel, Field, validator
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.agents.base import BaseAgent
from app.settings.config import settings
from app.agents.utils.logging import setup_logger

logger = setup_logger("ATSScanner")

class ATSIssue(BaseModel):
    """Represents an ATS parsing issue"""
    type: str = Field(..., description="Type of issue (format, keyword, header, etc)")
    description: str = Field(..., description="Detailed description of the issue")
    severity: str = Field(..., description="Impact level (high/medium/low)")
    suggestion: str = Field(..., description="Suggested fix for the issue")

    @validator('severity')
    def validate_severity(cls, value: str) -> str:
        """Validate severity level"""
        if value.lower() not in {'high', 'medium', 'low'}:
            raise ValueError("Severity must be high, medium, or low")
        return value.lower()

class ATSAnalysis(BaseModel):
    """Complete ATS analysis results"""
    keyword_match_score: float = Field(..., ge=0, le=1)
    parse_confidence: float = Field(..., ge=0, le=1)
    key_terms_found: List[str] = Field(default_factory=list)
    key_terms_missing: List[str] = Field(default_factory=list)
    format_issues: List[ATSIssue] = Field(default_factory=list)
    headers_analysis: Dict[str, bool] = Field(
        default_factory=dict,
        description="Status of key header elements"
    )

class ATSScannerAgent(BaseAgent[ATSAnalysis]):
    """Agent for analyzing cover letters for ATS compatibility"""
    
    def __init__(self):
        super().__init__()
        self.output_parser = PydanticOutputParser(pydantic_object=ATSAnalysis)
        self.prompt = self._create_prompt()
        
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the ATS analysis prompt template"""
        return ChatPromptTemplate.from_messages([
            ("system", """You are an ATS system expert. Analyze this cover letter for 
            compatibility with major ATS systems (Workday, Greenhouse, Lever, etc).
            
            Focus on:
            1. Keyword identification and matching
            2. Format and parsing issues
            3. Header and contact information parsing
            4. Technical term consistency
            
            Return a structured analysis following the exact schema provided.
            """),
            ("human", """Cover Letter:
            {cover_letter}
            
            Job Description:
            {job_description}
            
            Known Requirements:
            {requirements}
            
            Analyze for ATS compatibility and provide structured feedback.
            {format_instructions}
            """)
        ])

    async def process(self, cover_letter: str, job_description: str, requirements_analysis: Dict) -> ATSAnalysis:
        """
        Main processing method for ATS scanning.
        
        Args:
            cover_letter: The cover letter content
            job_description: The job description
            requirements_analysis: Analysis of job requirements
            
        Returns:
            ATSAnalysis: Structured analysis results
            
        Raises:
            ValueError: If inputs are invalid
            Exception: If analysis fails
        """
        return await self.scan_letter(cover_letter, job_description, requirements_analysis)

    async def scan_letter(
        self,
        cover_letter: str,
        job_description: str,
        requirements_analysis: Dict
    ) -> ATSAnalysis:
        """
        Analyze cover letter for ATS compatibility
        
        Args:
            cover_letter: The cover letter content
            job_description: The job description
            requirements_analysis: Analysis of job requirements
            
        Returns:
            ATSAnalysis: Structured analysis results
            
        Raises:
            ValueError: If inputs are invalid
            Exception: If analysis fails
        """
        logger.info("Starting ATS scan")
        
        if not all([cover_letter, job_description, requirements_analysis]):
            raise ValueError("All inputs are required")
            
        try:
            messages = self.prompt.format_messages(
                cover_letter=cover_letter,
                job_description=job_description,
                requirements=requirements_analysis,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(messages)
            result = self.output_parser.parse(response.content)
            
            logger.debug(f"ATS scan completed with score: {result.keyword_match_score}")
            return result
            
        except Exception as e:
            logger.error(f"ATS scan failed: {str(e)}")
            raise Exception(f"ATS analysis error: {str(e)}") from e

    async def suggest_improvements(
        self,
        analysis: ATSAnalysis,
        requirements_analysis: Dict
    ) -> List[Dict]:
        """
        Generate specific suggestions for improving ATS compatibility
        
        Args:
            analysis: ATS analysis results
            requirements_analysis: Job requirements analysis
            
        Returns:
            List of improvement suggestions
        """
        logger.info("Generating improvement suggestions")
        
        if analysis.keyword_match_score > 0.9 and not analysis.format_issues:
            return []
            
        suggestions = []
        
        # Handle missing keywords
        if analysis.key_terms_missing:
            suggestions.append({
                "type": "keyword_addition",
                "details": "Add missing key terms",
                "terms": analysis.key_terms_missing,
                "priority": "high"
            })
            
        # Handle format issues
        for issue in analysis.format_issues:
            suggestions.append({
                "type": "format_fix",
                "details": issue.description,
                "suggestion": issue.suggestion,
                "priority": issue.severity
            })
            
        logger.debug(f"Generated {len(suggestions)} improvement suggestions")
        return suggestions