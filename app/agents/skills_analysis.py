from datetime import datetime
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from typing import List, Dict
import json

class SkillsAnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4", temperature=0)
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
            MessagesPlaceholder(variable_name="agent_scratchpad")  # Add this line
        ])
    async def _extract_skills(self, text: str) -> Dict:
        """Extracts technical and soft skills from text."""
        try:
            response = await self.llm.invoke(f"""
            Analyze this text and extract skills:
            {text}
            
            Return the skills in JSON format following this schema:
            {json.dumps(self.skills_schema, indent=2)}
            """)
            return json.loads(response)
        except Exception as e:
            print(f"Error extracting skills: {str(e)}")
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
            return json.loads(response)
        except Exception as e:
            print(f"Error analyzing achievements: {str(e)}")
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
            return json.loads(response)
        except Exception as e:
            print(f"Error assessing proficiency: {str(e)}")
            return {}

    async def analyze(self, resume_text: str) -> Dict:
        """Main method to analyze a resume."""
        try:
            result = await self.agent_executor.ainvoke({
                "input": resume_text,
                "output_schema": self.skills_schema
            })
            
            return {
                "skills_analysis": result,
                "metadata": {
                    "model_used": "gpt-4",
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "1.0"
                }
            }
        except Exception as e:
            print(f"Error in skills analysis: {str(e)}")
            raise