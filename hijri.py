import requests
from datetime import datetime

HIJRI_THEMES = {
    1: "hijrah dan muhasabah",
    3: "akhlak Rasulullah",
    7: "taubat dan keinsafan",
    8: "istiqamah dalam ibadah",
    9: "iman, sabar, dan amal",
    12: "pengorbanan dan ketaatan"
}

def get_hijri_theme():
    today = datetime.utcnow().strftime("%d-%m-%Y")
    url = f"https://api.aladhan.com/v1/gToH/{today}"
    res = requests.get(url, timeout=10).json()
    month = int(res["data"]["hijri"]["month"]["number"])
    return HIJRI_THEMES.get(month, "nasihat kehidupan")
