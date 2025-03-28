from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from dependencies.auth import get_current_user
from models.journey_models import JourneyRequest, JourneyStatusResponse, JourneyDetailsResponse
from services.journey_service import (
    create_journey, cancel_journey_by_id, get_journey_by_id, get_journey_status
)

router = APIRouter()


@router.post("/book", response_model=JourneyStatusResponse)
async def book_journey(request: JourneyRequest, user=Depends(get_current_user)):
    return await create_journey(request, user)


@router.delete("/{journey_id}")
async def cancel_journey(journey_id: UUID, user=Depends(get_current_user)):
    return await cancel_journey_by_id(journey_id, user)


@router.get("/{journey_id}", response_model=JourneyDetailsResponse)
async def get_journey(journey_id: UUID, user=Depends(get_current_user)):
    return await get_journey_by_id(journey_id, user)


@router.get("/status/{journey_id}", response_model=JourneyStatusResponse)
async def get_status(journey_id: UUID, user=Depends(get_current_user)):
    return await get_journey_status(journey_id, user)
