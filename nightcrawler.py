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

def generate_status_message():
    prompt = (
        "Sistemlerin aktif olduğuna dair çok kısa, havalı, ajan/film/casus repliği tarzında, gönderdiğimde sadece sahibinin anlayacağı bir Telegram mesajı yaz. "
        "Doğrudan olaya veya sınava gönderme yapma. "
        "Örnekler: 'Sistemler devrede.', 'The night is darkest just before the dawn.', 'Gölgeler harekete geçti.', 'Ready when you are.', 'Execute Order 66.', 'Yonca tarlası hareketlendi.', 'Bring out the big guns.'"
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return "NC: Devre aktif."

def generate_cryptic_message():
    prompt = (
        "Bir gelişmenin olduğunu haber vermek için, çok kısa ve sahibinin anlayacağı şekilde, film ya da dizilerdeki gibi kod/ajan repliği veya popüler kültür göndermesi içeren bir Telegram mesajı yaz. "
        "Asla olayın detayını veya konu adını geçirme. "
        "Örnekler: 'Execute Order 66.', 'The storm begins.', 'Winter is coming.', 'Agent in play.', 'The owl spreads its wings.', 'Bring out the big guns.', 'This is just the beginning.', 'Let them come.' gibi."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-4.1-mini",
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return "NC: Gölge devrede."

def touch_status():
    with open("status.txt", "w") as f:
        f.write(f"triggered:{datetime.now().isoformat()}")

if os.environ.get("TEST_MODE", "false").lower() == "true":
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = generate_status_message()
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    print("Test mesajı gönderildi.")
    exit(0)

url = "https://sonuc.osym.gov.tr"
try:
    res = requests.get(url, timeout=15)
    if res.status_code != 200:
        print(f"NightCrawler: Web sitesine ulaşılamadı. Status code: {res.status_code}")
        exit(1)
    soup = BeautifulSoup(res.text, 'html.parser')
    page_text = soup.get_text().lower()
except Exception as e:
    print(f"NightCrawler: Siteye erişim başarısız: {e}")
    exit(1)

triggered = False
for line in page_text.split('\n'):
    if "2025" in line and ("dgs" in line or "dikey geçiş sınavı" in line):
        triggered = True
        break

if triggered:
    stealth_message = generate_cryptic_message()
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=stealth_message)
    touch_status()
else:
    print("NightCrawler: No triggers found.")
