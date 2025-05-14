from fastapi import APIRouter

from app.api.routes import predictor
from app.api.routes import sentiment

router = APIRouter()
router.include_router(predictor.router, tags=["model"], prefix="/model")
router.include_router(sentiment.router, tags=["sentiment"], prefix="/sentiment")
