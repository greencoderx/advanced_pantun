import os, json, random, sys, traceback
from datetime import datetime
from zoneinfo import ZoneInfo
from hijri_converter import Gregorian
import tweepy
import requests

# =====================
# CONFIG
# =====================
TZ = ZoneInfo("Asia/Kuala_Lumpur")
BOT_ENABLED = os.getenv("BOT_ENABLED", "").lower() == "true"
HIJRI_OVERRIDE = os.getenv("HIJRI_OVERRIDE", "").lower().strip()

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHANNEL_ID = os.getenv("TG_CHANNEL_ID")
TG_ADMIN_ID = os.getenv("TG_ADMIN_ID")  # personal chat for alerts

# =====================
# SAFETY EXIT
# =====================
if not BOT_ENABLED:
    print("Bot disabled by BOT_ENABLED")
    sys.exit(0)

# =====================
# TWITTER CLIENT
# =====================
client = tweepy.Client(
    consumer_key=os.getenv("TW_API_KEY"),
    consumer_secret=os.getenv("TW_API_SECRET"),
    access_token=os.getenv("TW_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TW_ACCESS_SECRET"),
)

# =====================
# HELPERS
# =====================
def now():
    return datetime.now(TZ)

def invisible_tag():
    return f"\u200b{now().strftime('%Y%m%d%H%M%S')}"

def telegram_send(text):
    if not TG_BOT_TOKEN or not TG_CHANNEL_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_CHANNEL_ID, "text": text})

def telegram_alert(error):
    if not TG_BOT_TOKEN or not TG_ADMIN_ID:
        return
    url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TG_ADMIN_ID, "text": f"🚨 BOT ERROR\n{error}"})

def hijri_date():
    today = now().date()
    h = Gregorian(today.year, today.month, today.day).to_hijri()
    return h.year, h.month, h.day, h.month_name()

def hijri_footer():
    y, m, d, name = hijri_date()
    return f"📅 {d} {name} {y}H | 🇲🇾 Malaysia"

def is_friday():
    return now().weekday() == 4

# =====================
# LOAD DATA
# =====================
QURAN = json.load(open("data/quran.json", encoding="utf-8"))
HADITH = json.load(open("data/hadith.json", encoding="utf-8"))

# =====================
# RAMADAN LOGIC
# =====================
def ramadan_countdown():
    _, m, d, _ = hijri_date()
    if m == 8:  # Sha'ban
        days = 30 - d
        if days <= 10:
            return (
                "🌙 Ramadan is approaching!\n\n"
                f"⏳ Approximately {days} days remaining.\n"
                "Let us prepare our hearts, intentions, and deeds."
            )
    return None

def resolve_mode():
    _, m, _, _ = hijri_date()

    if HIJRI_OVERRIDE in ["off", "normal"]:
        return "normal"
    if HIJRI_OVERRIDE == "ramadan":
        return "ramadan"

    if is_friday():
        return "friday"

    if m == 9:
        return "ramadan"

    return "normal"

# =====================
# POST FUNCTIONS
# =====================
def post(text):
    final = f"{text}\n\n{hijri_footer()}{invisible_tag()}"
    client.create_tweet(text=final)
    telegram_send(final)

def post_quran():
    q = random.choice(QURAN)
    text = (
        "📖 Qur’an Reflection\n\n"
        f"{q['arabic']}\n\n"
        f"🇮🇩 {q['indonesian']}\n\n"
        f"🇬🇧 {q['english']}"
    )
    post(text)

def post_hadith():
    h = random.choice(HADITH)
    text = (
        "📜 Hadith of the Day\n\n"
        f"{h['arabic']}\n\n"
        f"🇮🇩 {h['indonesian']}\n\n"
        f"🇬🇧 {h['english']}"
    )
    post(text)

# =====================
# MAIN
# =====================
try:
    mode = resolve_mode()

    countdown = ramadan_countdown()
    if countdown:
        post(countdown)

    if mode == "friday":
        post_quran()
        post_hadith()

    elif mode == "ramadan":
        post_quran()
        if is_friday():
            post_hadith()

    else:
        # Normal weekday (pantun logic intentionally skipped per your latest rule)
        post_quran()

except Exception as e:
    err = traceback.format_exc()
    print(err)
    telegram_alert(err)
    sys.exit(1)
