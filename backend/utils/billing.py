from datetime import datetime
from math import ceil

# ── Pricing config (tweak freely) ────────────────────────────────────────────
RATE_PER_HOUR = {
    "CAR":   30.0,   # ₹30 / hour
    "BIKE":  15.0,   # ₹15 / hour
    "TRUCK": 60.0,   # ₹60 / hour
}
MINIMUM_CHARGE = {
    "CAR":   20.0,
    "BIKE":  10.0,
    "TRUCK": 40.0,
}
FREE_MINUTES = 15   # first 15 min free (grace period)

def calculate_charge(entry_time: datetime, exit_time: datetime, vehicle_type: str) -> float:
    """
    Billing rules:
    - First FREE_MINUTES minutes are free (grace period).
    - After that, charge is rounded up to the next full hour.
    - Minimum charge applies if duration > grace period.
    """
    duration_seconds = (exit_time - entry_time).total_seconds()
    duration_minutes = duration_seconds / 60

    if duration_minutes <= FREE_MINUTES:
        return 0.0

    rate = RATE_PER_HOUR.get(vehicle_type, RATE_PER_HOUR["CAR"])
    minimum = MINIMUM_CHARGE.get(vehicle_type, MINIMUM_CHARGE["CAR"])

    billable_hours = ceil(duration_minutes / 60)
    charge = billable_hours * rate

    return max(charge, minimum)


def format_duration(entry_time: datetime, exit_time: datetime) -> str:
    total_seconds = int((exit_time - entry_time).total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"