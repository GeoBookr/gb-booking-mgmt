from uuid import uuid4, UUID
from datetime import datetime, timezone
from fastapi import HTTPException
from models.journey_models import JourneyRequest, JourneyStatusResponse, JourneyDetailsResponse
from fastapi.concurrency import run_in_threadpool
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
    rounded_time = request.scheduled_time.replace(
        minute=0, second=0, microsecond=0)
    new_journey = Journey(
        user_id=user["user_id"],
        origin_lat=request.origin_lat,
        origin_lon=request.origin_lon,
        destination_lat=request.destination_lat,
        destination_lon=request.destination_lon,
        vehicle_type=request.vehicle_type,
        scheduled_time=rounded_time,
    )
    await run_in_threadpool(db.add, new_journey)
    await run_in_threadpool(db.commit)
    await run_in_threadpool(db.refresh, new_journey)
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
        scheduled_time=new_journey.scheduled_time,
        timestamp=datetime.now(timezone.utc)
    )
    await publisher.publish(event.model_dump())

    return JourneyStatusResponse(journey_id=new_journey.journey_id, status=new_journey.status)


async def cancel_journey_by_id(journey_id: UUID, user, db: Session):
    result = await run_in_threadpool(db.execute, select(Journey).where(Journey.journey_id == journey_id))
    journey = result.scalar_one_or_none()

    if not journey:
        raise HTTPException(status_code=404, detail="Journey not found")
    if journey.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")
    if journey.status == "canceled":
        raise HTTPException(
            status_code=404, detail="Journey is already canceled")
    if journey.status == "rejected":
        raise HTTPException(
            status_code=404, detail="Journey is rejected, so can not be canceled")
    await run_in_threadpool(db.commit)
    event = JourneyCanceledEvent(
        journey_id=journey_id, user_id=user["user_id"], scheduled_time=journey.scheduled_time, timestamp=datetime.now(timezone.utc))
    await publisher.publish(event.model_dump())

    return JourneyStatusResponse(journey_id=journey_id, status="canceled")


async def get_journey_by_id(journey_id: UUID, user, db: Session):
    result = await run_in_threadpool(db.execute, select(Journey).where(Journey.journey_id == journey_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return transform_journey_to_response(record)


async def get_journey_status(journey_id: UUID, user, db: Session):
    result = await run_in_threadpool(db.execute, select(Journey).where(Journey.journey_id == journey_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Journey not found")
    if record.user_id != user["user_id"]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    return JourneyStatusResponse(journey_id=journey_id, status=record.status)


async def get_all_journeys_by_user(user, db: Session):
    result = await run_in_threadpool(db.execute, select(Journey).where(Journey.user_id == user["user_id"]))
    records = result.scalars().all()
    if not records:
        raise HTTPException(
            status_code=404, detail="No journeys found for this user")

    return [
        transform_journey_to_response(journey) for journey in records
    ]
