import random, json
from openai import OpenAI
from hijri import get_hijri_theme

client = OpenAI()

def load_fallback():
    with open("data/fallback_pantun.json", encoding="utf-8") as f:
        fb = random.choice(json.load(f))
    return fb["emoji"] + "\n" + fb["text"]

def generate_pantun():
    language = random.choices(
        ["melayu", "indonesia", "aceh"], weights=[40, 40, 20]
    )[0]

    emoji = {"melayu":"🇲🇾","indonesia":"🇮🇩","aceh":"🏴"}[language]
    lang_desc = {
        "melayu":"Bahasa Melayu baku",
        "indonesia":"Bahasa Indonesia baku",
        "aceh":"Bahasa Aceh berunsur adat dan Islam"
    }

    prompt = f"""
Cipta satu pantun 4 baris.
Bahasa: {lang_desc[language]}
Tema: {get_hijri_theme()}
Rima ABAB atau AABB
Nada beradab
≤280 aksara
"""

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}],
        temperature=0.8
    )
    return emoji + "\n" + res.choices[0].message.content.strip()

def get_pantun_safe():
    try:
        return generate_pantun(), True
    except Exception:
        return load_fallback(), False
