from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.sentiment import SentimentRequest, SentimentResponse
from app.services import gemini_service
from app.models.sentiment_log import SentimentLog
from app.db.session import get_db

router = APIRouter()

@router.post("/analyze", response_model=SentimentResponse, name="sentiment:analyze")
async def analyze_sentiment(
    request: SentimentRequest,
    db: Session = Depends(get_db)
):
    """
    Receives text input and returns sentiment analysis using Google Gemini.
    Logs the request and response to the database.
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        sentiment_label, sentiment_score = await gemini_service.get_sentiment_from_gemini(request.text)

        # Log to database
        log_entry = SentimentLog(
            text_input=request.text,
            sentiment_label=sentiment_label,
            sentiment_score=sentiment_score
        )
        db.add(log_entry)
        db.commit()
        # db.refresh(log_entry) # Not strictly necessary if not immediately using the generated ID/timestamp

        return SentimentResponse(
            text=request.text,
            sentiment=sentiment_label,
            score=sentiment_score
        )
    except Exception as e:
        # Log error or handle more gracefully
        # For now, re-raise as a generic server error
        # Check if it's a specific Gemini error vs. DB error for more specific feedback
        raise HTTPException(status_code=500, detail=f"Error processing sentiment analysis: {str(e)}") 