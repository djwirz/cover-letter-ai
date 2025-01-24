import pytest
from unittest.mock import Mock, AsyncMock, patch
from langchain_community.chat_models import ChatOpenAI
from app.agents.ats_scanner import ATSScannerAgent, ATSAnalysis, ATSIssue
from app.agents.base import AgentConfig

@pytest.fixture
def mock_llm():
    return Mock(ainvoke=AsyncMock(return_value=Mock(content="""
{
    "keyword_match_score": 0.85,
    "parse_confidence": 0.92,
    "key_terms_found": ["python", "aws", "leadership"],
    "key_terms_missing": ["kubernetes"],
    "format_issues": [
        {
            "type": "header_format",
            "description": "Contact information not easily parseable",
            "severity": "high",
            "suggestion": "Place contact info at top in clear format"
        }
    ],
    "headers_analysis": {
        "has_name": true,
        "has_email": true,
        "has_phone": false
    }
}
    """)))

@pytest.fixture
async def scanner_agent(mock_llm):
    with patch('app.agents.ats_scanner.ChatOpenAI', return_value=mock_llm):
        agent = ATSScannerAgent()
        yield agent

@pytest.fixture
def agent_config():
    return AgentConfig(
        model_name="gpt-4",
        temperature=0.7,
        max_tokens=1000
        # No need to pass the optional fields if not needed for tests
    )

@pytest.mark.asyncio
async def test_scan_letter(scanner_agent):
    """Test basic ATS scanning functionality."""
    cover_letter = """
Dear Hiring Manager,

I am writing to express my interest in the Python Developer position at your company.
With 5 years of experience in Python development and AWS cloud services, I believe I
would be a great fit for this role.

Best regards,
John Doe
    """
    
    job_description = """
Senior Python Developer
Required Skills:
- 5+ years Python experience
- AWS cloud services
- Kubernetes experience
- Leadership skills
    """
    
    requirements_analysis = {
        "core_requirements": [
            {"skill": "python", "years_experience": 5},
            {"skill": "aws", "years_experience": 3},
            {"skill": "kubernetes", "years_experience": 2}
        ]
    }
    
    result = await scanner_agent.scan_letter(
        cover_letter,
        job_description,
        requirements_analysis
    )
    
    assert isinstance(result, ATSAnalysis)
    assert 0 <= result.keyword_match_score <= 1
    assert 0 <= result.parse_confidence <= 1
    assert isinstance(result.key_terms_found, list)
    assert isinstance(result.key_terms_missing, list)
    assert isinstance(result.format_issues, list)
    assert all(isinstance(issue, ATSIssue) for issue in result.format_issues)

@pytest.mark.asyncio
async def test_suggest_improvements(scanner_agent):
    """Test improvement suggestions generation."""
    analysis = ATSAnalysis(
        keyword_match_score=0.85,
        parse_confidence=0.92,
        key_terms_missing=["kubernetes"],
        format_issues=[
            ATSIssue(
                type="header_format",
                description="Contact info issue",
                severity="high",
                suggestion="Fix contact format"
            )
        ],
        headers_analysis={"has_name": True}
    )
    
    requirements_analysis = {
        "core_requirements": [
            {"skill": "kubernetes", "years_experience": 2}
        ]
    }
    
    suggestions = await scanner_agent.suggest_improvements(
        analysis,
        requirements_analysis
    )
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(s, dict) for s in suggestions)
    assert any(s["type"] == "keyword_addition" for s in suggestions)