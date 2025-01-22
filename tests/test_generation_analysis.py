import pytest
from unittest.mock import AsyncMock, Mock, patch
from pydantic import BaseModel
from app.agents.generation_analysis import (
    CoverLetterGenerationAgent,
    CoverLetter,
    CoverLetterSection
)

@pytest.fixture
def sample_skills_analysis():
    return {
        "technical_skills": [
            {
                "skill": "Python",
                "level": "Advanced",
                "years": 5,
                "context": "Full-stack development"
            }
        ],
        "soft_skills": [
            {
                "skill": "Leadership",
                "evidence": "Led team of 6 developers"
            }
        ],
        "achievements": [
            {
                "description": "Improved system performance by 40%",
                "metrics": "40% speedup",
                "skills_demonstrated": ["Python", "Optimization"]
            }
        ]
    }

@pytest.fixture
def sample_requirements_analysis():
    return {
        "core_requirements": [
            {
                "skill": "Python",
                "years_experience": 5,
                "description": "Expert-level Python development"
            }
        ],
        "nice_to_have": [
            {
                "skill": "AWS",
                "description": "Cloud infrastructure experience"
            }
        ],
        "culture_indicators": [
            {
                "aspect": "Team-oriented",
                "description": "Strong collaborative environment"
            }
        ],
        "key_responsibilities": [
            {
                "responsibility": "Backend Development",
                "description": "Design and implement scalable services"
            }
        ]
    }

@pytest.fixture
def sample_strategy():
    return {
        "gap_analysis": {
            "missing_skills": [],
            "partial_matches": [],
            "strong_matches": [
                {
                    "skill": "Python",
                    "candidate_experience": 5,
                    "required_experience": 5
                }
            ]
        },
        "key_talking_points": [
            {
                "topic": "Python Expertise",
                "strategy": "Emphasize full-stack experience",
                "evidence": "Performance improvements",
                "priority": 1
            }
        ],
        "overall_approach": "Highlight technical expertise",
        "tone_recommendations": {
            "style": "Professional and confident"
        }
    }

class MockAIMessage:
    def __init__(self, content: str):
        self.content = content

class MockChatOpenAI:
    def __init__(self):
        self.model_name = "mock-gpt-4"
        self.temperature = 0.7

    async def ainvoke(self, messages, **kwargs):
        # Check if this is a refinement request by looking at the system message
        is_refinement = any("revising a cover letter" in msg.content.lower() for msg in messages)
        
        if is_refinement:
            # Return modified content for refinement
            return MockAIMessage("""
            {
                "greeting": "Dear Hiring Manager",
                "introduction": {
                    "content": "I am thrilled to submit my application for consideration...",
                    "purpose": "Create compelling opening",
                    "key_points": ["Enthusiasm", "Technical background"]
                },
                "body_paragraphs": [{
                    "content": "Throughout my career spanning 5 years of Python development...",
                    "purpose": "Highlight expertise",
                    "key_points": ["Technical depth", "Achievement focus"]
                }],
                "closing": {
                    "content": "I am excited about the opportunity to contribute...",
                    "purpose": "Strong finish",
                    "key_points": ["Enthusiasm", "Call to action"]
                },
                "signature": "Best regards,\\nJohn Doe",
                "metadata": {"generation_type": "refined"}
            }
            """)
        else:
            # Return original content for generation
            return MockAIMessage("""
            {
                "greeting": "Dear Hiring Manager",
                "introduction": {
                    "content": "I am writing to express my interest...",
                    "purpose": "Hook the reader",
                    "key_points": ["Technical expertise", "Relevant experience"]
                },
                "body_paragraphs": [{
                    "content": "With 5 years of Python experience...",
                    "purpose": "Demonstrate technical fit",
                    "key_points": ["Python expertise", "Performance optimization"]
                }],
                "closing": {
                    "content": "Thank you for considering my application...",
                    "purpose": "Express enthusiasm",
                    "key_points": ["Enthusiasm", "Follow-up"]
                },
                "signature": "Best regards,\\nJohn Doe",
                "metadata": {"generation_type": "standard"}
            }
            """)

@pytest.mark.asyncio
async def test_generate_cover_letter(
    sample_skills_analysis,
    sample_requirements_analysis,
    sample_strategy
):
    """Test basic cover letter generation."""
    with patch('app.agents.generation_analysis.ChatOpenAI', return_value=MockChatOpenAI()):
        agent = CoverLetterGenerationAgent()
        result = await agent.generate(
            sample_skills_analysis,
            sample_requirements_analysis,
            sample_strategy
        )

        assert isinstance(result, CoverLetter)
        assert result.greeting.startswith("Dear")
        assert len(result.body_paragraphs) > 0
        assert "Python" in result.body_paragraphs[0].content
        assert result.metadata.get("model") == "mock-gpt-4"

@pytest.mark.asyncio
async def test_refine_letter():
    """Test letter refinement functionality."""
    original_letter = CoverLetter(
        greeting="Dear Hiring Manager",
        introduction=CoverLetterSection(
            content="I am writing to express my interest...",
            purpose="Initial greeting",
            key_points=["Introduction"]
        ),
        body_paragraphs=[
            CoverLetterSection(
                content="Original content...",
                purpose="Original purpose",
                key_points=["Original point"]
            )
        ],
        closing=CoverLetterSection(
            content="Thank you...",
            purpose="Close",
            key_points=["Thanks"]
        ),
        signature="Best,\nJohn",
        metadata={}
    )

    with patch('app.agents.generation_analysis.ChatOpenAI', return_value=MockChatOpenAI()):
        agent = CoverLetterGenerationAgent()
        feedback = {
            "tone": "More enthusiasm",
            "content": "Emphasize technical excellence"
        }

        refined = await agent.refine_letter(original_letter, feedback)
        
        assert isinstance(refined, CoverLetter)
        assert refined.metadata.get("refined") == "true"
        assert refined.introduction.content != original_letter.introduction.content

@pytest.mark.asyncio
async def test_empty_input_handling():
    """Test handling of empty inputs."""
    with patch('app.agents.generation_analysis.ChatOpenAI', return_value=MockChatOpenAI()):
        agent = CoverLetterGenerationAgent()
        
        with pytest.raises(Exception) as exc_info:
            await agent.generate({}, {}, {})
        assert "Error generating cover letter" in str(exc_info.value)

@pytest.mark.asyncio
async def test_invalid_preferences_handling(
    sample_skills_analysis,
    sample_requirements_analysis,
    sample_strategy
):
    """Test handling of invalid preferences."""
    with patch('app.agents.generation_analysis.ChatOpenAI', return_value=MockChatOpenAI()):
        agent = CoverLetterGenerationAgent()
        
        # Should not raise an exception with None preferences
        result = await agent.generate(
            sample_skills_analysis,
            sample_requirements_analysis,
            sample_strategy,
            None
        )
        assert isinstance(result, CoverLetter)

        # Should handle empty preferences
        result = await agent.generate(
            sample_skills_analysis,
            sample_requirements_analysis,
            sample_strategy,
            {}
        )
        assert isinstance(result, CoverLetter)