import json
import pytest
from unittest.mock import Mock, patch, AsyncMock

from app.agents.strategy_analysis import (
    CoverLetterStrategyAgent,
    CoverLetterStrategy
)


class MockLLM:
    async def ainvoke(self, messages):
        """Mock LLM invocation with a properly formatted JSON response"""
        mock_strategy = {
            "gap_analysis": {
                "missing_skills": [
                    {"skill": "Kubernetes", "description": "Container orchestration"}
                ],
                "partial_matches": [
                    {"skill": "Python", "gap": 2}
                ],
                "strong_matches": [
                    {"skill": "AWS", "candidate_experience": 2, "required_experience": 2} 
                ]
            },
            "key_talking_points": [
                {
                    "topic": "Python Experience",
                    "strategy": "Emphasize rapid learning",
                    "evidence": "Built complex systems",
                    "priority": 1
                }
            ],
            "overall_approach": "Focus on fast learning ability",
            "tone_recommendations": {
                "style": "confident but humble"
            }
        }
        
        return Mock(content=json.dumps(mock_strategy))


@pytest.fixture
def sample_skills_analysis():
    return {
        'soft_skills': [
            {'description': 'Led 5-person team', 'skill': 'Team Leadership', 'years_experience': 2}
        ],
        'technical_skills': [
            {'description': 'Backend development', 'skill': 'Python', 'years_experience': 3},
            {'description': 'Cloud infrastructure', 'skill': 'AWS', 'years_experience': 2}
        ]
    }


@pytest.fixture
def sample_requirements_analysis():
    return {
        'core_requirements': [
            {'description': 'Expert level Python development', 'skill': 'Python', 'years_experience': 5},
            {'description': 'Cloud platforms', 'skill': 'AWS', 'years_experience': 2}
        ],
        'nice_to_have': [
            {'description': 'Experience with ML frameworks', 'skill': 'Machine Learning'},
            {'description': 'Container orchestration', 'skill': 'Kubernetes'}
        ]
    }


@pytest.fixture
def mock_vector_store():
    store = Mock()
    store.similarity_search = AsyncMock(return_value=[
        {"content": "Sample cover letter 1", "metadata": {"score": 0.8}},
        {"content": "Sample cover letter 2", "metadata": {"score": 0.7}}
    ])
    store.add_vectors = AsyncMock(return_value="test_vector_id")
    return store


@pytest.mark.asyncio 
async def test_analyze_skill_gaps(
    sample_skills_analysis,
    sample_requirements_analysis
):
    agent = CoverLetterStrategyAgent(vector_store=Mock())
    result = await agent.analyze_skill_gaps(
        sample_skills_analysis,
        sample_requirements_analysis
    )
    
    # Validate gap analysis structure
    assert result.missing_skills is not None
    assert result.partial_matches is not None
    assert result.strong_matches is not None


@pytest.mark.asyncio
async def test_find_similar_letters(
    sample_requirements_analysis,
    mock_vector_store
):
    agent = CoverLetterStrategyAgent(vector_store=mock_vector_store)
    similar_letters = await agent.find_similar_letters(sample_requirements_analysis)
    
    # Verify mock vector store was called correctly
    mock_vector_store.similarity_search.assert_called_once()
    assert len(similar_letters) == 2
    assert all(letter.get('metadata', {}).get('score') for letter in similar_letters)


@pytest.mark.asyncio
async def test_develop_strategy(
    sample_skills_analysis,
    sample_requirements_analysis,
    mock_vector_store
):
    with patch('app.agents.strategy_analysis.ChatOpenAI', return_value=MockLLM()):
        agent = CoverLetterStrategyAgent(vector_store=mock_vector_store)
        strategy = await agent.develop_strategy(
            sample_skills_analysis,
            sample_requirements_analysis
        )
        
        assert isinstance(strategy, CoverLetterStrategy)
        assert strategy.overall_approach is not None
        assert strategy.tone_recommendations is not None
        assert strategy.gap_analysis is not None


@pytest.mark.asyncio
async def test_get_strategy_vectors():
    strategy = CoverLetterStrategy(
        gap_analysis={
            "missing_skills": [],
            "partial_matches": [],
            "strong_matches": []
        },
        key_talking_points=[
            {
                "topic": "Python",
                "strategy": "Emphasize experience",
                "evidence": "Built complex systems",
                "priority": 1
            }
        ],
        overall_approach="Technical focus",
        tone_recommendations={"style": "professional"}
    )
    
    mock_store = Mock()
    mock_store.add_vectors = AsyncMock(return_value="test_vector_id")
    agent = CoverLetterStrategyAgent(vector_store=mock_store)
    vectors = await agent.get_strategy_vectors(strategy)
    
    assert isinstance(vectors, dict)
    assert "gap_analysis" in vectors
    assert "talking_points" in vectors
    assert "approach" in vectors

