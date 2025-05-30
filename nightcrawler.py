import os
import requests
from bs4 import BeautifulSoup
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai
from datetime import datetime

# Ayarlar
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

# Model sabit kaldı
OPENAI_MODEL = "gpt-4.1-mini"

# NightCrawler kişiliği tanımı
NIGHTCRAWLER_PERSONA = (
    "Sen NightCrawler adında bir gölge ajanısın. Ahmet Erol Bayrak' a Çalışıyorsun o senin patronun. Az konuşur, öz cevap verirsin. "
    "Her cevabın bir casus havası taşır. Gereksiz duygusallıktan uzak, stratejik, net ve kurnazsın. "
    "Kısa ama etkileyici konuşursun. Gerektiğinde film replikleriyle ya da kod adı gibi metaforlarla cevap ver. "
    "Kullandığın dil gizli görevdeki bir siber ajan gibi olmalı."
)

# Tetikleyici durumu kaydet
def touch_status():
    with open("status.txt", "w") as f:
        f.write(f"triggered:{datetime.now().isoformat()}")

# Sistem aktif mesajı
def generate_status_message():
    prompt = (
        "Sistemlerin aktif olduğuna dair çok kısa, havalı, ajan/film/casus repliği tarzında, gönderdiğimde sadece sahibinin anlayacağı bir Telegram mesajı yaz. "
        "Doğrudan olaya veya sınava gönderme yapma. "
    )
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except:
        return "NC: Devre aktif."

# Gizemli uyarı mesajı
def generate_cryptic_message():
    prompt = (
        "Bir gelişmenin olduğunu haber vermek için, çok kısa ve sahibinin anlayacağı şekilde, film ya da dizilerdeki gibi kod/ajan repliği veya popüler kültür göndermesi içeren bir Telegram mesajı yaz."
    )
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except:
        return "NC: Gölge devrede."

# Telegram'dan gelen mesajlara NightCrawler gibi yanıt ver
def handle_message(update: Update, context):
    user_message = update.message.text
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": NIGHTCRAWLER_PERSONA},
                {"role": "user", "content": user_message}
            ]
        )
        reply = resp.choices[0].message.content.strip()
    except:
        reply = "Sistemlerde bir aksaklık var. Sessizlik önerilir."

    update.message.reply_text(reply)

# Test mesajı modu
def handle_test_mode():
    bot = Bot(token=TELEGRAM_TOKEN)
    msg = generate_status_message()
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
    print("Test mesajı gönderildi.")

# Sayfa taraması
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

# Telegram üzerinden botu başlat
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

    # Arka planda tetikleyici olarak çalışacaksa
    if os.environ.get("BOT_ONLY", "false").lower() != "true":
        if check_osym_site():
            msg = generate_cryptic_message()
            bot = Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)
            touch_status()
        else:
            print("NightCrawler: No triggers found.")

    # Telegram botu her durumda aktif
    run_telegram_bot()
