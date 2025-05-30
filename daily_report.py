import os
from telegram import Bot
import openai

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
openai.api_key = OPENAI_API_KEY

def generate_daily_report():
    prompt = (
        "Bugün hiçbir hareket olmadığını kısaca, film veya ajan vari anonimliğe uygun, eğlenceli/kodlu gönderebileceğim bir Telegram mesajı yaz."
        "Örneğin: 'Ortam sessiz, gözcüler dinleniyor.', 'Bugün hiçbir gölge kıpırdamadı.', 'Gözleme devam, olay yok.' gibi."
    )
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return "NC: Görev devam ediyor."

def status_today():
    return os.path.isfile("status.txt")

bot = Bot(token=TELEGRAM_TOKEN)

if not status_today():
    ai_report = generate_daily_report()
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=ai_report)

# Ertesi gün sıfırlama için status.txt sil
if os.path.isfile("status.txt"):
    os.remove("status.txt")
