import os, json, random
from datetime import datetime
import tweepy
from pantun_ai import get_pantun_safe
from prayer_time import is_before_maghrib
from telegram import send_telegram

if os.getenv("BOT_ENABLED","true").lower() != "true":
    exit(0)

if not is_before_maghrib():
    exit(0)

client = tweepy.Client(
    consumer_key=os.environ["TW_API_KEY"],
    consumer_secret=os.environ["TW_API_SECRET"],
    access_token=os.environ["TW_ACCESS_TOKEN"],
    access_token_secret=os.environ["TW_ACCESS_SECRET"]
)

def is_friday():
    return datetime.utcnow().weekday() == 4

if is_friday():
    quran = random.choice(json.load(open("data/quran.json",encoding="utf-8")))
    client.create_tweet(text=quran)
    send_telegram(quran)
else:
    pantun, _ = get_pantun_safe()
    tweet = client.create_tweet(text=pantun)
    send_telegram(pantun)
