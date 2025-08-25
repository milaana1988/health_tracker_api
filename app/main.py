from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # For SQLite demo: create tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Health Tracker API", version="1.0.0", lifespan=lifespan)
app.include_router(api_router)
