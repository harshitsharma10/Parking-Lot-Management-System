from datetime import datetime, timezone
from math import ceil

RATE_PER_HOUR = {
    "CAR":   30.0,
    "BIKE":  15.0,
    "TRUCK": 60.0,
}
MINIMUM_CHARGE = {
    "CAR":   20.0,
    "BIKE":  10.0,
    "TRUCK": 40.0,
}
FREE_MINUTES = 15

def _ensure_aware(dt: datetime) -> datetime:
    """Make datetime timezone-aware (assume UTC if naive)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

def calculate_charge(entry_time: datetime, exit_time: datetime, vehicle_type) -> float:
    entry_time = _ensure_aware(entry_time)
    exit_time = _ensure_aware(exit_time)

    duration_seconds = (exit_time - entry_time).total_seconds()
    duration_minutes = duration_seconds / 60

    if duration_minutes <= FREE_MINUTES:
        return 0.0

    vtype = vehicle_type.value if hasattr(vehicle_type, 'value') else str(vehicle_type)

    rate = RATE_PER_HOUR.get(vtype, RATE_PER_HOUR["CAR"])
    minimum = MINIMUM_CHARGE.get(vtype, MINIMUM_CHARGE["CAR"])
    billable_hours = ceil(duration_minutes / 60)
    return max(billable_hours * rate, minimum)

def format_duration(entry_time: datetime, exit_time: datetime) -> str:
    entry_time = _ensure_aware(entry_time)
    exit_time = _ensure_aware(exit_time)

    total_seconds = int((exit_time - entry_time).total_seconds())

    if total_seconds < 0:
        return "0m"  

    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"