from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your English learning bot!")


async def echo(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text(f"GOT: {update.message.text}")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot is working")
    app.run_polling()


if __name__ == "__main__":
    main()
