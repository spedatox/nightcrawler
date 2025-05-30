import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from openai import OpenAI
from datetime import datetime

# Ayarlar
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# OpenAI istemcisi (yeni stil)
client = OpenAI(api_key=OPENAI_API_KEY)

OPENAI_MODEL = "gpt-4-turbo"  # gpt-4.1-mini yerine geçerli bir model adı kullanılmalı

# NightCrawler kişiliği
NIGHTCRAWLER_PERSONA = (
    "Sen NightCrawler adında bir gölge ajanısın. Ahmet Erol Bayrak'a çalışıyorsun, o senin patronun. Az konuşur, öz cevap verirsin. "
    "Her cevabın bir casus havası taşır. Gereksiz duygusallıktan uzak, stratejik, net ve kurnazsın. "
    "Kısa ama etkileyici konuşursun. Gerektiğinde film replikleriyle ya da kod adı gibi metaforlarla cevap ver. "
    "Kullandığın dil gizli görevdeki bir siber ajan gibi olmalı."
)


# Durum kaydı
def touch_status():
    with open("status.txt", "w") as f:
        f.write(f"triggered:{datetime.now().isoformat()}")

# Ajan tarzında sistem aktif mesajı
def generate_status_message():
    prompt = (
        "Sistemlerin aktif olduğuna dair çok kısa, havalı, ajan/film/casus repliği tarzında, gönderdiğimde sadece sahibinin anlayacağı bir Telegram mesajı yaz. "
        "Doğrudan olaya veya sınava gönderme yapma. "
    )
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"NC: Devre aktif. [Hata: {e}]"

# Ajan tarzında gelişme bildirimi
def generate_cryptic_message():
    prompt = (
        "Bir gelişmenin olduğunu haber vermek için, çok kısa ve sahibinin anlayacağı şekilde, film ya da dizilerdeki gibi kod/ajan repliği veya popüler kültür göndermesi içeren bir Telegram mesajı yaz."
    )
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"NC: Gölge devrede. [Hata: {e}]"

# Telegram mesajlarına yanıt
def handle_message(update: Update, context):
    user_message = update.message.text
    try:
        resp = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": NIGHTCRAWLER_PERSONA},
                {"role": "user", "content": user_message}
            ]
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as e:
        reply = f"Sistemlerde bir aksaklık var. Sessizlik önerilir.\n[Hata: {e}]"

    update.message.reply_text(reply)

# Test modu mesajı
def handle_test_mode():
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = generate_status_message()
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    print("Test mesajı gönderildi.")

# ÖSYM site kontrolü
def check_osym_site():
    url = "https://sonuc.osym.gov.tr"
    try:
        res = requests.get(url, timeout=15)
        if res.status_code != 200:
            print(f"NightCrawler: Web sitesine ulaşılamadı. Status code: {res.status_code}")
            return False
        soup = BeautifulSoup(res.text, 'html.parser')
        page_text = soup.get_text().lower()
        for line in page_text.split('\n'):
            if "2025" in line and ("dgs" in line or "dikey geçiş sınavı" in line):
                return True
    except Exception as e:
        print(f"NightCrawler: Siteye erişim başarısız: {e}")
    return False

# Telegram bot başlat
def run_telegram_bot():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    updater.start_polling()
    print("NightCrawler: Telegram bağlantısı aktif.")
    updater.idle()

# Ana kontrol
if __name__ == "__main__":
    if os.environ.get("TEST_MODE", "false").lower() == "true":
        handle_test_mode()
        exit(0)

    if os.environ.get("BOT_ONLY", "false").lower() != "true":
        if check_osym_site():
            msg = generate_cryptic_message()
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            touch_status()
        else:
            print("NightCrawler: No triggers found.")

    run_telegram_bot()
