import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Enum, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from database import Base

class VehicleType(str, enum.Enum):
    CAR = "CAR"
    BIKE = "BIKE"


class SlotStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"


class RecordStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)       # bcrypt hash
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slot_number = Column(String(10), unique=True, nullable=False, index=True)
    status = Column(Enum(SlotStatus), default=SlotStatus.AVAILABLE, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    records = relationship("ParkingRecord", back_populates="slot")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_number = Column(String(20), unique=True, nullable=False, index=True)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    owner_name = Column(String(100), nullable=False)

    records = relationship("ParkingRecord", back_populates="vehicle")


class ParkingRecord(Base):
    __tablename__ = "parking_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=False)
    slot_id = Column(UUID(as_uuid=True), ForeignKey("parking_slots.id"), nullable=False)
    entry_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    exit_time = Column(DateTime, nullable=True)
    total_charge = Column(Numeric(10, 2), nullable=True)
    status = Column(Enum(RecordStatus), default=RecordStatus.ACTIVE, nullable=False)

    vehicle = relationship("Vehicle", back_populates="records")
    slot = relationship("ParkingSlot", back_populates="records")
