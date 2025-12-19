import os
import json
import random
import datetime
from datetime import datetime as dt

import tweepy

from pantun_ai import get_pantun_safe
from prayer_time import is_before_maghrib
from telegram import send_telegram

# --- KILL SWITCH ---
if os.getenv("BOT_ENABLED", "true").lower() != "true":
    print("Bot disabled via BOT_ENABLED. Exiting.")
    exit(0)

# --- PRAYER TIME CHECK ---
if not is_before_maghrib():
    print("Too close to Maghrib, skipping post.")
    exit(0)

# --- TWITTER CLIENT ---
client = tweepy.Client(
    consumer_key=os.environ["TW_API_KEY"],
    consumer_secret=os.environ["TW_API_SECRET"],
    access_token=os.environ["TW_ACCESS_TOKEN"],
    access_token_secret=os.environ["TW_ACCESS_SECRET"]
)

# --- HELPER: APPEND INVISIBLE UNIQUE TAG ---
def append_unique_tag(text):
    ts = dt.utcnow().strftime("%Y%m%d%H%M%S")
    # Convert each digit to zero-width char
    zero_width = ''.join(chr(0x200B + int(c)) for c in ts)
    return text + zero_width

# --- HELPER: IS FRIDAY ---
def is_friday():
    return dt.utcnow().weekday() == 4  # Monday=0, Friday=4

# --- POSTING LOGIC ---
if is_friday():
    # Load Quran verses safely
    try:
        with open("data/quran.json", encoding="utf-8") as f:
            quran = random.choice(json.load(f))
    except FileNotFoundError:
        quran = "📖 \"Sesungguhnya bersama kesulitan ada kemudahan.\" (QS. Al-Insyirah: 6)"

    tweet_text = append_unique_tag(quran)
    try:
        client.create_tweet(text=tweet_text)
        print("Qur'an post sent successfully.")
    except tweepy.errors.Forbidden as e:
        print("Twitter duplicate / forbidden error:", e)

    send_telegram(tweet_text)

else:
    pantun, ai_used = get_pantun_safe()
    tweet_text = append_unique_tag(pantun)
    try:
        client.create_tweet(text=tweet_text)
        print("Pantun post sent successfully.")
    except tweepy.errors.Forbidden as e:
        print("Twitter duplicate / forbidden error:", e)

    send_telegram(tweet_text)
