from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from utils.enums import SlotType, VehicleType

# Slot schemas

class CreateSlotRequest(BaseModel):
    slot_number: str
    slot_type: SlotType
    floor: str = "G"
    lane: Optional[int] = None        
    position: Optional[int] = None    

class SlotResponse(BaseModel):
    id: int
    slot_number: str
    slot_type: str
    floor: str
    lane: Optional[int]
    position: Optional[int]
    status: str

    class Config:
        from_attributes = True

# Entry schemas

class QueueEntryRequest(BaseModel):
    vehicle_number: str = Field(min_length=3)
    vehicle_type: VehicleType
    entry_time: datetime
    expected_exit_time: datetime

class DynamicEntryRequest(BaseModel):
    vehicle_number: str = Field(min_length=3)
    vehicle_type: VehicleType

class AdminWalkInRequest(BaseModel):
    vehicle_number: str = Field(min_length=3)
    vehicle_type: VehicleType
    slot_id: Optional[int] = None

# Ticket / session response

class TicketResponse(BaseModel):
    ticket_id: str
    vehicle_number: str
    vehicle_type: str
    slot_number: str
    floor: str
    lane: Optional[int]
    position: Optional[int]
    parking_type: str
    entry_time: datetime
    expected_exit_time: Optional[datetime]
    exit_time: Optional[datetime]
    duration: Optional[str]
    amount_charged: Optional[float]
    status: str

class SessionResponse(BaseModel):
    id: int
    vehicle_number: str
    slot_id: int
    parking_type: str
    entry_time: datetime
    expected_exit_time: Optional[datetime]
    status: str

    class Config:
        from_attributes = True