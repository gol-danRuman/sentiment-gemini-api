from pydantic import BaseModel

class SentimentRequest(BaseModel):
    text: str

class SentimentResponse(BaseModel):
    text: str
    sentiment: str # e.g., Positive, Negative, Neutral
    score: float | None = None # Optional: confidence score from the model 