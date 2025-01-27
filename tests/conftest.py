import pytest
from unittest.mock import AsyncMock, Mock
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from app.main import app
from app.services.database import Database
from app.services.vector_store import VectorService
from app.services.ai_service import ConcreteAIService, EnhancedAIService
from app.api.dependencies import (
    get_db, get_vector_service, get_ai_service, 
    get_skills_agent, get_requirements_agent, get_strategy_agent, get_generation_agent,
    get_ats_scanner_agent, get_content_validation_agent, get_technical_term_agent  # Added these
)
from unittest.mock import patch
from app.agents.generation_analysis import CoverLetterGenerationAgent, CoverLetter, CoverLetterSection
from langchain_community.chat_models import ChatOpenAI

# Test data constants
SAMPLE_RESUME = """
Senior Software Engineer with 5 years of experience in Python development.
Strong background in cloud technologies and distributed systems.
"""

SAMPLE_JOB_DESCRIPTION = """
Looking for a Senior Software Engineer with:
- 5+ years Python experience
- Experience with AWS and cloud technologies
- Knowledge of Kubernetes
"""

class MockDatabase:
    """Mock database for testing."""
    def __init__(self):
        self.execute = AsyncMock()
        # Create a mock result that returns immediately
        mock_result = Mock()
        mock_result.first = Mock(return_value=None)
        self.execute.return_value = mock_result
        self.commit = AsyncMock()
        self.rollback = AsyncMock()
        
    async def close(self):
        pass

    async def get_session(self):
        yield self

@pytest.fixture
async def mock_db() -> AsyncGenerator[Database, None]:
    yield MockDatabase()

@pytest.fixture
async def mock_vector_service() -> AsyncGenerator[VectorService, None]:
    service = Mock(spec=VectorService)
    service.process_document = AsyncMock(return_value="test_doc_id")
    service.get_relevant_context = AsyncMock(return_value=[
        ({"content": "test content", "metadata": {"id": "1"}}, 0.8)
    ])
    service.add_vectors = AsyncMock(return_value="test_vector_id")
    yield service

@pytest.fixture
def mock_ai_service():
    """Create a mock AI service with properly configured vector service."""
    # Create the mock vector service first
    mock_vector_service = Mock()
    mock_vector_service.process_document = AsyncMock(
        return_value={"id": "test_doc_id", "status": "processed"}
    )
    
    # Create the mock AI service with the spec
    mock_service = Mock(spec=ConcreteAIService)
    
    # Add the vector_service attribute
    mock_service.vector_service = mock_vector_service
    
    # Add any other needed mock methods
    mock_service.generate_cover_letter = AsyncMock(
        return_value="Generated cover letter content..."
    )
    
    return mock_service

@pytest.fixture
async def mock_skills_agent():
    agent = Mock()
    agent.analyze = AsyncMock(return_value={
        "technical_skills": [{"skill": "Python", "level": "Advanced", "years": 5}],
        "soft_skills": [{"skill": "Leadership", "evidence": "Team lead"}],
        "achievements": [],
        "metadata": {}
    })
    yield agent

@pytest.fixture
async def mock_requirements_agent():
    agent = Mock()
    agent.analyze = AsyncMock(return_value={
        "core_requirements": [{"skill": "Python", "years_experience": 5}],
        "nice_to_have": [],
        "culture_indicators": [],
        "key_responsibilities": []
    })
    yield agent

@pytest.fixture
async def mock_strategy_agent():
    agent = Mock()
    agent.develop_strategy = AsyncMock(return_value={
        "gap_analysis": {
            "missing_skills": [],
            "partial_matches": [],
            "strong_matches": []
        },
        "key_talking_points": [{
            "topic": "Python",
            "strategy": "Emphasize",
            "evidence": "Projects",
            "priority": 1
        }],
        "overall_approach": "Positive",
        "tone_recommendations": {"style": "Professional"}
    })
    yield agent

@pytest.fixture
def mock_generation_agent(mocker):
    mock = mocker.MagicMock()
    mock.generate = mocker.AsyncMock()
    mock.refine_letter = mocker.AsyncMock()
    return mock

@pytest.fixture
def test_client(
    mock_db,
    mock_vector_service,
    mock_ai_service,
    mock_skills_agent,
    mock_requirements_agent,
    mock_strategy_agent,
    mock_generation_agent,
    mock_ats_scanner_agent,  # Added this
    mock_content_validation_agent,  # Added this
    mock_technical_term_agent  # Added this
) -> Generator[TestClient, None, None]:
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_vector_service] = lambda: mock_vector_service
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_skills_agent] = lambda: mock_skills_agent
    app.dependency_overrides[get_requirements_agent] = lambda: mock_requirements_agent
    app.dependency_overrides[get_strategy_agent] = lambda: mock_strategy_agent
    app.dependency_overrides[get_generation_agent] = lambda: mock_generation_agent
    app.dependency_overrides[get_ats_scanner_agent] = lambda: mock_ats_scanner_agent  # Added this
    app.dependency_overrides[get_content_validation_agent] = lambda: mock_content_validation_agent  # Added this
    app.dependency_overrides[get_technical_term_agent] = lambda: mock_technical_term_agent  # Added this

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
async def mock_ats_scanner_agent():
    agent = Mock()
    agent.scan_letter = AsyncMock(return_value={
        "keyword_match_score": 0.85,
        "parse_confidence": 0.92,
        "key_terms_found": ["python", "aws"],
        "key_terms_missing": ["kubernetes"],
        "format_issues": [],
        "headers_analysis": {}
    })
    agent.suggest_improvements = AsyncMock(return_value=[])
    yield agent

@pytest.fixture
async def mock_content_validation_agent():
    agent = Mock()
    agent.validate_content = AsyncMock(return_value={
        "issues": [],
        "supported_claims": [],
        "requirement_coverage": {},
        "confidence_score": 0.9
    })
    agent.suggest_improvements = AsyncMock(return_value=[])
    yield agent

@pytest.fixture
async def mock_technical_term_agent():
    agent = Mock()
    agent.standardize_terms = AsyncMock(return_value={
        "job_terms": {},
        "letter_terms": {},
        "misaligned_terms": [],
        "suggested_changes": []
    })
    agent.suggest_term_updates = AsyncMock(return_value=[])
    yield agent

@pytest.fixture
async def async_session(mock_db):
    """Reuse mock_db as async_session for consistency."""
    mock_db.execute.return_value.first.return_value = None
    yield mock_db