from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from utils.billing import calculate_charge
from utils.enums import ParkingType
from models.parking_slot_model import ParkingSlot, SlotStatus, SlotType
from models.parking_session_model import ParkingSession, SessionStatus

BUFFER_MINUTES = 15


# Slot queries

def get_all_slots(db: Session):
    slots = db.query(ParkingSlot).all()
    now = datetime.now(timezone.utc)

    result = []
    for slot in slots:
        if slot.slot_type == SlotType.QUEUE:
            active = (
                db.query(ParkingSession)
                .filter(
                    ParkingSession.slot_id == slot.id,
                    ParkingSession.status == SessionStatus.ACTIVE,
                    ParkingSession.entry_time <= now,        
                    ParkingSession.expected_exit_time >= now 
                )
                .first()
            )
            result.append({
                "id": slot.id,
                "slot_number": slot.slot_number,
                "slot_type": slot.slot_type,
                "floor": slot.floor,
                "lane": slot.lane,
                "position": slot.position,
                "status": "OCCUPIED" if active else "AVAILABLE"
            })
        else:
            result.append({
                "id": slot.id,
                "slot_number": slot.slot_number,
                "slot_type": slot.slot_type,
                "floor": slot.floor,
                "lane": slot.lane,
                "position": slot.position,
                "status": slot.status
            })

    return result

def get_slot_by_id(db: Session, slot_id: int):
    return db.query(ParkingSlot).filter(ParkingSlot.id == slot_id).first()

def get_slot_by_number(db: Session, slot_number: str):
    return db.query(ParkingSlot).filter(ParkingSlot.slot_number == slot_number).first()

def create_slot(db: Session, slot: ParkingSlot):
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot

def update_slot_status(db: Session, slot_id: int, status: SlotStatus):
    slot = get_slot_by_id(db, slot_id)
    if slot:
        slot.status = status
        db.flush()
    return slot


# Queue: lane-based slot allocation
# Rules:
#  1. Within a lane, exit times must be non-decreasing front → back
#  2. New car joins a lane only if its exit_time >= exit_time of all cars ahead
#  3. Among valid lanes, pick the one with fewest empty slots (pack tight)
#  4. If no valid lane, open any completely empty lane (position 1 = front)
#  5. 15-min buffer enforced between sessions on the same physical slot

def _slot_has_conflict(db, slot_id, entry_time, expected_exit_time):
    return bool(
        db.query(ParkingSession)
        .filter(
            ParkingSession.slot_id == slot_id,
            ParkingSession.status == SessionStatus.ACTIVE,
            ParkingSession.entry_time < expected_exit_time + timedelta(minutes=BUFFER_MINUTES),
            ParkingSession.expected_exit_time > entry_time - timedelta(minutes=BUFFER_MINUTES),
        )
        .first()
    )

def find_available_queue_slot(db: Session, entry_time: datetime, expected_exit_time: datetime):
    all_queue_slots = (
        db.query(ParkingSlot)
        .filter(ParkingSlot.slot_type == SlotType.QUEUE)
        .order_by(ParkingSlot.lane, ParkingSlot.position)
        .all()
    )

    lanes = {}
    for slot in all_queue_slots:
        lanes.setdefault(slot.lane, []).append(slot)

    valid_candidates = []  
    empty_lane_slot = None 

    for lane_num, slots_in_lane in sorted(lanes.items()):

        lane_has_any_occupied = any(
            _slot_has_conflict(db, s.id, entry_time, expected_exit_time)
            for s in slots_in_lane
        )

        if not lane_has_any_occupied:
            if empty_lane_slot is None:
                empty_lane_slot = slots_in_lane[0]  
            continue  

        next_empty = None
        for slot in slots_in_lane:
            if not _slot_has_conflict(db, slot.id, entry_time, expected_exit_time):
                next_empty = slot
                break

        if next_empty is None:
            continue  

        front_slots = [s for s in slots_in_lane if s.position < next_empty.position]
        constraint_ok = True
        for fs in front_slots:
            front_session = (
                db.query(ParkingSession)
                .filter(
                    ParkingSession.slot_id == fs.id,
                    ParkingSession.status == SessionStatus.ACTIVE,
                )
                .order_by(ParkingSession.expected_exit_time.desc())
                .first()
            )
            if front_session and front_session.expected_exit_time > expected_exit_time:
                constraint_ok = False
                break

        if not constraint_ok:
            continue

        occupied = sum(
            1 for s in slots_in_lane
            if _slot_has_conflict(db, s.id, entry_time, expected_exit_time)
        )
        empty_count = len(slots_in_lane) - occupied
        valid_candidates.append((empty_count, next_empty))

    if valid_candidates:
        valid_candidates.sort(key=lambda x: x[0])
        return valid_candidates[0][1]

    return empty_lane_slot  


# Dynamic slot allocation

def find_all_available_dynamic_slots(db: Session):
    return (
        db.query(ParkingSlot)
        .filter(
            ParkingSlot.slot_type == SlotType.DYNAMIC,
            ParkingSlot.status == SlotStatus.AVAILABLE,
        )
        .all()
    )

def expire_overdue_queue_sessions(db: Session):
    """
    Auto-complete queue sessions where expected_exit_time has passed
    and user never called exit. Charge based on expected duration.
    """
    now = datetime.now(timezone.utc)
    overdue = (
        db.query(ParkingSession)
        .filter(
            ParkingSession.parking_type == ParkingType.QUEUE,
            ParkingSession.status == SessionStatus.ACTIVE,
            ParkingSession.expected_exit_time < now,
        )
        .all()
    )

    for session in overdue:
        amount = calculate_charge(
            session.entry_time,
            session.expected_exit_time,  
            session.vehicle_type
        )
        session.actual_exit_time = session.expected_exit_time
        session.amount_charged = amount
        session.status = SessionStatus.COMPLETED

    if overdue:
        db.commit()

    return len(overdue)

# Session queries

def create_session(db: Session, session: ParkingSession):
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session_by_id(db: Session, session_id: int):
    return db.query(ParkingSession).filter(ParkingSession.id == session_id).first()

def get_active_sessions(db: Session):
    return db.query(ParkingSession).filter(ParkingSession.status == SessionStatus.ACTIVE).all()

def get_sessions_by_user(db: Session, user_id: int):
    return db.query(ParkingSession).filter(ParkingSession.user_id == user_id).all()

def get_active_session_by_vehicle(db: Session, vehicle_number: str):
    return (
        db.query(ParkingSession)
        .filter(
            ParkingSession.vehicle_number == vehicle_number,
            ParkingSession.status == SessionStatus.ACTIVE
        )
        .first()
    )

def complete_session(db: Session, session_id: int, actual_exit_time: datetime, amount: float):
    session = get_session_by_id(db, session_id)
    if session:
        session.actual_exit_time = actual_exit_time
        session.amount_charged = amount
        session.status = SessionStatus.COMPLETED
        db.commit()
        db.refresh(session)
    return session