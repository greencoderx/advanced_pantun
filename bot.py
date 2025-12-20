import os, json, random, datetime
from zoneinfo import ZoneInfo
import tweepy

from pantun_ai import get_pantun_safe, translate_to_english
from prayer_time import is_before_maghrib
from telegram import send_telegram, alert_admin

# --- TIMEZONE ---
MY_TZ = ZoneInfo("Asia/Kuala_Lumpur")

def now_myt():
    return datetime.datetime.now(MY_TZ)

def is_friday():
    return now_myt().weekday() == 4  # Friday (MY time)

def append_unique_tag(text):
    ts = now_myt().strftime("%Y%m%d%H%M%S")
    zero_width = ''.join(chr(0x200B + int(c)) for c in ts)
    return text + zero_width

# --- KILL SWITCH ---
if os.getenv("BOT_ENABLED", "true").lower() != "true":
    exit(0)

# --- PRAYER TIME CHECK ---
if not is_before_maghrib():
    exit(0)

# --- TWITTER CLIENT ---
client = tweepy.Client(
    consumer_key=os.environ["TW_API_KEY"],
    consumer_secret=os.environ["TW_API_SECRET"],
    access_token=os.environ["TW_ACCESS_TOKEN"],
    access_token_secret=os.environ["TW_ACCESS_SECRET"]
)

# =========================
# 🕌 FRIDAY: QUR'AN + HADITH
# =========================
if is_friday():
    try:
        # --- QUR'AN ---
        q = random.choice(json.load(open("data/quran.json", encoding="utf-8")))
        quran_text = (
            f"📖 QS. {q['surah']}: {q['ayah']}\n\n"
            f"{q['arabic']}\n\n"
            f"🇮🇩 {q['indonesian']}\n\n"
            f"🇬🇧 {q['english']}"
        )
        client.create_tweet(text=append_unique_tag(quran_text))
        send_telegram(quran_text)

        # --- HADITH ---
        h = random.choice(json.load(open("data/hadith.json", encoding="utf-8")))
        hadith_text = (
            f"📜 Hadith ({h['source']})\n\n"
            f"{h['arabic']}\n\n"
            f"🇮🇩 {h['indonesian']}\n\n"
            f"🇬🇧 {h['english']}"
        )
        client.create_tweet(text=append_unique_tag(hadith_text))
        send_telegram(hadith_text)

    except Exception as e:
        alert_admin(f"Friday post failed:\n{e}")

# =========================
# 📜 NORMAL DAYS: PANTUN
# =========================
else:
    try:
        pantun, _ = get_pantun_safe()
        main = client.create_tweet(text=append_unique_tag(pantun))

        # English translation thread
        translation = translate_to_english(pantun)
        client.create_tweet(
            text=translation,
            in_reply_to_tweet_id=main.data["id"]
        )

        send_telegram(pantun + "\n\n🇬🇧 " + translation)

    except Exception as e:
        alert_admin(f"Pantun post failed:\n{e}")
