import pytest
import os
from dotenv import load_dotenv

@pytest.fixture(autouse=True)
def env_setup():
    """Automatically load environment variables for all tests"""
    load_dotenv()
    # Verify OPENAI_API_KEY is set
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not set in environment")