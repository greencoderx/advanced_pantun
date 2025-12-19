import requests, os
from datetime import datetime, timedelta

LOCATIONS = {
    "MY_KL": (3.1390, 101.6869),
    "ID_JKT": (-6.2088, 106.8456),
    "ID_ACEH": (5.5483, 95.3238)
}

def is_before_maghrib():
    loc = os.getenv("BOT_LOCATION", "MY_KL")
    lat, lon = LOCATIONS.get(loc, LOCATIONS["MY_KL"])

    today = datetime.utcnow().strftime("%Y-%m-%d")
    url = f"https://api.aladhan.com/v1/timings/{today}?latitude={lat}&longitude={lon}&method=2"
    data = requests.get(url, timeout=10).json()

    maghrib = data["data"]["timings"]["Maghrib"]
    maghrib_time = datetime.strptime(maghrib, "%H:%M")
    return datetime.utcnow().time() < (maghrib_time - timedelta(minutes=30)).time()
