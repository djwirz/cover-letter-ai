from typing import Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from app.models.schemas import (
    TechnicalSkill,
    SoftSkill,
    Achievement,
    SkillsAnalysis
)

class SkillsAnalysisAgent:
    """Agent for analyzing resumes to extract skills and achievements."""
    
    def __init__(self, model_name: str = "gpt-4-turbo-preview", temperature: float = 0.0):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.output_parser = PydanticOutputParser(pydantic_object=SkillsAnalysis)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume analyzer. Extract and categorize skills 
            and achievements from resumes into structured data. Focus on:
            
            1. Technical Skills:
               - Identify specific technologies and tools
               - Determine skill level and years of experience
               - Note the context where skills were applied
            
            2. Soft Skills:
               - Identify interpersonal and professional skills
               - Find specific evidence of their application
            
            3. Achievements:
               - Extract quantifiable accomplishments
               - Note metrics and impact
               - List skills demonstrated
            
            Be thorough and specific in your analysis."""),
            ("human", "Please analyze the following resume content:\n\n{content}"),
            ("system", "Format the output as follows:\n{format_instructions}")
        ])

    async def analyze(self, content: str) -> SkillsAnalysis:
        """
        Analyze resume content to extract skills and achievements.
        
        Args:
            content (str): The resume text to analyze
            
        Returns:
            SkillsAnalysis: Structured analysis of skills and achievements
        """
        try:
            formatted_prompt = self.prompt.format_messages(
                content=content,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            return self.output_parser.parse(response.content)
            
        except Exception as e:
            raise Exception(f"Error analyzing skills: {str(e)}")

    async def get_vectorized_skills(self, analysis: SkillsAnalysis) -> Dict[str, str]:
        """
        Convert skills analysis into a format suitable for vector storage.
        
        Args:
            analysis (SkillsAnalysis): The analyzed skills data
            
        Returns:
            Dict[str, str]: Skills formatted for vector storage
        """
        vectors = {
            "technical_skills": " ".join([
                f"{skill.skill} ({skill.level}, {skill.years} years): {skill.context}"
                for skill in analysis.technical_skills
            ]),
            "soft_skills": " ".join([
                f"{skill.skill}: {skill.evidence}"
                for skill in analysis.soft_skills
            ]),
            "achievements": " ".join([
                f"{achievement.description} ({achievement.metrics}) - Skills: {', '.join(achievement.skills_demonstrated)}"
                for achievement in analysis.achievements
            ])
        }
        
        return vectors