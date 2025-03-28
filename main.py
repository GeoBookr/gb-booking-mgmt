from fastapi import FastAPI
from routes.journey import router

app = FastAPI()

app.include_router(router, prefix="/journey", tags=["Journey"])
