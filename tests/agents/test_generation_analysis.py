from unittest.mock import Mock, patch
import json

class MockLLM:
    async def ainvoke(self, messages):
        if any("revising a cover letter" in str(m) for m in messages):
            return Mock(content=json.dumps({
                "greeting": "Dear Hiring Manager",
                "introduction": {
                    "content": "I am excited to express my strong interest...",
                    "purpose": "Hook the reader",
                    "key_points": ["Technical expertise", "Relevant experience"]
                },
                "body_paragraphs": [{
                    "content": "With extensive Python experience...",
                    "purpose": "Demonstrate technical fit",
                    "key_points": ["Python expertise", "Performance optimization"]
                }],
                "closing": {
                    "content": "Thank you for your consideration...",
                    "purpose": "Express enthusiasm",
                    "key_points": ["Enthusiasm", "Follow-up"]
                },
                "signature": "Best regards,\nJohn Doe",
                "metadata": {
                    "generation_type": "refinement",
                    "refined": "true"
                }
            }))
        else:
            return Mock(content=json.dumps({
                "greeting": "Dear Hiring Manager",
                "introduction": {
                    "content": "I am writing to express my interest...",
                    "purpose": "Initial greeting", 
                    "key_points": ["Introduction"]
                },
                "body_paragraphs": [{
                    "content": "Original content...",
                    "purpose": "Original purpose",
                    "key_points": ["Original point"]
                }],
                "closing": {
                    "content": "Thank you...",
                    "purpose": "Close",
                    "key_points": ["Thanks"]
                },
                "signature": "Best,\nJohn",
                "metadata": {}
            }))

