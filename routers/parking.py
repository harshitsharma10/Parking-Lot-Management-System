from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database import get_db
from models import ParkingSlot, ParkingRecord, VehicleType
from schemas import SlotOut, RecordOut

router = APIRouter(prefix="/parking", tags=["Parking"])


class SlotCreate(BaseModel):
    slot_number: str = Field(..., min_length=1, max_length=10)
    vehicle_type: VehicleType


@router.get("/slots", response_model=List[SlotOut])
def get_all_slots(db: Session = Depends(get_db)):
    """List all slots with current availability status."""
    return db.query(ParkingSlot).order_by(ParkingSlot.slot_number).all()


@router.post("/slots", response_model=SlotOut, status_code=status.HTTP_201_CREATED)
def create_slot(payload: SlotCreate, db: Session = Depends(get_db)):
    """Add a new parking slot."""
    if db.query(ParkingSlot).filter(ParkingSlot.slot_number == payload.slot_number.upper()).first():
        raise HTTPException(status_code=409, detail=f"Slot '{payload.slot_number}' already exists.")
    slot = ParkingSlot(slot_number=payload.slot_number.upper(), vehicle_type=payload.vehicle_type)
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot


@router.get("/records", response_model=List[RecordOut])
def get_all_records(db: Session = Depends(get_db)):
    """View full entry/exit log."""
    return db.query(ParkingRecord).order_by(ParkingRecord.entry_time.desc()).all()
