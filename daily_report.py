import os
from telegram import Bot
import openai

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def generate_daily_report():
    prompt = (
        "Bugün hiçbir önemli gelişme olmadığını belirtmek için, film/ajan/casus/dizi tarzında kısa ve göndermeli bir Telegram mesajı yaz. "
        "Hiçbir detay veya konuya spesifik atıf verme. "
        "Örnek: 'Sessizliğin gölgesi uzun olur.', 'The game is still afoot.', 'Dalgalar durgun, fırtına bekliyor.', 'We wait for the call.', 'The midnight bell hasn't tolled yet.', 'Bekçi uykuda.'"
    )
    try:
        chat_completion = client.chat.completions.create(
            model="gpt-4.1-mini",  # veya "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
        return chat_completion.choices[0].message.content.strip()
    except Exception as e:
        return f"NC: OpenAI HATASI — {e}"

def status_today():
    return os.path.isfile("status.txt")

bot = Bot(token=TELEGRAM_TOKEN)

if not status_today():
    ai_report = generate_daily_report()
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=ai_report)

if os.path.isfile("status.txt"):
    os.remove("status.txt")
