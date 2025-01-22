from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class SkillRequirement(BaseModel):
    skill: str
    description: str
    years_experience: Optional[int] = 0

class SkillMatch(BaseModel):
    skill: str
    candidate_experience: int
    required_experience: int

class SkillGap(BaseModel):
    skill: str
    gap: int  # Years of experience gap

class SkillGapAnalysis(BaseModel):
    missing_skills: List[SkillRequirement] = Field(
        description="Required skills that are not present in the candidate's profile"
    )
    partial_matches: List[SkillGap] = Field(
        description="Skills where the candidate has some but not all required experience"
    )
    strong_matches: List[SkillMatch] = Field(
        description="Skills where the candidate meets or exceeds requirements"
    )

class TalkingPoint(BaseModel):
    topic: str = Field(description="The main topic or skill to address")
    strategy: str = Field(description="How to position this point in the cover letter")
    evidence: str = Field(description="Specific achievements or experiences to reference")
    priority: int = Field(description="Priority order for this talking point (1-5)")

class CoverLetterStrategy(BaseModel):
    gap_analysis: SkillGapAnalysis
    key_talking_points: List[TalkingPoint]
    overall_approach: str = Field(
        description="High-level strategy for the cover letter based on fit analysis"
    )
    tone_recommendations: Dict[str, str] = Field(
        description="Specific recommendations for tone and positioning"
    )

class CoverLetterStrategyAgent:
    """Agent for developing personalized cover letter strategies based on fit analysis."""
    
    def __init__(
        self, 
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.0,
        vector_store = None
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.vector_store = vector_store
        self.output_parser = PydanticOutputParser(pydantic_object=CoverLetterStrategy)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cover letter strategist. Analyze the fit between 
            a candidate's skills and job requirements, then develop a personalized strategy 
            that addresses gaps and emphasizes strengths. Consider:

            1. Skills Analysis:
               - Identify missing required skills
               - Note partially matching skills
               - Highlight strong matches
            
            2. Strategic Approach:
               - Determine how to address skill gaps
               - Plan evidence-based talking points
               - Consider company culture fit
               
            3. Past Successful Strategies:
               - Learn from similar past situations
               - Adapt proven approaches
               - Maintain consistency with past tone
            
            Provide detailed, actionable strategies while maintaining authenticity."""),
            ("human", """Please analyze the following:

            Candidate Skills:
            {skills_analysis}

            Job Requirements:
            {requirements_analysis}

            Past Cover Letters:
            {similar_letters}

            Develop a comprehensive strategy that addresses gaps and builds on strengths."""),
            ("system", "Format the output as follows:\n{format_instructions}")
        ])

    async def find_similar_letters(
        self,
        requirements_analysis: Dict,
        limit: int = 3
    ) -> List[Dict]:
        """Find similar past cover letters from the vector store."""
        if not self.vector_store:
            return []
            
        # Prepare search text from requirements
        search_text = " ".join([
            f"{req['skill']}: {req['description']}"
            for req in requirements_analysis.get('core_requirements', [])
        ])
        
        # Search vector store
        results = await self.vector_store.similarity_search(
            text=search_text,
            limit=limit,
            metadata_filter={"type": "cover_letter"}
        )
        
        return results

    async def analyze_skill_gaps(
        self,
        skills_analysis: Dict,
        requirements_analysis: Dict
    ) -> SkillGapAnalysis:
        """Analyze gaps between candidate skills and job requirements."""
        try:
            # Extract core requirements and skills for comparison
            required_skills = {
                req['skill'].lower(): req
                for req in requirements_analysis.get('core_requirements', [])
            }
            candidate_skills = {
                skill['skill'].lower(): skill
                for skill in skills_analysis.get('technical_skills', []) + 
                            skills_analysis.get('soft_skills', [])
            }
            
            # Categorize skills
            missing_skills = []
            partial_matches = []
            strong_matches = []
            
            for req_skill, req_details in required_skills.items():
                if req_skill not in candidate_skills:
                    missing_skills.append(SkillRequirement(
                        skill=req_details['skill'],
                        description=req_details['description'],
                        years_experience=req_details.get('years_experience', 0)
                    ))
                else:
                    # Compare experience levels if available
                    req_years = req_details.get('years_experience', 0)
                    candidate_years = candidate_skills[req_skill].get('years_experience', 0)
                    
                    if candidate_years >= req_years:
                        strong_matches.append(SkillMatch(
                            skill=req_skill,
                            candidate_experience=candidate_years,
                            required_experience=req_years
                        ))
                    else:
                        partial_matches.append(SkillGap(
                            skill=req_skill,
                            gap=req_years - candidate_years
                        ))
            
            return SkillGapAnalysis(
                missing_skills=missing_skills,
                partial_matches=partial_matches,
                strong_matches=strong_matches
            )
            
        except Exception as e:
            raise Exception(f"Error analyzing skill gaps: {str(e)}")

    async def develop_strategy(
        self,
        skills_analysis: Dict,
        requirements_analysis: Dict
    ) -> CoverLetterStrategy:
        """
        Develop a comprehensive cover letter strategy based on skill gap analysis
        and past successful approaches.
        """
        try:
            # Find similar past cover letters
            similar_letters = await self.find_similar_letters(requirements_analysis)
            
            # Analyze skill gaps
            gap_analysis = await self.analyze_skill_gaps(
                skills_analysis,
                requirements_analysis
            )
            
            # Generate strategy using LLM
            formatted_prompt = self.prompt.format_messages(
                skills_analysis=skills_analysis,
                requirements_analysis=requirements_analysis,
                similar_letters=similar_letters,
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            strategy = self.output_parser.parse(response.content)
            
            # Update gap analysis with our detailed analysis
            strategy.gap_analysis = gap_analysis
            
            return strategy
            
        except Exception as e:
            raise Exception(f"Error developing cover letter strategy: {str(e)}")

    async def get_strategy_vectors(self, strategy: CoverLetterStrategy) -> Dict[str, str]:
        """Convert strategy components into vectors for storage."""
        if not self.vector_store:
            return {}
            
        vectors_data = {
            "gap_analysis": " ".join([
                f"Missing: {skill.skill} ({skill.years_experience}+ years), "
                for skill in strategy.gap_analysis.missing_skills
            ] + [
                f"Partial: {skill.skill} (gap: {skill.gap} years), "
                for skill in strategy.gap_analysis.partial_matches
            ]),
            "talking_points": " ".join([
                f"{point.topic}: {point.strategy}" for point in strategy.key_talking_points
            ]),
            "approach": strategy.overall_approach
        }
        
        # Store in vector database
        vector_ids = {}
        for category, text in vectors_data.items():
            vector_id = await self.vector_store.add_vectors(
                text=text,
                metadata={
                    "type": "cover_letter_strategy",
                    "category": category
                }
            )
            vector_ids[category] = vector_id
            
        return vector_ids