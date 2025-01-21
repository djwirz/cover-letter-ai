from pydantic import ValidationError
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agents.skills_analysis import SkillsAnalysisAgent
from datetime import datetime, UTC

@pytest.fixture
def mock_structured_analysis():
    return {
        "technical_skills": [
            {
                "skill": "Python",
                "level": "Advanced",
                "years": 5,
                "context": "Professional development experience"
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
                "description": "Authentication System Improvement",
                "metrics": "40% performance improvement",
                "skills_demonstrated": ["Leadership"]
            }
        ],
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "version": "1.0"
        }
    }

@pytest.fixture
def skills_agent(mock_structured_analysis):
    with patch('langchain_openai.ChatOpenAI'):
        agent = SkillsAnalysisAgent()
        # Mock the agent executor
        agent.agent_executor = MagicMock()
        agent.agent_executor.ainvoke = AsyncMock(return_value={"output": "mocked output"})
        # Mock the structure analysis method
        agent._structure_analysis = AsyncMock(return_value=mock_structured_analysis)
        return agent

@pytest.mark.asyncio
async def test_skills_analysis_successful(skills_agent, mock_structured_analysis):
    resume = """
    Senior Software Engineer with 5 years of experience in full-stack development. 
    Led team of 6 developers to rebuild authentication system, improving performance by 40%. 
    """
    
    result = await skills_agent.analyze(resume)
    
    assert result is not None
    assert "skills_analysis" in result
    assert "metadata" in result
    
    # Verify the agent was called with correct input
    skills_agent.agent_executor.ainvoke.assert_called_once()
    
    # Check actual response content
    analysis = result["skills_analysis"]
    assert len(analysis["technical_skills"]) > 0
    assert len(analysis["soft_skills"]) > 0
    assert len(analysis["achievements"]) > 0
    
    # Verify specific content
    tech_skill = analysis["technical_skills"][0]
    assert tech_skill["skill"] == "Python"
    assert tech_skill["level"] == "Advanced"

@pytest.mark.asyncio
async def test_skills_analysis_short_input(skills_agent):
    """Test that short inputs are rejected"""
    with pytest.raises(ValueError, match="Resume text too short or empty"):
        await skills_agent.analyze("Too short")

@pytest.mark.asyncio
async def test_skills_analysis_empty_input(skills_agent):
    """Test that empty inputs are rejected"""
    with pytest.raises(ValueError, match="Resume text too short or empty"):
        await skills_agent.analyze("")

@pytest.mark.asyncio
async def test_structure_analysis_failure(skills_agent):
    """Test handling of structure analysis failures"""
    skills_agent._structure_analysis = AsyncMock(return_value={})
    
    with pytest.raises(ValidationError):
        await skills_agent.analyze(
            "Senior Software Engineer with 5 years of experience..."
        )