import asyncio
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from bot.services.practice_service import PracticeService
from database.session import get_db
from database.models import Word


class PracticeHandlers:
    def __init__(self, application):
        self.practice_service = PracticeService()
        self.user_schedules = {}
        self.application = application

    async def set_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                "Usage: /setschedule <minutes>\n"
                "Example: /setschedule 30 (for reminders every 30 minutes)"
            )
            return

        try:
            interval = int(context.args[0])
            user_id = update.effective_user.id

            if user_id in self.user_schedules:
                self.user_schedules[user_id].cancel()

            self.user_schedules[user_id] = asyncio.create_task(
                self._schedule_practice(update.effective_user, update.effective_chat.id, interval))

            await update.message.reply_text(
                f"✅ Practice reminders set for every {interval} minutes."
            )
        except ValueError:
            await update.message.reply_text("❌ Please enter a valid number")

    async def _schedule_practice(self, telegram_user, chat_id: int, interval: int):
        while True:
            await asyncio.sleep(interval * 60)
            db = next(get_db())
            try:
                word = self.practice_service.get_random_word(telegram_user)
                if word:
                    await self.application.bot.send_message(
                        chat_id=chat_id,
                        text=(
                            "⏰ *Time to practice!*\n\n"
                            f"Use this word in a sentence:\n"
                            f"*{word.word}* - {word.translation}\n\n"
                            f"Example: {word.example_usage or 'No example'}\n\n"
                            "Reply with your sentence below."
                        ),
                        parse_mode="MarkdownV2"
                    )
            except Exception as e:
                print(f"Schedule error: {str(e)}")
            finally:
                db.close()

    async def start_practice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            word = self.practice_service.get_random_word(update.effective_user)
            if word:
                await update.message.reply_text(
                    f"📝 *Practice word:* {word.word}\n"
                    f"*Translation:* {word.translation}\n\n"
                    "Write a sentence with this word:",
                    parse_mode="MarkdownV2"
                )
            else:
                await update.message.reply_text("❌ No words available. Add words first.")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")

    async def check_sentence(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sentence = update.message.text

        db = next(get_db())
        try:
            last_word = db.query(Word) \
                .filter(Word.user_id == update.effective_user.id) \
                .order_by(Word.last_practiced.desc()) \
                .first()

            if not last_word:
                await update.message.reply_text("❌ No active practice session")
                return

            result = await self.practice_service.check_sentence(
                update.effective_user,
                last_word.id,
                sentence
            )

            if result.get("error"):
                await update.message.reply_text(result["error"])
                return

            response = ("✅ *Correct!*" if result["is_correct"] else "❌ *Incorrect*") + "\n\n"
            response += f"*Feedback:* {result['feedback']}"

            await update.message.reply_text(response, parse_mode="MarkdownV2")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            db.close()

    def register_handlers(self):
        self.application.add_handler(CommandHandler("setschedule", self.set_schedule))
        self.application.add_handler(CommandHandler("practice", self.start_practice))
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.check_sentence
        ))