from uuid import uuid4, UUID
from datetime import datetime
from fastapi import HTTPException
from models.journey_models import JourneyRequest, JourneyStatusResponse, JourneyDetailsResponse

# Temporary in-memory DB
fake_db = {}


async def create_journey(request: JourneyRequest, user):
    journey_id = uuid4()
    now = datetime.utcnow()

    fake_db[str(journey_id)] = {
        "journey_id": journey_id,
        "user_id": user["user_id"],
        "origin": request.origin,
        "destination": request.destination,
        "vehicle_type": request.vehicle_type,
        "scheduled_time": request.scheduled_time,
        "status": "pending",
        "created_at": now
    }

    # TODO: send to RabbitMQ

    return JourneyStatusResponse(journey_id=journey_id, status="pending")


async def cancel_journey_by_id(journey_id: UUID, user):
    record = fake_db.get(str(journey_id))
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    record["status"] = "canceled"
    # TODO: send cancellation event

    return {"message": "Journey canceled", "journey_id": journey_id}


async def get_journey_by_id(journey_id: UUID, user):
    record = fake_db.get(str(journey_id))
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return record


async def get_journey_status(journey_id: UUID, user):
    record = fake_db.get(str(journey_id))
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record["user_id"] != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return JourneyStatusResponse(journey_id=journey_id, status=record["status"])
