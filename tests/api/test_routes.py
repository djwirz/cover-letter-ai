from datetime import UTC, datetime
import pytest
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies import (
    get_db, get_vector_service, get_ai_service,
    get_skills_agent, get_requirements_agent,
    get_strategy_agent, get_generation_agent,
    get_ats_scanner_agent, get_content_validation_agent,
    get_technical_term_agent
)
from tests.conftest import SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION
from app.agents.generation_analysis import CoverLetter, CoverLetterSection
from app.services.ai_service import ConcreteAIService
from app.services.vector_service import VectorService
from app.models.schemas import DocumentRequest  # Import your Pydantic model

pytestmark = pytest.mark.asyncio

@pytest.fixture
def ai_service(vector_service):
    return ConcreteAIService(vector_service)

@pytest.fixture
def mock_ai_service(mocker):
    """Fixture to mock AI service."""
    # Create a mock for the vector service
    mock_vector_service = mocker.Mock(spec=VectorService)
    mock_vector_service.process_document = AsyncMock(return_value={"id": "test_doc_id", "status": "processed"})
    
    # Patch the ConcreteAIService and set the vector_service attribute
    ai_service = mocker.patch('app.services.ai_service.ConcreteAIService', autospec=True)
    ai_service.return_value.vector_service = mock_vector_service  # Attach the mock vector service
    
    return ai_service

async def test_process_document(test_client, mocker):
    """Test document processing endpoint."""
    # Create mock vector service
    mock_vector_service = mocker.Mock()
    mock_vector_service.process_document = mocker.AsyncMock(
        return_value={"id": "test_doc_id", "status": "processed"}
    )
    
    # Create mock AI service
    mock_ai_service = mocker.Mock()
    mock_ai_service.vector_service = mock_vector_service
    
    # Set up dependency override
    original_get_ai_service = app.dependency_overrides.get(get_ai_service)
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service

    try:
        request_data = DocumentRequest(
            content=SAMPLE_RESUME,
            doc_type="resume",
            metadata={"user_id": "123"}
        )
        
        response = test_client.post(
            "/api/documents",
            json=request_data.model_dump()
        )
        
        # Print response for debugging
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.json() if response.status_code == 200 else response.text}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test_doc_id"
        assert data["status"] == "processed"
        
        # Verify mock was called correctly
        mock_vector_service.process_document.assert_called_once_with(
            SAMPLE_RESUME,
            "resume",
            {"user_id": "123"}
        )
    finally:
        # Restore original dependency if there was one
        if original_get_ai_service:
            app.dependency_overrides[get_ai_service] = original_get_ai_service
        else:
            del app.dependency_overrides[get_ai_service]

async def test_analyze_skills(test_client, mock_skills_agent):
    """Test skills analysis endpoint."""
    response = test_client.post(
        "/api/analyze/skills",
        json={"content": SAMPLE_RESUME}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "technical_skills" in data
    assert "soft_skills" in data
    mock_skills_agent.analyze.assert_called_once_with(SAMPLE_RESUME)

async def test_analyze_requirements(test_client, mock_requirements_agent):
    """Test requirements analysis endpoint."""
    response = test_client.post(
        "/api/analyze/requirements",
        json={"job_description": SAMPLE_JOB_DESCRIPTION}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "core_requirements" in data
    assert "nice_to_have" in data
    mock_requirements_agent.analyze.assert_called_once_with(SAMPLE_JOB_DESCRIPTION)

async def test_analyze_strategy(
    test_client, 
    mock_skills_agent,
    mock_requirements_agent,
    mock_strategy_agent
):
    """Test strategy analysis endpoint."""
    response = test_client.post(
        "/api/analyze/strategy",
        json={
            "resume_content": SAMPLE_RESUME,
            "job_description": SAMPLE_JOB_DESCRIPTION
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "gap_analysis" in data
    assert "key_talking_points" in data
    mock_strategy_agent.develop_strategy.assert_called_once()

async def test_generate_cover_letter(
    test_client,
    mock_vector_service,
    mock_ai_service,
    mock_ats_scanner_agent,
    mock_requirements_agent
):
    """Test cover letter generation endpoint."""
    # Mock the AI service
    mock_ai_service.generate_cover_letter = AsyncMock(return_value="Generated cover letter content...")
    
    # Mock the requirements analysis
    mock_requirements_agent.analyze = AsyncMock(return_value={
        "core_requirements": [{"skill": "Python", "years_experience": 5}],
        "nice_to_have": [],
        "culture_indicators": [],
        "key_responsibilities": []
    })
    
    # Update ATS scanner mock to return valid JSON
    mock_ats_scanner_agent.scan_letter = AsyncMock(return_value={
        "keyword_match_score": 0.85,
        "parse_confidence": 0.92,
        "key_terms_found": ["python", "aws"],
        "key_terms_missing": ["kubernetes"],
        "format_issues": [],
        "headers_analysis": {"has_contact_info": True}
    })
    
    # Mock vector service
    mock_vector_service.get_relevant_context = AsyncMock(return_value=[
        ({"content": "test content", "metadata": {"id": "1"}}, 0.8)
    ])
    
    response = test_client.post(
        "/api/generate",
        json={
            "job_description": SAMPLE_JOB_DESCRIPTION,
            "resume_id": "123",
            "resume_content": SAMPLE_RESUME,  # Add this field
            "preferences": {
                "tone": "professional",
                "focus": "technical"
            }
        }
    )
    
    # Add debug logging
    if response.status_code != 200:
        print(f"Error response: {response.json()}")
    
    assert response.status_code == 200
    assert "content" in response.json()

async def test_error_handling(test_client, mock_skills_agent):
    """Test error handling in endpoints."""
    mock_skills_agent.analyze = AsyncMock(side_effect=ValueError("Invalid input"))
    
    response = test_client.post(
        "/api/analyze/skills",
        json={"content": ""}
    )
    
    assert response.status_code == 500
    assert "detail" in response.json()
    mock_skills_agent.analyze.assert_called_once()

async def test_generate_cover_letter_content(
    test_client,
    mock_skills_agent,
    mock_requirements_agent,
    mock_generation_agent
):
    """Test cover letter content generation endpoint."""
    # Setup mock return value
    mock_generation_agent.generate.return_value = {
        "greeting": "Dear Hiring Manager",
        "introduction": {"content": "Test intro", "purpose": "Introduction", "key_points": []},
        "body_paragraphs": [{"content": "Test body", "purpose": "Experience", "key_points": []}],
        "closing": {"content": "Thank you", "purpose": "Close", "key_points": []},
        "signature": "Best regards",
        "metadata": {}
    }

    sample_request = {
        "skills_analysis": {
            "technical_skills": [{"skill": "Python", "level": "Expert"}]
        },
        "requirements_analysis": {
            "core_requirements": [{"skill": "Python"}]
        },
        "strategy": {
            "overall_approach": "technical focus"
        },
        "preferences": {
            "tone": "professional"
        }
    }

    response = test_client.post(
        "/api/generate/cover-letter",
        json=sample_request
    )

    # Add debug information
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert "greeting" in data
    assert "introduction" in data
    assert "body_paragraphs" in data
    mock_generation_agent.generate.assert_called_once()

async def test_refine_cover_letter(test_client, mock_generation_agent):
    """Test cover letter refinement endpoint."""
    # Setup mock return value
    mock_generation_agent.refine_letter.return_value = {
        "greeting": "Dear Hiring Manager",
        "introduction": {
            "content": "I am writing to express interest...",
            "purpose": "Introduction",
            "key_points": ["Interest"]
        },
        "body_paragraphs": [{
            "content": "My experience...",
            "purpose": "Experience",
            "key_points": ["Skills"]
        }],
        "closing": {
            "content": "Thank you...",
            "purpose": "Close",
            "key_points": ["Thanks"]
        },
        "signature": "Best regards",
        "metadata": {}
    }

    original_letter = {
        "greeting": "Dear Hiring Manager",
        "introduction": {
            "content": "I am writing to express interest...",
            "purpose": "Introduction",
            "key_points": ["Interest"]
        },
        "body_paragraphs": [{
            "content": "My experience...",
            "purpose": "Experience",
            "key_points": ["Skills"]
        }],
        "closing": {
            "content": "Thank you...",
            "purpose": "Close",
            "key_points": ["Thanks"]
        },
        "signature": "Best regards",
        "metadata": {}
    }

    feedback = {
        "tone": "Make more enthusiastic",
        "content": "Add more technical details"
    }

    response = test_client.post(
        "/api/refine/cover-letter",
        json={
            "cover_letter": original_letter,
            "feedback": feedback
        }
    )

    # Add debug information
    print(f"Response status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error response: {response.json()}")

    assert response.status_code == 200
    data = response.json()
    assert data == mock_generation_agent.refine_letter.return_value
    mock_generation_agent.refine_letter.assert_called_once()

async def test_generate_cover_letter_error_handling(test_client, mock_generation_agent):
    """Test error handling in cover letter generation."""
    mock_generation_agent.generate.side_effect = ValueError("Invalid input")
    
    response = test_client.post(
        "/api/generate/cover-letter",
        json={
            "skills_analysis": {},
            "requirements_analysis": {},
            "strategy": {}
        }
    )
    
    assert response.status_code == 500
    assert "detail" in response.json()

async def test_analyze_ats(test_client, mock_ats_scanner_agent):
    """Test ATS analysis endpoint."""
    # Mock the ATS scanner
    mock_ats_scanner_agent.scan_letter = AsyncMock(return_value={
        "keyword_match_score": 0.85,
        "parse_confidence": 0.92,
        "key_terms_found": ["python", "aws"],
        "key_terms_missing": ["kubernetes"],
        "format_issues": [],
        "headers_analysis": {}
    })
    
    request_data = {
        "cover_letter": "Sample cover letter...",
        "job_description": "Sample job description...",
        "requirements_analysis": {
            "core_requirements": [{"skill": "python", "years_experience": 5}]
        }
    }
    response = test_client.post("/api/analyze/ats", json=request_data)
    
    assert response.status_code == 200
    assert "keyword_match_score" in response.json()
    mock_ats_scanner_agent.scan_letter.assert_called_once()

async def test_validate_content(test_client, mock_content_validation_agent):
    """Test content validation endpoint."""
    # Mock the content validation agent
    mock_content_validation_agent.validate_content = AsyncMock(return_value={
        "issues": [],
        "supported_claims": [],
        "requirement_coverage": {},
        "confidence_score": 0.9
    })
    
    request_data = {
        "cover_letter": "Sample cover letter...",
        "resume": "Sample resume...",
        "job_description": "Sample job description..."
    }
    response = test_client.post("/api/validate/content", json=request_data)
    
    assert response.status_code == 200
    assert "issues" in response.json()
    mock_content_validation_agent.validate_content.assert_called_once()

async def test_standardize_terms(test_client, mock_technical_term_agent):
    """Test technical term standardization endpoint."""
    # Mock the technical term agent
    mock_technical_term_agent.standardize_terms = AsyncMock(return_value={
        "job_terms": {},
        "letter_terms": {},
        "misaligned_terms": [],
        "suggested_changes": []
    })
    
    request_data = {
        "job_description": "Senior Python Developer with 5+ years experience.",
        "cover_letter": "I am an experienced python developer with js skills."
    }
    
    # Add debug logging
    print(f"Request data: {request_data}")
    response = test_client.post("/api/standardize/terms", json=request_data)
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json()}")
    
    assert response.status_code == 200
    assert "misaligned_terms" in response.json()
    mock_technical_term_agent.standardize_terms.assert_called_once()

@pytest.fixture
def test_client(
    mock_db,
    mock_vector_service,
    mock_ai_service,
    mock_skills_agent,
    mock_requirements_agent,
    mock_strategy_agent,
    mock_generation_agent,
    mock_ats_scanner_agent,
    mock_content_validation_agent,
    mock_technical_term_agent
):
    """Create a test client with mocked dependencies."""
    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[get_vector_service] = lambda: mock_vector_service
    app.dependency_overrides[get_ai_service] = lambda: mock_ai_service
    app.dependency_overrides[get_skills_agent] = lambda: mock_skills_agent
    app.dependency_overrides[get_requirements_agent] = lambda: mock_requirements_agent
    app.dependency_overrides[get_strategy_agent] = lambda: mock_strategy_agent
    app.dependency_overrides[get_generation_agent] = lambda: mock_generation_agent
    app.dependency_overrides[get_ats_scanner_agent] = lambda: mock_ats_scanner_agent
    app.dependency_overrides[get_content_validation_agent] = lambda: mock_content_validation_agent
    app.dependency_overrides[get_technical_term_agent] = lambda: mock_technical_term_agent
    
    with TestClient(app) as client:
        yield client
        
    # Clean up overrides after test
    app.dependency_overrides.clear()

async def test_upload_resume(test_client, mock_db):
    """Test resume upload endpoint."""
    # Configure mock for no existing resume
    mock_result = Mock()
    mock_result.first = Mock(return_value=None)
    mock_db.execute.return_value = mock_result
    
    response = test_client.post(
        "/api/resume",
        json={
            "content": "Test resume content",
            "metadata": {"format": "text"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test resume content"
    assert "last_updated" in data

async def test_get_resume(test_client, mock_db):
    """Test resume retrieval endpoint."""
    # Mock resume exists
    mock_resume = Mock()
    mock_resume.content = "Test resume"
    mock_resume.updated_at = datetime.now(UTC)
    mock_resume.metadata = {}
    
    mock_result = Mock()
    mock_result.first = Mock(return_value=mock_resume)
    mock_db.execute.return_value = mock_result
    
    response = test_client.get("/api/resume")
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test resume"

async def test_get_resume_not_found(test_client, mock_db):
    """Test resume retrieval when no resume exists."""
    # Configure mock for no resume
    mock_result = Mock()
    mock_result.first = Mock(return_value=None)
    mock_db.execute.return_value = mock_result
    
    response = test_client.get("/api/resume")
    assert response.status_code == 404
