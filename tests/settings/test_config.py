"""Tests for application configuration."""
from app.settings.config import Settings

def test_settings_defaults():
    settings = Settings()
    assert settings.OPENAI_MODEL == "gpt-4"
    assert settings.OPENAI_TEMPERATURE == 0.7
    assert settings.database_url == "sqlite+aiosqlite:///./test.db"
    assert settings.debug_mode is False 