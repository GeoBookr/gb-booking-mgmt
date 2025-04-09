from uuid import uuid4, UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from models.journey_models import JourneyRequest, JourneyStatusResponse, JourneyDetailsResponse
from models.db_models import Journey
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from services.rabbitmq_publisher import publisher
from models.events import JourneyBookedEvent, JourneyCanceledEvent


def transform_journey_to_response(journey):
    return JourneyDetailsResponse(
        journey_id=journey.journey_id,
        user_id=journey.user_id,
        origin_lat=journey.origin_lat,
        origin_lon=journey.origin_lon,
        destination_lat=journey.destination_lat,
        destination_lon=journey.destination_lon,
        vehicle_type=journey.vehicle_type,
        scheduled_time=journey.scheduled_time,
        created_at=journey.created_at,
        status=journey.status
    )


async def create_journey(request: JourneyRequest, user, db: Session):
    new_journey = Journey(
        user_id=user["user_id"],
        origin_lat=request.origin_lat,
        origin_lon=request.origin_lon,
        destination_lat=request.destination_lat,
        destination_lon=request.destination_lon,
        vehicle_type=request.vehicle_type,
        scheduled_time=request.scheduled_time,
    )
    db.add(new_journey)
    db.commit()
    db.refresh(new_journey)
    journey = transform_journey_to_response(new_journey)
    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    if journey.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    event = JourneyBookedEvent(
        journey_id=new_journey.journey_id,
        user_id=new_journey.user_id,
        route=[],
        origin_lat=new_journey.origin_lat,
        origin_lon=new_journey.origin_lon,
        destination_lat=new_journey.destination_lat,
        destination_lon=new_journey.destination_lon,
        timestamp=datetime.now(timezone.utc)
    )
    await publisher.publish("journey.booked.v1", event.model_dump())

    return JourneyStatusResponse(journey_id=new_journey.journey_id, status=new_journey.status)


async def cancel_journey_by_id(journey_id: UUID, user, db: Session):
    record = db.execute(select(Journey).where(
        Journey.journey_id == journey_id))
    journey = record.scalar_one_or_none()

    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    if journey.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    journey.status = "canceled"
    await db.commit()
    event = JourneyCanceledEvent(
        journey_id=journey_id, user_id=user["user_id"], timestamp=datetime.now(timezone.utc))
    await publisher.publish("journey.canceled.v1", event.model_dump())

    return JourneyStatusResponse(journey_id=journey_id, status="canceled")


def get_journey_by_id(journey_id: UUID, user, db: Session):
    result = db.execute(select(Journey).where(
        Journey.journey_id == journey_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return transform_journey_to_response(record)


def get_journey_status(journey_id: UUID, user, db: Session):
    result = db.execute(select(Journey).where(
        Journey.journey_id == journey_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return JourneyStatusResponse(journey_id=journey_id, status=record.status)


def get_all_journeys_by_user(user, db: Session):
    result = db.execute(select(Journey).where(
        Journey.user_id == user["user_id"]))
    records = result.scalars().all()
    if not records:
        raise HTTPException(
            status_code=404, detail="No journeys found for this user")

    return [
        transform_journey_to_response(journey) for journey in records
    ]
