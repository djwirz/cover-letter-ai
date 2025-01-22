import pytest
from unittest.mock import AsyncMock, Mock
from pydantic import ValidationError
from app.agents.skills_analysis import SkillsAnalysisAgent
from app.models.schemas import SkillsAnalysis, TechnicalSkill, SoftSkill, Achievement

@pytest.fixture
async def skills_agent():
    agent = SkillsAnalysisAgent()
    agent.llm = AsyncMock()
    agent.llm.ainvoke = AsyncMock(return_value=Mock(content="""
    {
        "technical_skills": [
            {
                "skill": "Full-stack development",
                "level": "Senior",
                "years": 5.0,
                "context": "Used in general software development tasks"
            }
        ],
        "soft_skills": [
            {
                "skill": "Leadership",
                "evidence": "Led team of 6 developers to rebuild authentication system"
            },
            {
                "skill": "Project management",
                "evidence": "Successfully managed the rebuild of an authentication system"
            }
        ],
        "achievements": [
            {
                "description": "Rebuilt authentication system",
                "metrics": "Improved performance by 40%",
                "skills_demonstrated": ["Leadership", "Project management", "Full-stack development"]
            }
        ],
        "metadata": {}
    }
    """))
    return agent

@pytest.mark.asyncio
async def test_skills_analysis_successful(skills_agent):
    resume = """
    Senior Software Engineer with 5 years of experience in full-stack development.
    Led team of 6 developers to rebuild authentication system, improving performance by 40%.
    """

    result = await skills_agent.analyze(resume)

    assert isinstance(result, SkillsAnalysis)
    assert len(result.technical_skills) > 0
    assert len(result.soft_skills) > 0
    assert len(result.achievements) > 0
    
    # Verify specific content
    assert any(
        skill.skill.lower() == "full-stack development" 
        for skill in result.technical_skills
    )
    assert any(
        skill.skill.lower() == "leadership"
        for skill in result.soft_skills
    )

@pytest.mark.asyncio
async def test_skills_analysis_short_input(skills_agent):
    """Test that short inputs are handled appropriately"""
    skills_agent.llm.ainvoke = AsyncMock(return_value=Mock(
        content="Invalid response for short input"
    ))
    
    with pytest.raises(Exception) as exc_info:
        await skills_agent.analyze("Too short")
    assert "Error analyzing skills" in str(exc_info.value)

@pytest.mark.asyncio
async def test_skills_analysis_empty_input(skills_agent):
    """Test that empty inputs are handled appropriately"""
    skills_agent.llm.ainvoke = AsyncMock(return_value=Mock(
        content="Invalid response for empty input"
    ))
    
    with pytest.raises(Exception) as exc_info:
        await skills_agent.analyze("")
    assert "Error analyzing skills" in str(exc_info.value)

@pytest.mark.asyncio
async def test_structure_analysis_validation(skills_agent):
    """Test validation of malformed analysis results"""
    skills_agent.llm.ainvoke = AsyncMock(return_value=Mock(
        content='{"technical_skills": [], "soft_skills": [], "invalid_field": []}'
    ))
    
    with pytest.raises(Exception) as exc_info:
        await skills_agent.analyze("Invalid content")
    assert "Error analyzing skills" in str(exc_info.value)