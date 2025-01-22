import pytest
from unittest.mock import AsyncMock, Mock
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Database
from app.core.vector_store import VectorService
from app.core.ai_service import EnhancedAIService
from app.api.dependencies import (
    get_db, get_vector_service, get_ai_service, 
    get_skills_agent, get_requirements_agent, get_strategy_agent, get_generation_agent
)
from unittest.mock import patch
from app.agents.generation_analysis import CoverLetterGenerationAgent, CoverLetter, CoverLetterSection

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
    async def close(self):
        pass

    @property
    def client(self):
        return Mock()

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
async def mock_ai_service() -> AsyncGenerator[EnhancedAIService, None]:
    service = Mock(spec=EnhancedAIService)
    service.generate_cover_letter = AsyncMock(return_value="Generated cover letter content...")
    yield service

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
    mock_generation_agent
) -> Generator[TestClient, None, None]:
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_vector_service] = lambda: mock_vector_service
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_skills_agent] = lambda: mock_skills_agent
    app.dependency_overrides[get_requirements_agent] = lambda: mock_requirements_agent
    app.dependency_overrides[get_strategy_agent] = lambda: mock_strategy_agent
    app.dependency_overrides[get_generation_agent] = lambda: mock_generation_agent

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()