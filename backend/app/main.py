from fastapi import FastAPI
from database.core import Base, engine
from api.routes import api_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(router=api_router)
