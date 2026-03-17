from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Enum
from sqlalchemy.sql import func
from database import Base
from sqlalchemy.orm import relationship
from utils.enums import VehicleType, ParkingType, SessionStatus

class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    vehicle_number = Column(String, nullable=False)
    vehicle_type = Column(Enum(VehicleType), nullable=False)
    slot_id = Column(Integer, ForeignKey("parking_slots.id"), nullable=False)
    parking_type = Column(Enum(ParkingType), nullable=False)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    expected_exit_time = Column(DateTime(timezone=True), nullable=True)
    actual_exit_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(SessionStatus), nullable=False, default=SessionStatus.ACTIVE)
    amount_charged = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="sessions")
    slot = relationship("ParkingSlot", back_populates="sessions")
