from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import config

DATABASE_URL = config("DATABASE_URL", default="sqlite:///./sentiment_analysis.db")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False} # check_same_thread is for SQLite only
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 