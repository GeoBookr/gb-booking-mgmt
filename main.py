from fastapi import FastAPI
import asyncio
from routes.journey import router as journey_router
from routes.health import router as health_router
from services.rabbitmq_publisher import publisher

app = FastAPI(root_path="/journey")


@app.on_event("startup")
async def startup_event():
    for _ in range(5):
        try:
            await publisher.connect()
            break
        except Exception as e:
            print(f"Waiting for RabbitMQ... {e}")
            await asyncio.sleep(3)
app.include_router(health_router, tags=["Health"])
app.include_router(journey_router, tags=["Journey"])
