import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from models import VehicleType

class VehicleCreate(BaseModel):
    vehicle_number: str = Field(..., min_length=2, max_length=20, examples=["TN01AB1234"])
    vehicle_type: VehicleType
    owner_name: str = Field(..., min_length=2, max_length=100)

    @field_validator("vehicle_number")
    @classmethod
    def uppercase_number(cls, v: str) -> str:
        return v.strip().upper()

class VehicleOut(BaseModel):
    id: uuid.UUID
    vehicle_number: str
    vehicle_type: VehicleType
    owner_name: str
    model_config = {"from_attributes": True}


class SlotOut(BaseModel):
    slot_number: str
    status: str
    vehicle_type: VehicleType
    model_config = {"from_attributes": True}


class RecordOut(BaseModel):
    id: uuid.UUID
    vehicle_id: uuid.UUID
    slot_id: uuid.UUID
    entry_time: datetime
    exit_time: Optional[datetime] = None
    total_charge: Optional[float] = None
    status: str
    model_config = {"from_attributes": True}


class EntryResponse(BaseModel):
    message: str
    record_id: uuid.UUID
    vehicle_number: str
    slot_number: str
    entry_time: datetime


class ExitResponse(BaseModel):
    message: str
    vehicle_number: str
    slot_number: str
    entry_time: datetime
    exit_time: datetime
    duration_hours: float
    total_charge: float
