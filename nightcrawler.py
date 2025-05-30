import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import openai
from datetime import datetime

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

def generate_cryptic_message(keyword):
    prompt = (
        f"Bir iletişimin, anahtar kelime olan '{keyword}'u belirtmeden, "
        f"film ya da dizi repliği veya casus kodu gibi yarı gizli, yarı sinematik kısa bir Telegram mesajı yaz. "
        f"Örneğin: 'Operasyon başlıyor.', 'Gölgeler harekete geçti.' veya 'Talimat için hazırız.' gibi."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return "NC: Görev devam ediyor."

def touch_status():
    with open("status.txt", "w") as f:
        f.write(f"triggered:{datetime.now().isoformat()}")

url = "https://example.com"
keywords = ["Example Domain"]

res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
page_text = soup.get_text().lower()

found_keyword = None
for kw in keywords:
    if kw.lower() in page_text:
        found_keyword = kw
        break

if found_keyword:
    stealth_message = generate_cryptic_message(found_keyword)
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=stealth_message)
    touch_status()  # Gün içinde trigger'landığını kaydet
else:
    print("NightCrawler: No triggers found.")
