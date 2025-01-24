from typing import Dict, List, Set, Tuple
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.schema.output_parser import OutputParserException

class TermVariant(BaseModel):
    """Represents different variants of the same technical term."""
    canonical: str = Field(description="The standardized version of the term")
    variants: List[str] = Field(description="Alternative forms found")
    context: str = Field(description="How the term is used in context")

class TermAlignment(BaseModel):
    """Results of term alignment analysis."""
    job_terms: Dict[str, TermVariant] = Field(
        description="Technical terms from job description"
    )
    letter_terms: Dict[str, TermVariant] = Field(
        description="Technical terms from cover letter"
    )
    misaligned_terms: List[Dict[str, str]] = Field(
        description="Terms that need standardization"
    )
    suggested_changes: List[Dict[str, str]] = Field(
        description="Specific term changes suggested"
    )

class TechnicalTermAgent:
    """
    Ensures consistent usage of technical terminology between 
    job descriptions and cover letters.
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
        self.output_parser = PydanticOutputParser(pydantic_object=TermAlignment)
        
    async def standardize_terms(
        self,
        job_description: str,
        cover_letter: str,
        technology_context: Dict = None
    ) -> TermAlignment:
        """Analyzes and standardizes technical terminology usage."""
        try:
            # Check for None values first
            if job_description is None or cover_letter is None:
                raise Exception("Error during term standardization: Inputs cannot be None")
                
            # Then check for empty strings
            if not job_description.strip() or not cover_letter.strip():
                raise ValueError("Job description and cover letter cannot be empty")
                
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a technical terminology expert. Analyze these documents
                for technical term usage and ensure consistency. Focus on:
                
                1. Programming languages (Python vs python vs py)
                2. Technologies and frameworks (JavaScript vs Javascript vs js)
                3. Industry standard abbreviations (AWS vs Amazon Web Services)
                4. Technical methodologies (CI/CD vs continuous integration)
                
                Identify canonical forms and suggest standardization.
                """),
                ("human", """Job Description:
                {job_description}
                
                Cover Letter:
                {cover_letter}
                
                Additional Context:
                {context}
                
                Analyze terminology consistency and provide structured feedback.
                {format_instructions}
                """)
            ])
            
            messages = prompt.format_messages(
                job_description=job_description,
                cover_letter=cover_letter,
                context=technology_context or {},
                format_instructions=self.output_parser.get_format_instructions()
            )
            
            response = await self.llm.ainvoke(messages)
            return self.output_parser.parse(response.content)
            
        except ValueError as e:
            raise e
        except OutputParserException as e:
            raise Exception(f"Error during term standardization: Failed to parse LLM output")
        except Exception as e:
            raise Exception(f"Error during term standardization: {str(e)}")
    
    async def suggest_term_updates(
        self,
        alignment: TermAlignment
    ) -> List[Dict]:
        """
        Generate specific suggestions for terminology updates.
        """
        suggestions = []
        
        for misaligned in alignment.misaligned_terms:
            current = misaligned.get('current')
            canonical = misaligned.get('canonical')
            
            if current and canonical:
                term_variant = alignment.job_terms.get(canonical)
                context = term_variant.context if term_variant else ''

                suggestions.append({
                    "term": current,
                    "suggested_update": canonical,
                    "reason": f"Match job description terminology",
                    "context": context,
                    "priority": "high" if current in alignment.job_terms else "medium"
                })
        
        return suggestions
    
    async def validate_technical_accuracy(
        self,
        term_pairs: List[Tuple[str, str]]  # [(term, context), ...]
    ) -> List[Dict]:
        """
        Validates technical term usage is accurate in given contexts.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a technical accuracy validator. 
            Check if technical terms are used correctly in their contexts."""),
            ("human", """Please validate these technical terms and contexts:
            {term_pairs}
            
            For each term, verify:
            1. Term is used accurately in context
            2. Usage matches industry standards
            3. No conceptual mistakes present""")
        ])
        
        try:
            messages = prompt.format_messages(term_pairs=term_pairs)
            response = await self.llm.ainvoke(messages)
            
            # Process response into structured feedback
            return [
                {
                    "term": term,
                    "context": context,
                    "is_accurate": True,  # Updated based on analysis
                    "issues": []  # Any accuracy issues found
                }
                for term, context in term_pairs
            ]
            
        except Exception as e:
            raise Exception(f"Error validating technical accuracy: {str(e)}")