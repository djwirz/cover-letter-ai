import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.technical_term import (
    TechnicalTermAgent,
    TermAlignment,
    TermVariant
)
from langchain_community.chat_models import ChatOpenAI
from langchain_community.embeddings import OpenAIEmbeddings

@pytest.fixture
def mock_standardization_response():
    return """
    {
        "job_terms": {
            "Python": {
                "canonical": "Python",
                "variants": ["python", "py"],
                "context": "5+ years Python development experience"
            },
            "JavaScript": {
                "canonical": "JavaScript",
                "variants": ["Javascript", "js"],
                "context": "Frontend development with JavaScript"
            }
        },
        "letter_terms": {
            "python": {
                "canonical": "python",
                "variants": ["Python"],
                "context": "Experienced python developer"
            },
            "js": {
                "canonical": "js",
                "variants": ["JavaScript"],
                "context": "Built js applications"
            }
        },
        "misaligned_terms": [
            {
                "current": "python",
                "canonical": "Python"
            },
            {
                "current": "js",
                "canonical": "JavaScript"
            }
        ],
        "suggested_changes": [
            {
                "from": "python",
                "to": "Python",
                "reason": "Maintain professional capitalization"
            }
        ]
    }
    """

@pytest.fixture
def mock_llm(mock_standardization_response):
    mock = Mock()
    mock.ainvoke = AsyncMock(return_value=Mock(content=mock_standardization_response))
    return mock

@pytest.fixture
async def term_agent(mock_llm):
    with patch('app.agents.technical_term.ChatOpenAI', return_value=mock_llm):
        agent = TechnicalTermAgent()
        yield agent

@pytest.mark.asyncio
async def test_standardize_terms_basic(term_agent):
    """Test basic term standardization functionality."""
    job_description = "Senior Python Developer with 5+ years experience."
    cover_letter = "I am an experienced python developer with js skills."
    
    result = await term_agent.standardize_terms(job_description, cover_letter)
    
    assert isinstance(result, TermAlignment)
    assert len(result.misaligned_terms) > 0
    assert any(term["current"] == "python" for term in result.misaligned_terms)

@pytest.mark.asyncio
async def test_suggest_term_updates(term_agent):
    """Test generation of term update suggestions."""
    alignment = TermAlignment(
        job_terms={
            "Python": TermVariant(
                canonical="Python",
                variants=["python"],
                context="Python development"
            )
        },
        letter_terms={
            "python": TermVariant(
                canonical="python",
                variants=["Python"],
                context="python experience"
            )
        },
        misaligned_terms=[
            {"current": "python", "canonical": "Python"}
        ],
        suggested_changes=[
            {"from": "python", "to": "Python"}
        ]
    )
    
    suggestions = await term_agent.suggest_term_updates(alignment)
    
    assert isinstance(suggestions, list)
    assert len(suggestions) > 0
    assert all(isinstance(s, dict) for s in suggestions)
    assert "term" in suggestions[0]
    assert "suggested_update" in suggestions[0]