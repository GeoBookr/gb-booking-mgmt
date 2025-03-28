from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from dependencies.auth import get_current_user
from dependencies.db import get_db
from sqlalchemy.orm import Session
from models.journey_models import JourneyRequest, JourneyStatusResponse, JourneyDetailsResponse
from services.journey_service import (
    create_journey, cancel_journey_by_id, get_journey_by_id, get_journey_status, get_all_journeys_by_user
)

router = APIRouter()


@router.get("/", response_model=list[JourneyDetailsResponse])
def get_all_journeys(user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_all_journeys_by_user(user, db)


@router.post("/", response_model=JourneyStatusResponse)
async def book_journey(request: JourneyRequest, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return await create_journey(request, user, db)


@router.delete("/{journey_id}", response_model=JourneyStatusResponse)
async def cancel_journey(journey_id: UUID, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return await cancel_journey_by_id(journey_id, user, db)


@router.get("/{journey_id}", response_model=JourneyDetailsResponse)
def get_journey(journey_id: UUID, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_journey_by_id(journey_id, user, db)


@router.get("/{journey_id}/status", response_model=JourneyStatusResponse)
def get_status(journey_id: UUID, user=Depends(get_current_user), db: Session = Depends(get_db)):
    return get_journey_status(journey_id, user, db)
