import os
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

client = Groq(api_key=GROQ_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text("Recebi! Extraindo os dados...")

    prompt = "Extraia os dados abaixo e retorne APENAS um JSON sem markdown. Campos: fn, ln, phone (E.164), email, event_name (use Purchase), value (numero), currency (BRL/USD/EUR), event_time (ISO 8601), dob (MM/DD/YY), doby (ano 4 digitos), gen (M/F), age (numero), zip, ct, st, country (2 letras), madid. Use null se nao encontrado. Texto: " + msg

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    texto = response.choices[0].message.content.strip()
    clean = texto.replace("```json", "").replace("```", "").strip()
    data = json.loads(clean)

    params = {k: v for k, v in data.items() if v is not None}
    r = requests.get(WEBHOOK_URL, params=params)
    result = r.json()

    if result.get("status") == "ok":
        nome = str(data.get("fn", "")) + " " + str(data.get("ln", ""))
        telefone = str(data.get("phone", ""))
        valor = str(data.get("value", ""))
        evento = str(data.get("event_name", ""))
        await update.message.reply_text("Salvo na planilha!\n\nNome: " + nome + "\nTelefone: " + telefone + "\nValor: R$ " + valor + "\nEvento: " + evento)
    else:
        await update.message.reply_text("Erro ao salvar. Tenta de novo!")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
