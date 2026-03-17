from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
from utils.enums import SlotType, SlotStatus

class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id = Column(Integer, primary_key=True)
    slot_number = Column(String, unique=True, nullable=False)        
    slot_type = Column(Enum(SlotType), nullable=False)               
    floor = Column(String, nullable=False, default="G")
    lane = Column(Integer, nullable=True)                            
    position = Column(Integer, nullable=True)           
    status = Column(Enum(SlotStatus), nullable=False, default=SlotStatus.AVAILABLE)

    sessions = relationship("ParkingSession", back_populates="slot")