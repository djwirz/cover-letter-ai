import pytest
from unittest.mock import AsyncMock
from tests.conftest import SAMPLE_RESUME, SAMPLE_JOB_DESCRIPTION
from app.agents.generation_analysis import CoverLetter, CoverLetterSection

pytestmark = pytest.mark.asyncio

async def test_process_document(test_client, mock_vector_service):
    """Test document processing endpoint."""
    response = test_client.post(
        "/api/documents",
        json={
            "content": SAMPLE_RESUME,
            "doc_type": "resume",
            "metadata": {"user_id": "123"}
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test_doc_id"
    assert data["status"] == "processed"
    mock_vector_service.process_document.assert_called_once()

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

async def test_generate_cover_letter(test_client, mock_vector_service, mock_ai_service):
    """Test cover letter generation endpoint."""
    response = test_client.post(
        "/api/generate",
        json={
            "job_description": SAMPLE_JOB_DESCRIPTION,
            "resume_id": "123",
            "preferences": {
                "tone": "professional",
                "focus": "technical"
            }
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "metadata" in data
    assert "similar_documents" in data
    mock_ai_service.generate_cover_letter.assert_called_once()

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