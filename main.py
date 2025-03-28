from fastapi import FastAPI
from routes.journey import router as journey_router
from routes.health import router as health_router

app = FastAPI(root_path="/journey")

app.include_router(health_router, tags=["Health"])
app.include_router(journey_router, tags=["Journey"])
