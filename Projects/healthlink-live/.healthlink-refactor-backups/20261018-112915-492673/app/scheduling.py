import re
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

CLINIC_TZ = ZoneInfo("Asia/Kolkata")
SLOT_LENGTH = timedelta(minutes=30)
DAYS = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}

class UnsupportedSchedule(ValueError):
    pass

def build_daily_slots(schedule: str, on_date: date):
    """Generate fixed slots from the supplied directory's working-hours format."""
    midnight = datetime.combine(on_date, time.min, tzinfo=CLINIC_TZ)
    schedule = " ".join(schedule.strip().split())
    if schedule == "24/7":
        opening, closing = midnight, midnight + timedelta(days=1)
    else:
        match = re.fullmatch(
            r"(.+?)\s+(\d{1,2}(?::\d{2})?(?:AM|PM))\s*-\s*(\d{1,2}(?::\d{2})?(?:AM|PM))",
            schedule, flags=re.IGNORECASE,
        )
        if not match:
            raise UnsupportedSchedule("Unsupported working-hours format")
        days_text, opening_text, closing_text = match.groups()
        working_days = set()
        try:
            for token in days_text.split():
                parts = token.split("-")
                if len(parts) == 1:
                    working_days.add(DAYS[parts[0].title()])
                elif len(parts) == 2:
                    start, end = [DAYS[p.title()] for p in parts]
                    working_days.update((start + i) % 7 for i in range((end - start) % 7 + 1))
                else:
                    raise ValueError("Invalid days")
            def parse_clock(value):
                return datetime.strptime(value.upper(), "%I:%M%p" if ":" in value else "%I%p").time()
            opening = datetime.combine(on_date, parse_clock(opening_text), tzinfo=CLINIC_TZ)
            closing = datetime.combine(on_date, parse_clock(closing_text), tzinfo=CLINIC_TZ)
        except (KeyError, ValueError) as exc:
            raise UnsupportedSchedule("Invalid schedule values") from exc
        if closing <= opening:
            raise UnsupportedSchedule("Overnight schedules are not supported yet")
        if on_date.weekday() not in working_days:
            return []
    slots = []
    cursor = opening
    while cursor + SLOT_LENGTH <= closing:
        slots.append({"starts_at": cursor, "ends_at": cursor + SLOT_LENGTH})
        cursor += SLOT_LENGTH
    return slots
