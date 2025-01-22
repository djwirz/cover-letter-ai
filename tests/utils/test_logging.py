"""Tests for logging utilities."""
from app.utils.logging import setup_logger

def test_logger_setup():
    logger = setup_logger("test")
    assert logger.name == "test" 