import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.content_validation import (
    ContentValidationAgent,
    ValidationResult,
    ValidationIssue
)

@pytest.fixture
def mock_validation_response():
    return """
    {
        "issues": [
            {
                "type": "unsupported_claim",
                "severity": "high",
                "location": "paragraph 2",
                "description": "Claims of leadership not supported by resume",
                "suggestion": "Rephrase to match documented experience"
            }
        ],
        "supported_claims": [
            {
                "claim": "Python development experience",
                "evidence": "5 years Python development listed in resume"
            }
        ],
        "requirement_coverage": {
            "python_experience": true,
            "leadership": false
        },
        "confidence_score": 0.85
    }
    """

@pytest.fixture
def mock_llm(mock_validation_response):
    mock = Mock()
    mock.ainvoke = AsyncMock(return_value=Mock(content=mock_validation_response))
    return mock

@pytest.fixture
async def validation_agent(mock_llm):
    with patch('app.agents.content_validation.ChatOpenAI', return_value=mock_llm):
        agent = ContentValidationAgent()
        yield agent

@pytest.mark.asyncio
async def test_validate_content_basic(validation_agent):
    """Test basic content validation functionality."""
    result = await validation_agent.validate_content(
        cover_letter="I have led multiple teams...",
        resume="Python developer with 5 years experience...",
        job_description="Looking for a senior developer..."
    )
    
    assert isinstance(result, ValidationResult)
    assert len(result.issues) > 0
    assert 0 <= result.confidence_score <= 1
    assert result.requirement_coverage

@pytest.mark.asyncio
async def test_validate_content_empty_inputs(validation_agent):
    """Test validation with empty inputs."""
    with pytest.raises(ValueError) as exc_info:
        await validation_agent.validate_content("", "", "")
    assert "required" in str(exc_info.value)

@pytest.mark.asyncio
async def test_suggest_improvements(validation_agent):
    """Test improvement suggestion generation."""
    validation_result = ValidationResult(
        issues=[
            ValidationIssue(
                type="unsupported_claim",
                severity="high",
                location="paragraph 2",
                description="Unsupported leadership claim",
                suggestion="Rephrase to match experience"
            )
        ],
        supported_claims=[],
        requirement_coverage={},
        confidence_score=0.8
    )
    
    suggestions = await validation_agent.suggest_improvements(validation_result)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(s, dict) for s in suggestions)
    assert "suggestion" in suggestions[0]
    assert "priority" in suggestions[0]

@pytest.mark.asyncio
async def test_error_handling(validation_agent):
    """Test error handling for invalid inputs."""
    # Test None values
    with pytest.raises(Exception) as exc_info:
        await validation_agent.validate_content(None, None, None)
    assert "Error during content validation" in str(exc_info.value)
    
    # Test invalid LLM response
    with patch.object(validation_agent.llm, 'ainvoke', 
                     return_value=Mock(content="invalid json")):
        with pytest.raises(Exception) as exc_info:
            await validation_agent.validate_content(
                "valid letter",
                "valid resume",
                "valid job description"
            )
        assert "Invalid json output" in str(exc_info.value)