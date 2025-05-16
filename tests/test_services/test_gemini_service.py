import pytest
from unittest.mock import AsyncMock, patch

from app.services.gemini_service import get_sentiment_from_gemini

@pytest.mark.asyncio
async def test_get_sentiment_positive():
    """Test sentiment analysis with a positive response."""
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Positive
    SCORE: 0.95
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        sentiment, score = await get_sentiment_from_gemini("I love this!")
        assert sentiment == "Positive"
        assert score == 0.95

@pytest.mark.asyncio
async def test_get_sentiment_negative():
    """Test sentiment analysis with a negative response."""
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Negative
    SCORE: 0.85
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        sentiment, score = await get_sentiment_from_gemini("I hate this!")
        assert sentiment == "Negative"
        assert score == 0.85

@pytest.mark.asyncio
async def test_get_sentiment_neutral():
    """Test sentiment analysis with a neutral response."""
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Neutral
    SCORE: 0.5
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        sentiment, score = await get_sentiment_from_gemini("This is a fact.")
        assert sentiment == "Neutral"
        assert score == 0.5

@pytest.mark.asyncio
async def test_get_sentiment_no_score():
    """Test sentiment analysis with a response that doesn't include a score."""
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Positive
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        sentiment, score = await get_sentiment_from_gemini("This is good.")
        assert sentiment == "Positive"
        assert score is None

@pytest.mark.asyncio
async def test_get_sentiment_invalid_score():
    """Test sentiment analysis with an invalid score format."""
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Positive
    SCORE: invalid
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        sentiment, score = await get_sentiment_from_gemini("This is good.")
        assert sentiment == "Positive"
        assert score is None

@pytest.mark.asyncio
async def test_get_sentiment_api_error():
    """Test sentiment analysis when the API call fails."""
    with patch('app.services.gemini_service.model.generate_content_async', side_effect=Exception("API Error")):
        sentiment, score = await get_sentiment_from_gemini("This is a test.")
        assert sentiment == "Error"
        assert score is None

@pytest.mark.asyncio
async def test_get_sentiment_missing_sentiment():
    """Test sentiment analysis with a response missing the sentiment label."""
    mock_response = AsyncMock()
    mock_response.text = """
    SCORE: 0.5
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        sentiment, score = await get_sentiment_from_gemini("This is a test.")
        assert sentiment == "Neutral"  # Default sentiment
        assert score == 0.5 