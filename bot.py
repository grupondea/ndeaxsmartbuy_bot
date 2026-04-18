import os
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import google.generativeai as genai

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text("⏳ Recebi! Extraindo os dados...")

    prompt = f"""Extraia os dados abaixo e retorne APENAS um JSON sem markdown.
Campos: fn, ln, phone (E.164), email, event_name (use Purchase), value (número), currency (BRL/USD/EUR), event_time (ISO 8601), dob (MM/DD/YY), doby (ano 4 digitos), gen (M/F), age (número), zip, ct, st, country (2 letras), madid.
Use null se não encontrado.
Texto: {msg}"""

    response = model.generate_content(prompt)
    texto = response.text.strip()
    clean = texto.replace("```json","").replace("```","").strip()
    data = json.loads(clean)

    params = {{k: v for k, v in data.items() if v is not None}}
    r = requests.get(WEBHOOK_URL, params=params)
    result = r.json()

    if result.get("status") == "ok":
        await update.message.reply_text(
            f"✅ Salvo na planilha!\n\n"
            f"👤 {data.get('fn','')} {data.get('ln','')}\n"
            f"📱 {data.get('phone','')}\n"
            f"💰 R$ {data.get('value','')}\n"
            f"🛍️ {data.get('event_name','')}"
        )
    else:
        await update.message.reply_text("❌ Erro ao salvar. Tenta de novo!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
