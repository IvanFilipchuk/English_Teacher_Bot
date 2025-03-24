# from huggingface_hub import InferenceClient
#
# MODEL_NAME = "tiiuae/falcon-7b-instruct"
# API_TOKEN = "###########################"
#
# client = InferenceClient(model=MODEL_NAME, token=API_TOKEN)
#
# def test_model():
#     prompt = "Correct this sentence: 'He go to school.' Return only the corrected version."
#
#     response = client.text_generation(
#         prompt,
#         max_new_tokens=50,
#         temperature=0.5,
#         stream=False
#     )
#
#     print("Odpowiedź AI:", response.strip())
#
# if __name__ == "__main__":
#     test_model()


from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os
from dotenv import load_dotenv
from bot.handlers import add_word_handler
from bot.handlers import start
from bot.handlers import my_words_handler
from bot.handlers import edit_word_handler
from bot.handlers import delete_word_handler

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_word", add_word_handler))
    app.add_handler(CommandHandler("my_words", my_words_handler))
    app.add_handler(CommandHandler("edit_word", edit_word_handler))
    app.add_handler(CommandHandler("delete_word", delete_word_handler))

    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
