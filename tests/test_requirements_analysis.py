import json
import pytest
from unittest.mock import Mock, AsyncMock, patch

from app.agents.requirements_analysis import JobRequirements, RequirementsAnalysisAgent
class MockAIMessage:
    def __init__(self, content: str):
        self.content = content

class MockLLM:
    def __init__(self):
        self.model_name = "mock-gpt-4"
        self.temperature = 0.7

    async def ainvoke(self, messages, **kwargs):
        """Mock LLM that returns predefined responses"""
        mock_requirements = {
            "core_requirements": [
                {
                    "skill": "Python",
                    "years_experience": 5,
                    "description": "Expert level Python development"
                },
                {
                    "skill": "AWS",
                    "years_experience": 2,
                    "description": "Cloud platforms experience"
                }
            ],
            "nice_to_have": [
                {
                    "skill": "Kubernetes",
                    "description": "Container orchestration"
                }
            ],
            "culture_indicators": [
                {
                    "aspect": "Remote work",
                    "description": "Remote-first workplace"
                }
            ],
            "key_responsibilities": [
                {
                    "responsibility": "Backend Development",
                    "description": "Design scalable services"
                }
            ]
        }
        """Mock LLM that returns predefined responses"""
        mock_requirements = {
            "core_requirements": [
                {
                    "skill": "Python",
                    "years_experience": 5,
                    "description": "Expert level Python development"
                },
                {
                    "skill": "AWS", 
                    "years_experience": 2,
                    "description": "Cloud platforms experience"
                }
            ],
            "nice_to_have": [
                {
                    "skill": "Kubernetes",
                    "description": "Container orchestration"
                }
            ],
            "culture_indicators": [
                {
                    "aspect": "Remote work",
                    "description": "Remote-first workplace"
                }
            ],
            "key_responsibilities": [
                {
                    "responsibility": "Backend Development",
                    "description": "Design scalable services" 
                }
            ]
        }
        return MockAIMessage(json.dumps(mock_requirements))
        

@pytest.fixture
def mock_vector_store():
    store = Mock()
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
    with patch('app.agents.requirements_analysis.ChatOpenAI', return_value=MockLLM()):
        agent = RequirementsAnalysisAgent()
        result = await agent.analyze(sample_job_description)
        
        assert isinstance(result, JobRequirements)
        assert len(result.core_requirements) > 0
        assert len(result.nice_to_have) > 0
        assert len(result.culture_indicators) > 0
        assert len(result.key_responsibilities) > 0
        
        assert any("Python" in req.skill for req in result.core_requirements)
        assert any("Kubernetes" in skill.skill for skill in result.nice_to_have)
        assert any("remote" in indicator.description.lower() 
                  for indicator in result.culture_indicators)

@pytest.mark.asyncio
async def test_vectorize_requirements(sample_job_description, mock_vector_store):
    with patch('app.agents.requirements_analysis.ChatOpenAI', return_value=MockLLM()):
        agent = RequirementsAnalysisAgent()
        result = await agent.analyze_and_vectorize(sample_job_description, mock_vector_store)
        
        assert isinstance(result, dict)
        assert "analysis" in result
        assert "vector_ids" in result
        
        expected_categories = {
            "core_requirements",
            "nice_to_have",
            "culture_indicators",
            "key_responsibilities"
        }
        assert set(result["vector_ids"].keys()) == expected_categories
        assert mock_vector_store.add_vectors.call_count == len(expected_categories)