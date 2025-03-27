import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from database.session import get_db
from database.repositories import UserRepository, WordRepository
from bot.services.practice import PracticeService

logger = logging.getLogger(__name__)


class PracticeHandlers:
    def __init__(self, application):
        self.application = application
        self.job_queue = application.job_queue
        self.practice_service = PracticeService()
        self.active_jobs = {}

    async def start_practice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(update.effective_user)
            word = self.practice_service.get_random_word(user.id)

            if not word:
                await update.message.reply_text("❌ Add words first!")
                return

            await update.message.reply_text(
                f"✏️ *Practice word:* {word.word}\n"
                f"*Translation:* {word.translation}\n\n"
                "Write a sentence with this word:",
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error("Practice error: %s", str(e))
            await update.message.reply_text("❌ Error starting practice")
        finally:
            db.close()

    async def check_sentence(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(update.effective_user)
            word = self.practice_service.get_random_word(user.id)

            if not word:
                await update.message.reply_text("❌ No word selected")
                return

            result = await self.practice_service.evaluate_sentence(
                user.id, word.id, update.message.text
            )

            if result['is_correct']:
                response = f"✅ *Correct!*\n\n{result['feedback']}"
            else:
                response = (
                    f"📝 *Suggestion:*\n{result['correction']}\n\n"
                    f"*Explanation:* {result['feedback']}"
                )

            await update.message.reply_text(response, parse_mode="Markdown")
        except Exception as e:
            logger.error("Check error: %s", str(e))
            await update.message.reply_text("❌ Error checking sentence")
        finally:
            db.close()

    async def set_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            interval = int(context.args[0]) if context.args else 0
            user = UserRepository(next(get_db())).get_or_create(update.effective_user)  # Get or create user

            if interval > 0:
                job = self.job_queue.run_repeating(
                    self._send_reminder,
                    interval=interval * 60,
                    chat_id=update.effective_chat.id,
                    data={"user_id": user.id}  # Use user.id instead of update.effective_user.id
                )
                self.active_jobs[user.id] = job
                await update.message.reply_text(f"🔔 Reminders set every {interval} minutes")
                logger.info(f"Job set for user {user.id} to repeat every {interval} minutes")
            else:
                if user.id in self.active_jobs:
                    self.active_jobs[user.id].schedule_removal()
                await update.message.reply_text("🔕 Reminders disabled")
                logger.info(f"Job removed for user {user.id}")
        except (ValueError, IndexError):
            await update.message.reply_text("Usage: /setschedule <minutes>")

    async def _send_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        user_id = context.job.data["user_id"]
        word = self.practice_service.get_random_word(user_id)

        logger.info(f"Attempting to send reminder for user {user_id} with word: {word}")

        if word:
            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=f"⏰ *Practice time!*\n\nWord: {word.word}\n\nWrite a sentence:",
                parse_mode="Markdown"
            )
        else:
            logger.warning(f"No word found for user {user_id} during reminder")

    def register_handlers(self):
        handlers = [
            CommandHandler("practice", self.start_practice),
            CommandHandler("setschedule", self.set_schedule),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_sentence)
        ]
        for handler in handlers:
            self.application.add_handler(handler)
