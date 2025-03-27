import logging
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

from database.models import PracticeSession
from database.session import get_db
from database.repositories import UserRepository, WordRepository, UserSettingsRepository
from bot.services.ai_service import AIService
import asyncio

logger = logging.getLogger(__name__)


class PracticeHandlers:
    def __init__(self, application):
        self.application = application
        self.job_queue = application.job_queue
        self.active_sessions = {}

    async def initialize_scheduled_practices(self):
        """Initialize all active reminders on bot startup"""
        db = next(get_db())
        try:
            settings_repo = UserSettingsRepository(db)
            user_repo = UserRepository(db)

            active_settings = settings_repo.get_active_reminders()

            for settings in active_settings:
                user = user_repo.get(settings.user_id)
                if user and settings.practice_interval > 0:
                    self._schedule_practice(
                        user.telegram_id,
                        settings.user_id,
                        settings.practice_interval
                    )
        except Exception as e:
            logger.error(f"Initialization error: {e}")
        finally:
            db.close()

    def _schedule_practice(self, telegram_id, user_id, interval_minutes):
        """Helper to schedule practice sessions"""
        if telegram_id in self.active_sessions:
            self.active_sessions[telegram_id].schedule_removal()

        job = self.job_queue.run_repeating(
            self._send_practice_notification,
            interval=interval_minutes * 60,
            first=10,
            chat_id=telegram_id,
            data={'user_id': user_id},
            name=str(telegram_id))

        self.active_sessions[telegram_id] = job
        return job

    async def set_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for /setschedule command"""
        if not context.args:
            await update.message.reply_text(
                "Usage: /setschedule <minutes>\n"
                "Example: /setschedule 120 (for every 2 hours)\n"
                "Use 0 to disable reminders"
            )
            return

        try:
            interval = int(context.args[0])
            user = update.effective_user

            db = next(get_db())
            try:
                # Update database
                user_obj = UserRepository(db).get_or_create(user)
                settings = UserSettingsRepository(db).update_practice_interval(
                    user_obj.id, interval
                )

                # Update job queue
                if interval > 0:
                    self._schedule_practice(
                        user.id,
                        user_obj.id,
                        interval
                    )
                    msg = f"🔔 Practice reminders enabled every {interval} minutes"
                else:
                    if user.id in self.active_sessions:
                        self.active_sessions[user.id].schedule_removal()
                        del self.active_sessions[user.id]
                    msg = "🔕 Practice reminders disabled"

                await update.message.reply_text(msg)
            finally:
                db.close()
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number")

    async def _send_practice_notification(self, context: ContextTypes.DEFAULT_TYPE):
        """Send practice notification to user"""
        db = next(get_db())
        try:
            user_id = context.job.data['user_id']
            word = WordRepository(db).get_random_word(user_id)
            user = UserRepository(db).get(user_id)

            if not word or not user:
                return

            await context.bot.send_message(
                chat_id=context.job.chat_id,
                text=(
                    f"📚 *Time to practice!*\n\n"
                    f"Word: *{word.word}*\n"
                    f"Translation: {word.translation}\n\n"
                    f"Example: {word.example_usage or 'No example available'}\n\n"
                    "Please reply with a sentence using this word:"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Notification error: {e}")
        finally:
            db.close()

    async def start_practice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler for manual practice session"""
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(update.effective_user)
            word = WordRepository(db).get_random_word(user.id)

            if not word:
                await update.message.reply_text("You don't have any words to practice yet!")
                return

            await update.message.reply_text(
                f"Let's practice!\n\nWord: *{word.word}*\n"
                f"Meaning: {word.translation}\n\n"
                "Write a sentence using this word:",
                parse_mode="Markdown"
            )
        finally:
            db.close()

    async def check_sentence(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Evaluate user's sentence"""
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(update.effective_user)
            word = WordRepository(db).get_random_word(user.id)

            if not word:
                await update.message.reply_text("No active practice session")
                return

            ai_service = AIService()
            result = await ai_service.check_sentence(
                word.word,
                update.message.text
            )
            logger.info(f"AI response: {result}")

            # Save practice session
            session = PracticeSession(
                user_id=user.id,
                word_id=word.id,
                user_sentence=update.message.text,
                ai_feedback=result['feedback'],
                is_correct=result['is_correct'],
                created_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()

            # Prepare response
            if result['is_correct']:
                response = "✅ Great job! Your sentence is correct."
            else:
                response = (
                    "📝 Here's a suggested improvement:\n\n"
                    f"*Your sentence:* {update.message.text}\n"
                    f"*Suggestion:* {result['correction']}\n\n"
                    f"*Explanation:* {result['feedback']}"
                )

            await update.message.reply_text(response, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Sentence check error: {e}")
            await update.message.reply_text("❌ Error processing your sentence")
        finally:
            db.close()

    async def check_ai_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ai = AIService()
        test_result = await ai.check_sentence("run", "I runs every day")

        status = "✅ AI Service Working" if not test_result.get("error") else "❌ AI Service Failed"

        await update.message.reply_text(
            f"{status}\n"
            f"Test result: {test_result}"
        )

    def register_handlers(self):
        """Register all command and message handlers"""
        handlers = [
            CommandHandler("practice", self.start_practice),
            CommandHandler("setschedule", self.set_schedule),
            CommandHandler("aistatus", self.check_ai_status),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.check_sentence
            )
        ]
        for handler in handlers:
            self.application.add_handler(handler)