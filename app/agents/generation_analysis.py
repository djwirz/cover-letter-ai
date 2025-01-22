from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

class CoverLetterSection(BaseModel):
    content: str = Field(description="The actual content of this section")
    purpose: str = Field(description="The strategic purpose of this section")
    key_points: List[str] = Field(description="Main points addressed in this section")

class CoverLetter(BaseModel):
    greeting: str = Field(description="Personalized greeting")
    introduction: CoverLetterSection
    body_paragraphs: List[CoverLetterSection]
    closing: CoverLetterSection
    signature: str = Field(description="Professional signature")
    metadata: Dict[str, str] = Field(description="Additional information about the generation")

class CoverLetterGenerationAgent:
    """Agent responsible for generating tailored cover letters."""
    
    def __init__(
        self, 
        model_name: str = "gpt-4-turbo-preview",
        temperature: float = 0.7
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature
        )
        self.output_parser = PydanticOutputParser(pydantic_object=CoverLetter)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert cover letter writer who creates compelling, 
            personalized cover letters that effectively connect candidate experiences 
            with job requirements. Focus on:

            1. Strategy:
               - Use the provided strategy analysis to guide the letter's approach
               - Address identified gaps professionally
               - Emphasize key strengths and matches
            
            2. Style:
               - Maintain a professional but engaging tone
               - Use active voice and concrete examples
               - Keep paragraphs focused and concise
            
            3. Structure:
               - Create a compelling introduction that hooks the reader
               - Develop body paragraphs that follow the strategic talking points
               - Write a strong closing that reinforces interest and fit
            
            The letter should be authentic, specific, and demonstrate clear value to the employer."""),
            ("human", """Please generate a cover letter with the following:

            Skills Analysis:
            {skills_analysis}

            Requirements Analysis:
            {requirements_analysis}

            Strategy:
            {strategy}

            Preferences:
            {preferences}"""),
            ("system", "Format the output as follows:\n{format_instructions}")
        ])

    async def generate(
        self,
        skills_analysis: Dict,
        requirements_analysis: Dict,
        strategy: Dict,
        preferences: Optional[Dict] = None
    ) -> CoverLetter:
        """
        Generate a personalized cover letter based on analysis results.
        
        Args:
            skills_analysis: Analysis of candidate's skills
            requirements_analysis: Analysis of job requirements
            strategy: Strategic approach for the letter
            preferences: Optional customization preferences
            
        Returns:
            CoverLetter: Structured cover letter content
        """
        try:
            if not skills_analysis or not requirements_analysis or not strategy:
                raise ValueError("Required analysis data is missing")

            formatted_prompt = self.prompt.format_messages(
                skills_analysis=skills_analysis,
                requirements_analysis=requirements_analysis,
                strategy=strategy,
                preferences=preferences or {},
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(formatted_prompt)
            cover_letter = self.output_parser.parse(response.content)
            
            # Record generation metadata
            cover_letter.metadata.update({
                "model": self.llm.model_name,
                "temperature": str(self.llm.temperature),
                "strategy_type": strategy.get("overall_approach", "standard")
            })
            
            return cover_letter
            
        except Exception as e:
            raise Exception(f"Error generating cover letter: {str(e)}")

    async def refine_letter(
            self,
            cover_letter: CoverLetter,
            feedback: Dict[str, str]
        ) -> CoverLetter:
            """
            Refine the cover letter based on feedback.
            
            Args:
                cover_letter: The original cover letter
                feedback: Specific feedback for improvements
                
            Returns:
                CoverLetter: The refined cover letter
            """
            try:
                # Format letter content in a way that preserves structure but is readable
                letter_content = f"""Original letter content to refine:
                Greeting: {cover_letter.greeting}
                
                Introduction: {cover_letter.introduction.content}
                Purpose: {cover_letter.introduction.purpose}
                Key Points: {', '.join(cover_letter.introduction.key_points)}
                
                Body paragraphs:
                {chr(10).join([f'- {p.content} (Purpose: {p.purpose})' for p in cover_letter.body_paragraphs])}
                
                Closing: {cover_letter.closing.content}
                Purpose: {cover_letter.closing.purpose}
                Key Points: {', '.join(cover_letter.closing.key_points)}
                
                Signature: {cover_letter.signature}"""

                refinement_prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are revising a cover letter based on specific feedback.
                    Create an improved version that addresses the feedback while maintaining
                    the overall structure. Return the letter in valid JSON format matching
                    the original structure but with improved content."""),
                    ("human", """Here's the letter to refine:
                    {letter}
                    
                    Feedback to incorporate:
                    {feedback}
                    
                    Please return the refined letter following the exact same JSON structure
                    as the original, but with content that addresses the feedback.""")
                ])
                
                response = await self.llm.ainvoke(refinement_prompt.format_messages(
                    letter=letter_content,
                    feedback=feedback
                ))
                refined_letter = self.output_parser.parse(response.content)
                
                # Update metadata
                refined_letter.metadata.update({
                    "refined": "true",
                    "original_metadata": cover_letter.metadata
                })
                
                return refined_letter
                
            except Exception as e:
                raise Exception(f"Error refining cover letter: {str(e)}")

    def format_letter(self, cover_letter: CoverLetter, style: str = "standard") -> str:
        """
        Format the cover letter into its final form.
        
        Args:
            cover_letter: The structured cover letter content
            style: The formatting style to apply
            
        Returns:
            str: The formatted cover letter text
        """
        # Start with the greeting
        formatted = [cover_letter.greeting, ""]
        
        # Add introduction
        formatted.extend([
            cover_letter.introduction.content,
            ""
        ])
        
        # Add body paragraphs
        for paragraph in cover_letter.body_paragraphs:
            formatted.extend([paragraph.content, ""])
        
        # Add closing
        formatted.extend([
            cover_letter.closing.content,
            "",
            cover_letter.signature
        ])
        
        return "\n".join(formatted)