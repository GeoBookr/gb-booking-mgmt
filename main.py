from fastapi import FastAPI
import asyncio
from routes.journey import router as journey_router
from routes.health import router as health_router
from services.rabbitmq_publisher import publisher
from logging_config import configure_logging

configure_logging()

app = FastAPI(root_path="/api/v1/journey")


@app.on_event("startup")
async def startup_event():
    for _ in range(5):
        try:
            await publisher.connect()
            break
        except Exception as e:
            import logging
            logging.error(f"Waiting for RabbitMQ... {e}")
            await asyncio.sleep(3)

app.include_router(health_router, tags=["Health"])
app.include_router(journey_router, tags=["Journey"])
