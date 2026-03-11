import uuid
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session

from models import Vehicle, ParkingSlot, ParkingRecord, VehicleType, SlotStatus, RecordStatus
from schemas import VehicleCreate

def get_all_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[Vehicle]:
    return db.query(Vehicle).offset(skip).limit(limit).all()

def get_vehicle_by_id(db: Session, vehicle_id: uuid.UUID) -> Optional[Vehicle]:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()

def get_vehicle_by_number(db: Session, vehicle_number: str) -> Optional[Vehicle]:
    return db.query(Vehicle).filter(Vehicle.vehicle_number == vehicle_number.upper()).first()

def create_vehicle(db: Session, payload: VehicleCreate) -> Vehicle:
    vehicle = Vehicle(
        vehicle_number=payload.vehicle_number.upper(),
        vehicle_type=payload.vehicle_type,
        owner_name=payload.owner_name,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle

def get_or_create_vehicle(db: Session, payload: VehicleCreate) -> tuple[Vehicle, bool]:
    existing = get_vehicle_by_number(db, payload.vehicle_number)
    if existing:
        return existing, False
    return create_vehicle(db, payload), True

def get_available_slot(db: Session, vehicle_type: VehicleType) -> Optional[ParkingSlot]:
    return (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.status == SlotStatus.AVAILABLE,
            ParkingSlot.vehicle_type == vehicle_type,
        )
        .order_by(ParkingSlot.slot_number)
        .with_for_update(skip_locked=True)
        .first()
    )

def set_slot_status(db: Session, slot: ParkingSlot, status: SlotStatus) -> ParkingSlot:
    slot.status = status
    db.commit()
    db.refresh(slot)
    return slot
    
def get_active_record(db: Session, vehicle_id: uuid.UUID) -> Optional[ParkingRecord]:
    return (
        db.query(ParkingRecord)
        .filter(ParkingRecord.vehicle_id == vehicle_id, ParkingRecord.status == RecordStatus.ACTIVE)
        .first()
    )


def create_parking_record(db: Session, vehicle_id: uuid.UUID, slot_id: uuid.UUID) -> ParkingRecord:
    record = ParkingRecord(vehicle_id=vehicle_id, slot_id=slot_id, entry_time=datetime.utcnow())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def complete_parking_record(
    db: Session, record: ParkingRecord, exit_time: datetime, total_charge: float
) -> ParkingRecord:
    record.exit_time = exit_time
    record.total_charge = total_charge
    record.status = RecordStatus.COMPLETED
    db.commit()
    db.refresh(record)
    return record

def filter_parking_records(
    db: Session,
    entry_after: Optional[datetime] = None,
    min_hours: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[ParkingRecord]:
    query = db.query(ParkingRecord)
    if entry_after:
        query = query.filter(ParkingRecord.entry_time >= entry_after)
    if min_hours is not None:
        query = query.filter(
            ParkingRecord.exit_time.isnot(None),
            (ParkingRecord.exit_time - ParkingRecord.entry_time) >= timedelta(hours=min_hours),
        )
    return query.order_by(ParkingRecord.entry_time.desc()).offset(skip).limit(limit).all()
