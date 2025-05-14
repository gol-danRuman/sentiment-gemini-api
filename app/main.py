from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routes.api import router as api_router
from app.core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION

# Database setup
from app.db.base_class import Base
from app.db.session import engine

# Create tables
# This should ideally be handled by Alembic migrations in a production scenario
Base.metadata.create_all(bind=engine)

def get_application():
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router, prefix=API_PREFIX)

    return application

app = get_application()
