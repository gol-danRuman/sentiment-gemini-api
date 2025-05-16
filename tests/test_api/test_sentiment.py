import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch, AsyncMock

from app.main import app
from app.db.base_class import Base
from app.db.session import get_db
from app.models.sentiment_log import SentimentLog

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the get_db dependency
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.mark.asyncio
async def test_analyze_sentiment_success():
    """Test successful sentiment analysis request."""
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Positive
    SCORE: 0.95
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        response = client.post(
            "/api/sentiment/analyze",
            json={"text": "I love this product, it's amazing!"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "sentiment" in data
        assert "score" in data
        assert data["text"] == "I love this product, it's amazing!"
        assert data["sentiment"] == "Positive"
        assert data["score"] == 0.95

def test_analyze_sentiment_empty_text():
    """Test sentiment analysis with empty text."""
    response = client.post(
        "/api/sentiment/analyze",
        json={"text": ""}
    )
    assert response.status_code == 400
    assert "Input text cannot be empty" in response.json()["detail"]

def test_analyze_sentiment_whitespace_text():
    """Test sentiment analysis with whitespace-only text."""
    response = client.post(
        "/api/sentiment/analyze",
        json={"text": "   "}
    )
    assert response.status_code == 400
    assert "Input text cannot be empty" in response.json()["detail"]

def test_analyze_sentiment_invalid_json():
    """Test sentiment analysis with invalid JSON."""
    response = client.post(
        "/api/sentiment/analyze",
        json={"invalid": "data"}
    )
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_analyze_sentiment_database_logging():
    """Test that sentiment analysis results are logged to database."""
    test_text = "This is a test for database logging"
    
    # Mock the Gemini service response
    mock_response = AsyncMock()
    mock_response.text = """
    SENTIMENT: Positive
    SCORE: 0.85
    """
    
    with patch('app.services.gemini_service.model.generate_content_async', return_value=mock_response):
        response = client.post(
            "/api/sentiment/analyze",
            json={"text": test_text}
        )
        assert response.status_code == 200
        
        # Check database
        db = TestingSessionLocal()
        log_entry = db.query(SentimentLog).filter(SentimentLog.text_input == test_text).first()
        assert log_entry is not None
        assert log_entry.text_input == test_text
        assert log_entry.sentiment_label == "Positive"
        assert log_entry.sentiment_score == 0.85
        db.close() 