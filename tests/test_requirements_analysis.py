import json
from unittest.mock import Mock, patch


class MockLLM:
    async def ainvoke(self, messages):
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
        return Mock(content=json.dumps(mock_requirements))
