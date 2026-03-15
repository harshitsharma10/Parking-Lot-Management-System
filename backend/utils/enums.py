import enum

class SlotType(str, enum.Enum):
    QUEUE = "QUEUE"
    DYNAMIC = "DYNAMIC"

class SlotStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    OCCUPIED = "OCCUPIED"

class VehicleType(str, enum.Enum):
    CAR = "CAR"
    BIKE = "BIKE"
    TRUCK = "TRUCK"

class ParkingType(str, enum.Enum):
    QUEUE = "QUEUE"
    DYNAMIC = "DYNAMIC"

class SessionStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"