from langchain_openai import ChatOpenAI
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import ValidationError
from typing import Dict, List, Optional
from logging import getLogger
import traceback
import json
from datetime import datetime
from app.models.schemas import SkillsAnalysis

logger = getLogger(__name__)

class SkillsAnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
        self.logger = logger
        self.skills_schema = {
            "type": "object",
            "properties": {
                "technical_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill": {"type": "string"},
                            "level": {"type": "string"},
                            "years": {"type": "number"},
                            "context": {"type": "string"}
                        }
                    }
                },
                "soft_skills": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "skill": {"type": "string"},
                            "evidence": {"type": "string"}
                        }
                    }
                },
                "achievements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "description": {"type": "string"},
                            "metrics": {"type": "string"},
                            "skills_demonstrated": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                }
            }
        }
        self._setup_agent()

    def _create_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", """You are an expert skills analysis agent specialized in parsing resumes 
            and professional documents. Your goal is to extract, categorize, and evaluate skills 
            and achievements with high precision. Focus on:
            1. Technical skills with proficiency levels
            2. Soft skills with supporting evidence
            3. Quantifiable achievements
            4. Years of experience in each area
            
            Always look for specific evidence and context rather than just listing skills."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

    def _setup_agent(self):
        self.tools = [
            Tool(
                name="extract_skills",
                func=self._extract_skills,
                description="Extracts and categorizes skills from text"
            ),
            Tool(
                name="analyze_achievements",
                func=self._analyze_achievements,
                description="Identifies and analyzes quantifiable achievements"
            ),
            Tool(
                name="assess_proficiency",
                func=self._assess_proficiency,
                description="Evaluates skill levels based on context"
            )
        ]

        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self._create_prompt()
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )

    async def _extract_skills(self, text: str) -> Dict:
        """Extracts technical and soft skills from text."""
        try:
            response = await self.llm.invoke(f"""
            Analyze this text and extract skills:
            {text}
            
            Return the skills in JSON format following this schema:
            {json.dumps(self.skills_schema, indent=2)}
            """)
            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"Error extracting skills: {str(e)}")
            return {}

    async def _analyze_achievements(self, text: str) -> List[Dict]:
        """Identifies quantifiable achievements and their impact."""
        try:
            response = await self.llm.invoke(f"""
            Analyze this text and extract quantifiable achievements.
            Focus on specific metrics, improvements, and impact.
            Format each achievement with:
            - Description
            - Specific metrics/numbers
            - Skills demonstrated
            """)
            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"Error analyzing achievements: {str(e)}")
            return []

    async def _assess_proficiency(self, skill_data: Dict) -> Dict:
        """Evaluates skill levels based on context and evidence."""
        try:
            response = await self.llm.invoke(f"""
            Evaluate the proficiency level for each skill based on:
            {json.dumps(skill_data, indent=2)}
            
            Consider:
            - Years of experience
            - Complexity of projects
            - Leadership/ownership level
            - Technical depth demonstrated
            
            Return a proficiency assessment (Beginner/Intermediate/Advanced/Expert)
            with supporting evidence.
            """)
            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"Error assessing proficiency: {str(e)}")
            return {}

    async def _run_analysis_pipeline(self, text: str) -> Dict:
        """Runs the complete analysis pipeline."""
        try:
            raw_analysis = await self.agent_executor.ainvoke({
                "input": text,
                "output_schema": self.skills_schema
            })

            structured_analysis = {
                "technical_skills": [],
                "soft_skills": [],
                "achievements": []
            }

            # Process the raw analysis into structured format
            if raw_result := await self._structure_analysis(raw_analysis["output"]):
                structured_analysis.update(raw_result)

            return {
                "skills_analysis": structured_analysis,
                "metadata": {
                    "model_used": "gpt-4",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            }
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise

    async def _structure_analysis(self, raw_analysis: str) -> Dict:
        """Converts raw analysis into structured format."""
        prompt = f"""
        Convert this analysis into a structured format following exactly this schema:
        {json.dumps(self.skills_schema, indent=2)}

        Analysis to convert:
        {raw_analysis}
        
        Ensure all fields match the schema exactly and all values are appropriate for their types.
        """
        
        try:
            response = await self.llm.invoke(prompt)
            return json.loads(response.content)
        except Exception as e:
            self.logger.error(f"Error structuring analysis: {str(e)}")
            return {}

    async def analyze(self, resume_text: str) -> Dict:
        """Main method to analyze a resume."""
        try:
            # Input validation
            if not resume_text or len(resume_text.strip()) < 50:
                raise ValueError("Resume text too short or empty")

            # Run analysis
            result = await self._run_analysis_pipeline(resume_text)
            
            # Validate output against schema
            try:
                SkillsAnalysis(**result["skills_analysis"])
            except ValidationError as e:
                self.logger.error(f"Output validation failed: {str(e)}")
                raise

            return result

        except Exception as e:
            self.logger.error(f"Analysis failed: {traceback.format_exc()}")
            raise