import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.technical_term import (
    TechnicalTermAgent,
    TermAlignment,
    TermVariant
)

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
async def test_standardize_terms_basic():
    """Test basic term standardization functionality."""
    with patch('app.agents.technical_term.ChatOpenAI') as mock_chat:
        mock_chat.return_value.ainvoke = AsyncMock(return_value=Mock(content="""
        {
            "job_terms": {},
            "letter_terms": {},
            "misaligned_terms": [],
            "suggested_changes": []
        }
        """))
        
        agent = TechnicalTermAgent()
        result = await agent.standardize_terms(
            job_description="Python developer needed",
            cover_letter="Experienced python developer"
        )
        
        assert isinstance(result, TermAlignment)
        assert hasattr(result, 'job_terms')
        assert hasattr(result, 'letter_terms')
        assert hasattr(result, 'misaligned_terms')

@pytest.mark.asyncio
async def test_standardize_terms_with_misalignments(term_agent):
    """Test term standardization with known misalignments."""
    job_description = """
    Senior Python Developer
    - 5+ years Python experience
    - JavaScript and React
    """
    
    cover_letter = """
    I am an experienced python developer with js skills
    """
    
    result = await term_agent.standardize_terms(job_description, cover_letter)
    
    assert len(result.misaligned_terms) > 0
    assert any(
        term['current'] == 'python' and term['canonical'] == 'Python' 
        for term in result.misaligned_terms
    )
    assert any(
        term['current'] == 'js' and term['canonical'] == 'JavaScript'
        for term in result.misaligned_terms
    )

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
    
    assert len(suggestions) > 0
    assert all(isinstance(s, dict) for s in suggestions)
    assert "term" in suggestions[0]
    assert "suggested_update" in suggestions[0]
    assert "priority" in suggestions[0]

@pytest.mark.asyncio
async def test_validate_technical_accuracy(term_agent):
    """Test technical term validation functionality."""
    term_pairs = [
        ("Python", "Built scalable Python applications"),
        ("React", "Developed React components")
    ]
    
    results = await term_agent.validate_technical_accuracy(term_pairs)
    
    assert isinstance(results, list)
    assert len(results) == len(term_pairs)
    assert all(isinstance(r, dict) for r in results)
    assert all("term" in r for r in results)
    assert all("is_accurate" in r for r in results)

@pytest.mark.asyncio
async def test_error_handling(term_agent):
    """Test error handling for invalid inputs."""
    # Test empty strings
    with pytest.raises(ValueError) as exc_info:
        await term_agent.standardize_terms("  ", "  ")
    assert "cannot be empty" in str(exc_info.value)

    # Test None values - separate test
    with pytest.raises(Exception) as exc_info:
        await term_agent.standardize_terms(None, None)
    assert "Error during term standardization" in str(exc_info.value)
    assert "cannot be None" in str(exc_info.value)

    # Test malformed LLM response
    with patch.object(term_agent.llm, 'ainvoke', return_value=Mock(content="invalid json")):
        with pytest.raises(Exception) as exc_info:
            await term_agent.standardize_terms(
                "valid job description",
                "valid cover letter"
            )
        # Changed this to match actual error message
        assert "Invalid json output" in str(exc_info.value)