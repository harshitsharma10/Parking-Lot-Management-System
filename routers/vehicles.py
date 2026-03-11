import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import SlotStatus
import crud
from schemas import VehicleCreate, VehicleOut, EntryResponse, ExitResponse

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])

RATES = {"CAR": 50.0, "BIKE": 20.0}
MIN_HOURS = 1


def _calc_charge(vehicle_type: str, entry: datetime, exit_: datetime) -> float:
    hours = max(MIN_HOURS, (exit_ - entry).total_seconds() / 3600)
    return round(hours * RATES.get(vehicle_type, 50.0), 2)


@router.get("", response_model=List[VehicleOut])
def get_all_vehicles(db: Session = Depends(get_db)):
    """List all registered vehicles."""
    return crud.get_all_vehicles(db)


@router.post("", response_model=EntryResponse, status_code=status.HTTP_201_CREATED)
def vehicle_entry(payload: VehicleCreate, db: Session = Depends(get_db)):
    """Vehicle entry — registers vehicle, allocates slot, starts billing."""
    vehicle, _ = crud.get_or_create_vehicle(db, payload)

    if crud.get_active_record(db, vehicle.id):
        raise HTTPException(status_code=409, detail=f"'{vehicle.vehicle_number}' is already parked.")

    slot = crud.get_available_slot(db, vehicle.vehicle_type)
    if not slot:
        raise HTTPException(status_code=409, detail=f"No available slots for {vehicle.vehicle_type.value}.")

    crud.set_slot_status(db, slot, SlotStatus.OCCUPIED)
    record = crud.create_parking_record(db, vehicle.id, slot.id)

    return EntryResponse(
        message="Vehicle entered successfully.",
        record_id=record.id,
        vehicle_number=vehicle.vehicle_number,
        slot_number=slot.slot_number,
        entry_time=record.entry_time,
    )


@router.delete("/{vehicle_id}", response_model=ExitResponse)
def vehicle_exit(vehicle_id: uuid.UUID, db: Session = Depends(get_db)):
    """Vehicle exit — calculates bill, frees slot, closes record."""
    vehicle = crud.get_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found.")

    record = crud.get_active_record(db, vehicle.id)
    if not record:
        raise HTTPException(status_code=404, detail=f"No active record for '{vehicle.vehicle_number}'.")

    exit_time = datetime.utcnow()
    total_charge = _calc_charge(vehicle.vehicle_type.value, record.entry_time, exit_time)
    duration_hours = (exit_time - record.entry_time).total_seconds() / 3600

    crud.complete_parking_record(db, record, exit_time, total_charge)
    crud.set_slot_status(db, record.slot, SlotStatus.AVAILABLE)

    return ExitResponse(
        message="Vehicle exited successfully.",
        vehicle_number=vehicle.vehicle_number,
        slot_number=record.slot.slot_number,
        entry_time=record.entry_time,
        exit_time=exit_time,
        duration_hours=round(duration_hours, 2),
        total_charge=total_charge,
    )
