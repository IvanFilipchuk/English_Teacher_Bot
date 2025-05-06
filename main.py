import logging
from telegram.ext import ApplicationBuilder
from config.config import Config
from bot.handlers import base, dictionary, practice
from bot.handlers.teacher_handlers import TeacherHandlers

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

        TeacherHandlers.register_handlers(application)

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