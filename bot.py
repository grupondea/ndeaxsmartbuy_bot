import os
import requests
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from google import genai

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

client = genai.Client(api_key=GEMINI_API_KEY)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    await update.message.reply_text("⏳ Recebi! Extraindo os dados...")

    prompt = f"""Extraia os dados abaixo e retorne APENAS um JSON sem markdown.
Campos: fn, ln, phone (E.164), email, event_name (use Purchase), value (número), currency (BRL/USD/EUR), event_time (ISO 8601), dob (MM/DD/YY), doby (ano 4 digitos
