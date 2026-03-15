import random
from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from starlette import status

from models.parking_slot_model import ParkingSlot
from models.parking_session_model import ParkingSession
from schemas.ParkingRequest import (
    CreateSlotRequest, QueueEntryRequest,
    DynamicEntryRequest, AdminWalkInRequest, TicketResponse
)
from repositories import parking_repository
from utils.billing import calculate_charge, format_duration
from utils.enums import SlotType, SlotStatus, SessionStatus


# ── Slot management ───────────────────────────────────────────────────────────

def create_slot(db: Session, req: CreateSlotRequest):
    if parking_repository.get_slot_by_number(db, req.slot_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Slot {req.slot_number} already exists"
        )
    if req.slot_type == SlotType.QUEUE:
        if req.lane is None or req.position is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="QUEUE slots must have lane and position specified"
            )

    slot = ParkingSlot(
        slot_number=req.slot_number,
        slot_type=req.slot_type,
        floor=req.floor,
        lane=req.lane,
        position=req.position,
        status=SlotStatus.AVAILABLE       # ← Enum, not string
    )
    return parking_repository.create_slot(db, slot)

def get_all_slots(db: Session):
    return parking_repository.get_all_slots(db)


# ── Queue entry ───────────────────────────────────────────────────────────────

def queue_entry(db: Session, req: QueueEntryRequest, user_id: int):
    if req.expected_exit_time <= req.entry_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="expected_exit_time must be after entry_time"
        )

    existing = parking_repository.get_active_session_by_vehicle(
        db, req.vehicle_number.upper()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vehicle {req.vehicle_number.upper()} already has an active session (session_id: {existing.id})"
        )

    slot = parking_repository.find_available_queue_slot(
        db, req.entry_time, req.expected_exit_time
    )
    if not slot:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No queue slots available for the requested time window"
        )

    session = ParkingSession(
        user_id=user_id,
        vehicle_number=req.vehicle_number.upper(),
        vehicle_type=req.vehicle_type,
        slot_id=slot.id,
        parking_type=SlotType.QUEUE,      # ← Enum, not string
        entry_time=req.entry_time,
        expected_exit_time=req.expected_exit_time,
        status=SessionStatus.ACTIVE       # ← Enum, not string
    )
    created = parking_repository.create_session(db, session)

    return {
        "session_id": created.id,
        "vehicle_number": created.vehicle_number,
        "slot_number": slot.slot_number,
        "lane": slot.lane,
        "position": slot.position,
        "floor": slot.floor,
        "parking_type": "QUEUE",
        "entry_time": created.entry_time,
        "expected_exit_time": created.expected_exit_time,
        "status": created.status,
        "message": f"Assigned to Lane {slot.lane}, Position {slot.position} (front=1)"
    }


# ── Dynamic entry ─────────────────────────────────────────────────────────────

def dynamic_entry(db: Session, req: DynamicEntryRequest, user_id: int):
    existing = parking_repository.get_active_session_by_vehicle(
        db, req.vehicle_number.upper()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vehicle {req.vehicle_number.upper()} already has an active session (session_id: {existing.id})"
        )

    all_available = parking_repository.find_all_available_dynamic_slots(db)
    if not all_available:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No dynamic slots available right now"
        )

    slot = random.choice(all_available)
    parking_repository.update_slot_status(db, slot.id, SlotStatus.OCCUPIED)  # ← Enum

    session = ParkingSession(
        user_id=user_id,
        vehicle_number=req.vehicle_number.upper(),
        vehicle_type=req.vehicle_type,
        slot_id=slot.id,
        parking_type=SlotType.DYNAMIC,    # ← Enum, not string
        entry_time=datetime.now(timezone.utc),
        status=SessionStatus.ACTIVE       # ← Enum, not string
    )
    created = parking_repository.create_session(db, session)

    return {
        "session_id": created.id,
        "vehicle_number": created.vehicle_number,
        "slot_number": slot.slot_number,
        "floor": slot.floor,
        "parking_type": "DYNAMIC",
        "entry_time": created.entry_time,
        "status": created.status
    }


# ── Admin walk-in ─────────────────────────────────────────────────────────────

def admin_walk_in(db: Session, req: AdminWalkInRequest):
    if req.slot_id:
        slot = parking_repository.get_slot_by_id(db, req.slot_id)
        if not slot:
            raise HTTPException(status_code=404, detail="Slot not found")
        if slot.slot_type != SlotType.DYNAMIC:           # ← Enum, not string
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Walk-in slots must be from the DYNAMIC pool"
            )
        if slot.status != SlotStatus.AVAILABLE:          # ← Enum, not string
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slot {slot.slot_number} is not available"
            )
    else:
        all_available = parking_repository.find_all_available_dynamic_slots(db)
        if not all_available:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No dynamic slots available for walk-in"
            )
        slot = all_available[0]

    parking_repository.update_slot_status(db, slot.id, SlotStatus.OCCUPIED)  # ← Enum

    session = ParkingSession(
        user_id=None,
        vehicle_number=req.vehicle_number.upper(),
        vehicle_type=req.vehicle_type,
        slot_id=slot.id,
        parking_type=SlotType.DYNAMIC,    # ← Enum, not string
        entry_time=datetime.now(timezone.utc),
        status=SessionStatus.ACTIVE       # ← Enum, not string
    )
    created = parking_repository.create_session(db, session)

    return {
        "session_id": created.id,
        "vehicle_number": created.vehicle_number,
        "slot_number": slot.slot_number,
        "floor": slot.floor,
        "parking_type": "DYNAMIC",
        "entry_time": created.entry_time,
        "status": created.status,
        "message": "Walk-in registered successfully"
    }


# ── Exit & billing ────────────────────────────────────────────────────────────

def process_exit(db: Session, session_id: int):
    session = parking_repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.status == SessionStatus.COMPLETED:        # ← Enum, not string
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already completed"
        )

    exit_time = datetime.now(timezone.utc)
    amount = calculate_charge(session.entry_time, exit_time, session.vehicle_type)

    if session.parking_type == SlotType.DYNAMIC:         # ← Enum, not string
        parking_repository.update_slot_status(db, session.slot_id, SlotStatus.AVAILABLE)

    return parking_repository.complete_session(db, session_id, exit_time, amount)


# ── Ticket ────────────────────────────────────────────────────────────────────

def get_ticket(db: Session, session_id: int) -> TicketResponse:
    session = parking_repository.get_session_by_id(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    slot = parking_repository.get_slot_by_id(db, session.slot_id)

    duration_str = None
    if session.actual_exit_time:
        duration_str = format_duration(session.entry_time, session.actual_exit_time)
    elif session.status == SessionStatus.ACTIVE:         # ← Enum, not string
        duration_str = format_duration(session.entry_time, datetime.now(timezone.utc))

    return TicketResponse(
        ticket_id=f"TKT-{session.id:05d}",
        vehicle_number=session.vehicle_number,
        vehicle_type=session.vehicle_type,
        slot_number=slot.slot_number,
        floor=slot.floor,
        lane=slot.lane,
        position=slot.position,
        parking_type=session.parking_type,
        entry_time=session.entry_time,
        expected_exit_time=session.expected_exit_time,
        exit_time=session.actual_exit_time,
        duration=duration_str,
        amount_charged=session.amount_charged,
        status=session.status
    )


# ── Session helpers ───────────────────────────────────────────────────────────

def get_my_sessions(db: Session, user_id: int):
    return parking_repository.get_sessions_by_user(db, user_id)

def get_all_active_sessions(db: Session):
    return parking_repository.get_active_sessions(db)