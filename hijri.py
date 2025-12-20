from hijri_converter import Gregorian
from datetime import datetime
from zoneinfo import ZoneInfo
import os

TZ = ZoneInfo("Asia/Kuala_Lumpur")

def get_hijri():
    today = datetime.now(TZ).date()
    h = Gregorian(today.year, today.month, today.day).to_hijri()
    return {
        "year": h.year,
        "month": h.month,
        "day": h.day,
        "month_name": h.month_name()
    }

def hijri_footer():
    h = get_hijri()
    return f"📅 {h['day']} {h['month_name']} {h['year']}H | 🇲🇾 Malaysia"

def hijri_override():
    return os.getenv("HIJRI_OVERRIDE", "").lower().strip()
