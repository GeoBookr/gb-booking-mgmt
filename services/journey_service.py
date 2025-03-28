from uuid import uuid4, UUID
from datetime import datetime
from fastapi import HTTPException
from models.journey_models import JourneyRequest, JourneyStatusResponse, JourneyDetailsResponse
from models.db_models import Journey
from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from services.rabbitmq_publisher import publisher


def transform_journey_to_response(journey):
    return JourneyDetailsResponse(
        journey_id=journey.journey_id,
        user_id=journey.user_id,
        origin=journey.origin,
        destination=journey.destination,
        vehicle_type=journey.vehicle_type,
        scheduled_time=journey.scheduled_time,
        created_at=journey.created_at,
        status=journey.status
    )


async def create_journey(request: JourneyRequest, user, db: Session):
    new_journey = Journey(
        user_id=user["user_id"],
        origin=request.origin,
        destination=request.destination,
        vehicle_type=request.vehicle_type,
        scheduled_time=request.scheduled_time,
    )
    db.add(new_journey)
    db.commit()
    db.refresh(new_journey)
    journey = JourneyDetailsResponse(
        journey_id=new_journey.journey_id,
        user_id=new_journey.user_id,
        origin=new_journey.origin,
        destination=new_journey.destination,
        vehicle_type=new_journey.vehicle_type,
        scheduled_time=new_journey.scheduled_time,
        created_at=new_journey.created_at,
        status=new_journey.status
    )
    await publisher.publish("journey.booked", journey.model_dump_json())

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

    await publisher.publish("journey.canceled", {"journey_id": str(journey_id), "user_id": user["user_id"], "status": "canceled"})

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
