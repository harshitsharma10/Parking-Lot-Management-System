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

# ADMIN — slot management

@router.post("/admin/slots", status_code=status.HTTP_201_CREATED)
def create_slot(db: db_dependency, _: admin_dependency, req: CreateSlotRequest):
    return parking.create_slot(db, req)


@router.get("/admin/slots")
def list_all_slots(db: db_dependency, _: admin_dependency):
    return parking.get_all_slots(db)

# ADMIN — walk-in registration

@router.post("/admin/parking/walk-in", status_code=status.HTTP_201_CREATED)
def admin_walk_in(db: db_dependency, _: admin_dependency, req: AdminWalkInRequest):
    return parking.admin_walk_in(db, req)


@router.get("/admin/sessions")
def list_active_sessions(db: db_dependency, _: admin_dependency):
    return parking.get_all_active_sessions(db)

# USER — queue parking

@router.post("/parking/queue/enter", status_code=status.HTTP_201_CREATED)
def queue_enter(db: db_dependency, current_user: user_dependency, req: QueueEntryRequest):
    return parking.queue_entry(db, req, current_user["id"])

# USER — dynamic parking

@router.post("/parking/dynamic/enter", status_code=status.HTTP_201_CREATED)
def dynamic_enter(db: db_dependency, current_user: user_dependency, req: DynamicEntryRequest):
    return parking.dynamic_entry(db, req, current_user["id"])

# USER — exit 

@router.post("/parking/exit/{session_id}")
def exit_parking(db: db_dependency, _: user_dependency, session_id: int):
    return parking.process_exit(db, session_id)

# USER — ticket

@router.get("/parking/ticket/{session_id}")
def get_ticket(db: db_dependency, _: user_dependency, session_id: int):
    return parking.get_ticket(db, session_id)

# USER — session history

@router.get("/parking/my-sessions")
def my_sessions(db: db_dependency, current_user: user_dependency):
    return parking.get_my_sessions(db, current_user["id"])