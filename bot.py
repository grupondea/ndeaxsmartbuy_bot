import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from datetime import datetime
import anthropic

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text("⏳ Recebi! Extraindo os dados...")

    prompt = f"""Extraia os dados abaixo e retorne APENAS um JSON sem markdown.
Campos: fn, ln, phone (E.164), email, event_name (use Purchase), value (número), currency (BRL/USD/EUR), event_time (ISO 8601), dob (MM/DD/YY), doby (ano 4 digitos), gen (M/F), age (número), zip, ct, st, country (2 letras), madid.
Use null se não encontrado.
Texto: {msg}"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    texto = response.content[0].text.strip()
    clean = texto.replace("```json","").replace("```","").strip()
    data = json.loads(clean)

    params = {k: v for k, v in data.items() if v is not None}
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
        await update.message.reply_text("❌ Erro ao salvar na planilha. Tenta de novo!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
