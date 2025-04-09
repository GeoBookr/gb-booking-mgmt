from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from uuid import UUID


class JourneyRequest(BaseModel):
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    scheduled_time: datetime
    vehicle_type: Literal["car", "bus", "truck", "motorcycle"]


class JourneyStatusResponse(BaseModel):
    journey_id: UUID
    status: Literal["pending", "confirmed", "rejected", "canceled"]


class JourneyDetailsResponse(JourneyStatusResponse):
    user_id: str
    origin_lat: float
    origin_lon: float
    destination_lat: float
    destination_lon: float
    vehicle_type: str
    scheduled_time: datetime
    created_at: datetime
