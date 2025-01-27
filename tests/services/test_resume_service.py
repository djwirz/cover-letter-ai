import pytest
from datetime import datetime, UTC
from unittest.mock import Mock, AsyncMock
from app.services.resume_service import ResumeService
from app.models.schemas import ResumeResponse

@pytest.mark.asyncio
async def test_store_resume(async_session):
    """Test storing a new resume."""
    service = ResumeService()
    content = "Test resume content"
    metadata = {"format": "text"}
    
    # Configure mock for empty result
    mock_result = Mock()
    mock_result.first = Mock(return_value=None)  # No existing resume
    async_session.execute.return_value = mock_result
    
    result = await service.store_resume(async_session, content, metadata)
    
    assert isinstance(result, ResumeResponse)
    assert result.content == content
    assert result.metadata == metadata
    async_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_resume(async_session):
    """Test updating an existing resume."""
    service = ResumeService()
    
    # Mock existing resume
    mock_resume = Mock()
    mock_resume.id = 1
    mock_result = Mock()
    mock_result.first = Mock(return_value=mock_resume)
    async_session.execute.return_value = mock_result
    
    result = await service.store_resume(async_session, "Updated content")
    assert result.content == "Updated content"
    async_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_active_resume(async_session):
    """Test retrieving the active resume."""
    service = ResumeService()
    
    # Test no resume exists
    mock_result = Mock()
    mock_result.first = Mock(return_value=None)
    async_session.execute.return_value = mock_result
    
    result = await service.get_active_resume(async_session)
    assert result is None
    
    # Test with resume
    mock_resume = Mock()
    mock_resume.content = "Test content"
    mock_resume.updated_at = datetime.now(UTC)
    mock_resume.metadata = {}
    
    mock_result = Mock()
    mock_result.first = Mock(return_value=mock_resume)
    async_session.execute.return_value = mock_result
    
    result = await service.get_active_resume(async_session)
    assert result is not None
    assert result.content == "Test content"