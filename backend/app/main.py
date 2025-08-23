from fastapi import FastAPI
from app.database.core import Base, engine
from app.api.routes import api_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router=api_router)
