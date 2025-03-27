# # from huggingface_hub import InferenceClient
# #
# # MODEL_NAME = "tiiuae/falcon-7b-instruct"
# # API_TOKEN = "###########################"
# #
# # client = InferenceClient(model=MODEL_NAME, token=API_TOKEN)
# #
# # def test_model():
# #     prompt = "Correct this sentence: 'He go to school.' Return only the corrected version."
# #
# #     response = client.text_generation(
# #         prompt,
# #         max_new_tokens=50,
# #         temperature=0.5,
# #         stream=False
# #     )
# #
# #     print("Odpowiedź AI:", response.strip())
# #
# # if __name__ == "__main__":
# #     test_model()

import logging
from telegram.ext import ApplicationBuilder
from config.config import Config
from bot.handlers import base, dictionary, practice

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    try:
        logger.info("🚀 Starting bot initialization...")

        application = (
            ApplicationBuilder()
            .token(Config.TELEGRAM_BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )

        logger.info("✅ Application built successfully")

        base.BaseHandlers.register_handlers(application)
        dictionary.DictionaryHandlers.register_handlers(application)

        practice_handler = practice.PracticeHandlers(application)
        practice_handler.register_handlers()

        logger.info("🤖 Bot is ready and running")
        application.run_polling()

    except Exception as e:
        logger.error(f"🔥 Critical error: {e}")
    finally:
        logger.info("🛑 Bot stopped")


if __name__ == "__main__":
    main()