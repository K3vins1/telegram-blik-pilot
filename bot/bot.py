import os
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
BACKEND_URL = os.getenv("BACKEND_URL")

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot działa! Użyj /pay aby rozpocząć płatność testową."
    )

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND_URL}/create_transaction",
            json={"user_id": user_id, "amount": 5.00}
        )

    transaction_id = r.json()["transaction_id"]

    user_states[user_id] = {
        "state": "awaiting_code",
        "transaction_id": transaction_id
    }

    await update.message.reply_text("Podaj 6‑cyfrowy kod BLIK:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()

    if user_id in user_states and user_states[user_id]["state"] == "awaiting_code":
        if not text.isdigit() or len(text) != 6:
            await update.message.reply_text("Kod musi mieć 6 cyfr.")
            return

        transaction_id = user_states[user_id]["transaction_id"]

        async with httpx.AsyncClient() as client:
            await client.post(
                f"{BACKEND_URL}/send_blik_code",
                json={"transaction_id": transaction_id, "blik_code": text}
            )

        await update.message.reply_text(
            "Kod wysłany! Potwierdź płatność w aplikacji banku."
        )

        del user_states[user_id]
        return

    await update.message.reply_text("Użyj /pay aby rozpocząć.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
