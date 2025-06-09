# NightCrawler – An AI Powered Silent Watcher Bot

**NightCrawler** is an asynchronous Python bot that periodically monitors a specified results webpage and notifies its operator (Ahmet Erol Bayrak) via Telegram when certain keywords are detected. Inspired by spy films, all messages are written in a cryptic, code-like style using OpenAI.

---

## 🔍 What It Does

- **Hourly Monitoring**  
  The bot checks a results webpage every hour (using headless Chrome via Selenium).

- **Keyword Detection**  
  It scans for lines that include both the year `"2025"` and any of the phrases:  
  `"e-yökdil"` or `"foreign language exam"` (case-insensitive).  

- **Cryptic Messaging**  
  When triggered, it uses the OpenAI API to generate a brief, film-style agent message that hints at the detected change, and sends it via Telegram.

- **Daily Reports**  
  Every morning at 09:00, the bot sends a short daily report – either confirming silence or summarizing the last detected event.

---

## 🧠 Technologies Used

- **Python 3.10+**
- **Selenium + BeautifulSoup** – for headless page scraping
- **Telegram Bot API** – for sending notifications
- **OpenAI GPT (async)** – for generating coded messages
- **WebDriver Manager** – to automatically manage ChromeDriver

---

## 🔧 Environment Variables

Make sure to set the following environment variables:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
OPENAI_API_KEY=your_openai_api_key
