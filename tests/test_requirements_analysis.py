import pytest
from unittest.mock import Mock, AsyncMock
from app.agents.requirements_analysis import RequirementsAnalysisAgent, JobRequirements

@pytest.fixture
def mock_vector_store():
    store = Mock()
    # Use AsyncMock for the async method
    store.add_vectors = AsyncMock(return_value="test_vector_id")
    return store

@pytest.fixture
def sample_job_description():
    return """
    Senior Software Engineer
    
    We're looking for a Senior Software Engineer to join our growing team.
    
    Required Skills:
    - 5+ years experience with Python
    - Strong background in distributed systems
    - Experience with cloud platforms (AWS/GCP)
    
    Nice to Have:
    - Experience with Kubernetes
    - Knowledge of machine learning frameworks
    
    Our Culture:
    - Remote-first workplace
    - Emphasis on work-life balance
    
    Responsibilities:
    - Design and implement scalable backend services
    - Mentor junior developers
    - Participate in technical planning
    """

@pytest.mark.asyncio
async def test_requirements_analysis(sample_job_description):
    agent = RequirementsAnalysisAgent()
    result = await agent.analyze(sample_job_description)
    
    assert isinstance(result, JobRequirements)
    assert len(result.core_requirements) > 0
    assert len(result.nice_to_have) > 0
    assert len(result.culture_indicators) > 0
    assert len(result.key_responsibilities) > 0
    
    # Check specific content - using dot notation for Pydantic models
    assert any("Python" in req.skill for req in result.core_requirements)
    assert any("Kubernetes" in skill.skill for skill in result.nice_to_have)
    assert any("remote" in indicator.description.lower() 
              for indicator in result.culture_indicators)

@pytest.mark.asyncio
async def test_vectorize_requirements(sample_job_description, mock_vector_store):
    agent = RequirementsAnalysisAgent()
    result = await agent.analyze_and_vectorize(sample_job_description, mock_vector_store)
    
    # Verify result structure
    assert isinstance(result, dict)
    assert "analysis" in result
    assert "vector_ids" in result
    
    # Check analysis contains all required fields
    analysis = result["analysis"]
    assert "core_requirements" in analysis
    assert "nice_to_have" in analysis
    assert "culture_indicators" in analysis
    assert "key_responsibilities" in analysis
    
    # Verify vector IDs for all categories
    expected_categories = {
        "core_requirements", 
        "nice_to_have", 
        "culture_indicators", 
        "key_responsibilities"
    }
    assert set(result["vector_ids"].keys()) == expected_categories
    
    # Verify vector store interactions
    assert mock_vector_store.add_vectors.call_count == len(expected_categories)
    
    # Verify each vector store call had the correct metadata
    for call_args in mock_vector_store.add_vectors.call_args_list:
        kwargs = call_args[1]  # Get keyword arguments
        assert "metadata" in kwargs
        metadata = kwargs["metadata"]
        assert metadata["type"] == "job_requirement"
        assert metadata["category"] in expected_categories