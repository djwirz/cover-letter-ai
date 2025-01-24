from typing import Dict, List
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class ATSIssue(BaseModel):
    """Represents an ATS parsing issue."""
    type: str = Field(description="Type of issue (format, keyword, header, etc)")
    description: str = Field(description="Detailed description of the issue")
    severity: str = Field(description="high/medium/low impact on ATS parsing")
    suggestion: str = Field(description="Suggested fix for the issue")

class ATSAnalysis(BaseModel):
    """Complete ATS analysis results."""
    keyword_match_score: float = Field(ge=0, le=1)
    parse_confidence: float = Field(ge=0, le=1)
    key_terms_found: List[str] = Field(default_factory=list)
    key_terms_missing: List[str] = Field(default_factory=list)
    format_issues: List[ATSIssue] = Field(default_factory=list)
    headers_analysis: Dict[str, bool] = Field(
        description="Status of key header elements (contact info, date, etc)"
    )

class ATSScannerAgent:
    """
    Analyzes cover letters for ATS system compatibility. Works alongside existing 
    generation and requirements agents to ensure optimal parsing.
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
        self.output_parser = PydanticOutputParser(pydantic_object=ATSAnalysis)
        
    async def scan_letter(
        self,
        cover_letter: str,
        job_description: str,
        requirements_analysis: Dict  # From your existing RequirementsAnalysisAgent
    ) -> ATSAnalysis:
        """
        Analyzes cover letter for ATS compatibility, using insights from 
        requirements analysis.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an ATS system expert. Analyze this cover letter for 
            compatibility with major ATS systems (Workday, Greenhouse, Lever, etc).
            
            Focus on:
            1. Keyword identification and matching
            2. Format and parsing issues
            3. Header and contact information parsing
            4. Technical term consistency
            
            Consider both basic ATS parsing and modern ML-based ATS systems.
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
        
        try:
            messages = prompt.format_messages(
                cover_letter=cover_letter,
                job_description=job_description,
                requirements=requirements_analysis,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(messages)
            return self.output_parser.parse(response.content)
            
        except Exception as e:
            raise Exception(f"Error during ATS analysis: {str(e)}")
    
    async def suggest_improvements(
        self,
        analysis: ATSAnalysis,
        requirements_analysis: Dict
    ) -> List[Dict]:
        """
        Generate specific suggestions for improving ATS compatibility
        based on analysis results.
        """
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
            
        return suggestions