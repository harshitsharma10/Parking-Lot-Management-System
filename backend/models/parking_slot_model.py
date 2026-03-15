from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
from utils.enums import SlotType, SlotStatus

class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True)
    slot_number = Column(String, unique=True, nullable=False)        # "Q-01", "D-01"
    slot_type = Column(Enum(SlotType), nullable=False)               # QUEUE | DYNAMIC
    floor = Column(String, nullable=False, default="G")

    # Lane-based fields (QUEUE only, null for DYNAMIC)
    lane = Column(Integer, nullable=True)                            # Lane number: 1, 2, 3...
    position = Column(Integer, nullable=True)                        # 1=front, 2=middle, 3=back...

    status = Column(Enum(SlotStatus), nullable=False, default=SlotStatus.AVAILABLE)

    sessions = relationship("ParkingSession", back_populates="slot")