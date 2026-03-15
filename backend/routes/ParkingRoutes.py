from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from database import get_db
from utils.jwt import get_current_user
from utils.admin_guard import require_admin
from schemas.ParkingRequest import (
    CreateSlotRequest, QueueEntryRequest,
    DynamicEntryRequest, AdminWalkInRequest
)
from services import parking

router = APIRouter(tags=["PARKING"])
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
admin_dependency = Annotated[dict, Depends(require_admin)]


# ════════════════════════════════════════════════════════════════════════════════
# ADMIN — slot management
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/admin/slots", status_code=status.HTTP_201_CREATED)
def create_slot(db: db_dependency, _: admin_dependency, req: CreateSlotRequest):
    """Create a single parking slot (QUEUE or DYNAMIC)."""
    return parking.create_slot(db, req)


@router.get("/admin/slots")
def list_all_slots(db: db_dependency, _: admin_dependency):
    """View all slots with current status."""
    return parking.get_all_slots(db)


# ════════════════════════════════════════════════════════════════════════════════
# ADMIN — walk-in registration (no registered user)
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/admin/parking/walk-in", status_code=status.HTTP_201_CREATED)
def admin_walk_in(db: db_dependency, _: admin_dependency, req: AdminWalkInRequest):
    """
    Admin registers a walk-in vehicle.
    Slot is taken from DYNAMIC pool and marked OCCUPIED.
    Optionally provide slot_id to pick a specific slot; otherwise auto-assigned.
    """
    return parking.admin_walk_in(db, req)


@router.get("/admin/sessions")
def list_active_sessions(db: db_dependency, _: admin_dependency):
    """View all currently active parking sessions."""
    return parking.get_all_active_sessions(db)


# ════════════════════════════════════════════════════════════════════════════════
# USER — queue parking
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/parking/queue/enter", status_code=status.HTTP_201_CREATED)
def queue_enter(db: db_dependency, current_user: user_dependency, req: QueueEntryRequest):
    """
    Register a vehicle for QUEUE parking.
    Provide entry_time + expected_exit_time.
    System finds a slot with no overlap (15-min buffer).
    """
    return parking.queue_entry(db, req, current_user["id"])


# ════════════════════════════════════════════════════════════════════════════════
# USER — dynamic parking
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/parking/dynamic/enter", status_code=status.HTTP_201_CREATED)
def dynamic_enter(db: db_dependency, current_user: user_dependency, req: DynamicEntryRequest):
    """
    Register a vehicle for DYNAMIC (mall-style) parking.
    Slot is randomly assigned and marked OCCUPIED immediately.
    """
    return parking.dynamic_entry(db, req, current_user["id"])


# ════════════════════════════════════════════════════════════════════════════════
# USER — exit (works for both queue and dynamic)
# ════════════════════════════════════════════════════════════════════════════════

@router.post("/parking/exit/{session_id}")
def exit_parking(db: db_dependency, _: user_dependency, session_id: int):
    """
    Mark exit for a session. Calculates and stores charge.
    For DYNAMIC, frees the slot immediately.
    """
    return parking.process_exit(db, session_id)


# ════════════════════════════════════════════════════════════════════════════════
# USER — ticket
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/parking/ticket/{session_id}")
def get_ticket(db: db_dependency, _: user_dependency, session_id: int):
    """
    Returns ticket data for a session.
    Frontend uses this to render the ticket card with pricing.
    """
    return parking.get_ticket(db, session_id)


# ════════════════════════════════════════════════════════════════════════════════
# USER — session history
# ════════════════════════════════════════════════════════════════════════════════

@router.get("/parking/my-sessions")
def my_sessions(db: db_dependency, current_user: user_dependency):
    """List all sessions (active + completed) for the logged-in user."""
    return parking.get_my_sessions(db, current_user["id"])