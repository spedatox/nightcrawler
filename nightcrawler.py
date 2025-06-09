import os
import asyncio
import time
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

from telegram import Bot
import openai


# Ajan Ayarları
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY
OPENAI_MODEL = "gpt-4.1-mini"
client = AsyncOpenAI(api_key=OPENAI_API_KEY)

NIGHTCRAWLER_PERSONA = (
    "Sen NightCrawler adında bir gölge ajanısın. Ahmet Erol Bayrak'a çalışıyorsun, o senin patronun. Az ve öz konuşursun. "
    "Casus gibi, stratejik ve soğukkanlı cevaplar verirsin. Film repliği veya kod adı göndermeleriyle konuşabilirsin."
)

# === OSYM Kontrol Fonksiyonu ===
def selenium_check_osym_site():
    result = False
    trigger_line = ""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f"--user-data-dir=/tmp/chrome_userdata_{int(time.time())}")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        driver.get("https://sonuc.osym.gov.tr")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        page_text = soup.get_text().lower()
        for line in page_text.split('\n'):
            if "2025" in line and ("dgs" in line or "dikey geçiş sınavı" in line):
                result = True
                trigger_line = line.strip()[:120]
                break
    except Exception as e:
        trigger_line = f"Hata oluştu: {e}"
    finally:
        driver.quit()
    return result, trigger_line

# === Telegram'a Mesaj At ===
async def send_telegram(msg):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=msg)

# === OpenAI'dan Ajan Cümleleri Üret ===
async def generate_cryptic_message():
    prompt = (
        "Bir gelişmenin olduğunu haber vermek için, çok kısa ve sahibinin anlayacağı şekilde, film ya da dizilerdeki gibi kod/ajan repliği veya popüler kültür göndermesi içeren bir Telegram mesajı yaz."
    )
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"NC: Gölgede kıpırtı var. [OpenAI Hatası: {e}]"

async def generate_daily_report(last_trigger_time, last_trigger_info):
    if not last_trigger_time:
        extra = "Ses yok, iz yok, tüm gece temiz geçti."
    else:
        extra = f"Son tespit: {last_trigger_time.strftime('%H:%M:%S')} -> {last_trigger_info}"
    prompt = (
        "Bir casus gibi, çok kısa ve doğrudan günlük operasyon raporu Telegram mesajı yaz. "
        f"Sessiz yaşandıysa vurgula. Bilgi: {extra}"
    )
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except:
        return "NC: Gece sessiz geçti, kıpırtı yok."

# === Zaman ve Planlama ===
async def agent_loop():
    last_trigger_time = None
    last_trigger_info = ""
    daily_report_hour = 9
    daily_reported_date = None

    while True:
        now = datetime.now()

        # SAATLİK KONTROL
        found, trigger_line = selenium_check_osym_site()
        if found:
            msg = await generate_cryptic_message()
            msg += f"\n[Tetikleyici: {trigger_line}]"
            await send_telegram(msg)
            last_trigger_time = now
            last_trigger_info = trigger_line

        # GÜNLÜK RAPOR: Her gün belirli saatte
        if now.hour == daily_report_hour and (not daily_reported_date or daily_reported_date != now.date()):
            report = await generate_daily_report(last_trigger_time, last_trigger_info)
            await send_telegram(report)
            daily_reported_date = now.date()
            last_trigger_time = None
            last_trigger_info = ""

        await asyncio.sleep(60 * 60)

if __name__ == "__main__":
    asyncio.run(agent_loop())
