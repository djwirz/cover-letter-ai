import json
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.strategy_analysis import (
    CoverLetterStrategyAgent,
    CoverLetterStrategy,
    SkillGapAnalysis,
    SkillRequirement,
    SkillMatch,
    SkillGap,
    TalkingPoint
)

# Add new MockAIMessage and MockLLM classes
class MockAIMessage:
    def __init__(self, content: str):
        self.content = content

class MockLLM:
    def __init__(self):
        self.model_name = "mock-gpt-4"
        self.temperature = 0.7

    async def ainvoke(self, messages, **kwargs):
        """Mock LLM that returns predefined responses"""
        mock_strategy = {
            "gap_analysis": {
                "missing_skills": [
                    {
                        "skill": "Kubernetes",
                        "description": "Container orchestration",
                        "years_experience": 2
                    }
                ],
                "partial_matches": [
                    {
                        "skill": "Python",
                        "gap": 2
                    }
                ],
                "strong_matches": [
                    {
                        "skill": "AWS",
                        "candidate_experience": 2,
                        "required_experience": 2
                    }
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
            "tone_recommendations": {"style": "confident but humble"}
        }
        """Mock LLM that returns predefined responses"""
        mock_strategy = {
            "gap_analysis": {
                "missing_skills": [
                    {
                        "skill": "Kubernetes",
                        "description": "Container orchestration",
                        "years_experience": 2
                    }
                ],
                "partial_matches": [
                    {
                        "skill": "Python",
                        "gap": 2
                    }
                ],
                "strong_matches": [
                    {
                        "skill": "AWS",
                        "candidate_experience": 2,
                        "required_experience": 2
                    }
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
            "tone_recommendations": {"style": "confident but humble"}
        }
        return MockAIMessage(json.dumps(mock_strategy))



@pytest.fixture
def mock_vector_store():
    store = Mock()
    store.similarity_search = AsyncMock(return_value=[
        {
            "content": "Previous successful cover letter...",
            "metadata": {"type": "cover_letter"}
        }
    ])
    store.add_vectors = AsyncMock(return_value="test_vector_id")
    return store



@pytest.fixture
def sample_skills_analysis():
    return {
        "technical_skills": [
            {
                "skill": "Python",
                "years_experience": 3,
                "description": "Advanced Python development"
            },
            {
                "skill": "AWS",
                "years_experience": 2,
                "description": "Cloud infrastructure"
            }
        ],
        "soft_skills": [
            {
                "skill": "Team Leadership",
                "years_experience": 2,
                "description": "Led 5-person team"
            },
            {
                "skill": "Communication",
                "years_experience": 5,
                "description": "Strong written and verbal"
            }
        ]
    }



@pytest.fixture
def sample_requirements_analysis():
    return {
        "core_requirements": [
            {
                "skill": "Python",
                "years_experience": 5,
                "description": "Expert level Python development"
            },
            {
                "skill": "Kubernetes",
                "years_experience": 2,
                "description": "Container orchestration"
            },
            {
                "skill": "AWS",
                "years_experience": 2,
                "description": "Cloud infrastructure"
            }
        ],
        "nice_to_have": [
            {
                "skill": "Machine Learning",
                "description": "Experience with ML frameworks"
            }
        ]
    }



@pytest.mark.asyncio
async def test_analyze_skill_gaps(
    sample_skills_analysis,
    sample_requirements_analysis
):
    with patch('app.agents.strategy_analysis.ChatOpenAI', return_value=MockLLM()):
        agent = CoverLetterStrategyAgent()
        gap_analysis = await agent.analyze_skill_gaps(
            sample_skills_analysis,
            sample_requirements_analysis
        )
        
        assert isinstance(gap_analysis, SkillGapAnalysis)
        # Check missing skills
        assert len(gap_analysis.missing_skills) == 1
        kubernetes = gap_analysis.missing_skills[0]
        assert isinstance(kubernetes, SkillRequirement)
        assert kubernetes.skill.lower() == "kubernetes"
        assert kubernetes.years_experience == 2
        
        # Check partial matches
        assert len(gap_analysis.partial_matches) == 1
        python_gap = gap_analysis.partial_matches[0]
        assert isinstance(python_gap, SkillGap)
        assert python_gap.skill.lower() == "python"
        assert python_gap.gap == 2  # Required 5 years, has 3 years
        
        # Check strong matches
        assert len(gap_analysis.strong_matches) == 1
        aws_match = gap_analysis.strong_matches[0]
        assert isinstance(aws_match, SkillMatch)
        assert aws_match.skill.lower() == "aws"
        assert aws_match.required_experience == 2
        assert aws_match.candidate_experience == 2



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
        
        # Verify strategy structure
        assert isinstance(strategy, CoverLetterStrategy)
        assert isinstance(strategy.gap_analysis, SkillGapAnalysis)
        assert len(strategy.key_talking_points) > 0
        assert strategy.overall_approach
        assert strategy.tone_recommendations
        
        # Verify gap analysis detail
        gap_analysis = strategy.gap_analysis
        assert any(
            skill.skill.lower() == "kubernetes"
            for skill in gap_analysis.missing_skills
        )
        assert any(
            gap.skill.lower() == "python" and gap.gap == 2
            for gap in gap_analysis.partial_matches
        )
        assert any(
            match.skill.lower() == "aws"
            for match in gap_analysis.strong_matches
        )
        
        # Verify talking points structure
        for point in strategy.key_talking_points:
            assert isinstance(point, TalkingPoint)
            assert 1 <= point.priority <= 5
            assert point.topic
            assert point.strategy
            assert point.evidence



@pytest.mark.asyncio
async def test_find_similar_letters(mock_vector_store):
    agent = CoverLetterStrategyAgent(vector_store=mock_vector_store)
    similar_letters = await agent.find_similar_letters({
        "core_requirements": [
            {
                "skill": "Python",
                "description": "Expert level"
            }
        ]
    })
    
    assert len(similar_letters) > 0
    assert mock_vector_store.similarity_search.called
    
    call_kwargs = mock_vector_store.similarity_search.call_args[1]
    assert call_kwargs["metadata_filter"]["type"] == "cover_letter"



@pytest.mark.asyncio
async def test_get_strategy_vectors(mock_vector_store):
    agent = CoverLetterStrategyAgent(vector_store=mock_vector_store)
    
    # Create test strategy
    strategy = CoverLetterStrategy(
        gap_analysis=SkillGapAnalysis(
            missing_skills=[
                SkillRequirement(
                    skill="Kubernetes",
                    description="Container orchestration",
                    years_experience=2
                )
            ],
            partial_matches=[
                SkillGap(
                    skill="Python",
                    gap=2
                )
            ],
            strong_matches=[
                SkillMatch(
                    skill="AWS",
                    candidate_experience=2,
                    required_experience=2
                )
            ]
        ),
        key_talking_points=[
            TalkingPoint(
                topic="Python Experience",
                strategy="Emphasize rapid learning",
                evidence="Built complex systems",
                priority=1
            )
        ],
        overall_approach="Focus on fast learning ability",
        tone_recommendations={"style": "confident but humble"}
    )
    
    vector_ids = await agent.get_strategy_vectors(strategy)
    
    assert set(vector_ids.keys()) == {
        "gap_analysis",
        "talking_points",
        "approach"
    }
    assert mock_vector_store.add_vectors.call_count == 3

    # Verify metadata in vector store calls
    for call_args in mock_vector_store.add_vectors.call_args_list:
        kwargs = call_args[1]
        assert kwargs["metadata"]["type"] == "cover_letter_strategy"
        assert "category" in kwargs["metadata"]
