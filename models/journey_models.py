from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from uuid import UUID


class JourneyRequest(BaseModel):
    origin: str
    destination: str
    scheduled_time: datetime
    vehicle_type: Literal["car", "bus", "truck", "motorcycle"]


class JourneyStatusResponse(BaseModel):
    journey_id: UUID
    status: Literal["pending", "confirmed", "rejected", "canceled"]


class JourneyDetailsResponse(JourneyStatusResponse):
    user_id: str
    origin: str
    destination: str
    vehicle_type: str
    scheduled_time: datetime
    created_at: datetime
