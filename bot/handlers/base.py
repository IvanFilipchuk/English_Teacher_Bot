import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from database.session import get_db
from database.repositories import UserRepository


class BaseHandlers:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(update.effective_user)

            welcome_text = (
                f"✨ *Welcome {user.first_name} to English Teacher Bot!* ✨\n\n"
                "Your personal assistant for mastering English vocabulary!\n\n"
                "📚 *Main Features:*\n"
                "- Add & manage your vocabulary\n"
                "- Practice with spaced repetition\n"
                "- Get AI-powered feedback\n"
                "- Daily reminders"
            )

            keyboard = [
                [InlineKeyboardButton("📥 Add Word", callback_data="add_word"),
                 InlineKeyboardButton("📚 My Words", callback_data="list_words")],
                [InlineKeyboardButton("🎮 Practice Now", callback_data="start_practice"),
                 InlineKeyboardButton("⏰ Set Reminders", callback_data="set_schedule")]
            ]

            banner_path = os.path.join('assets', 'welcome.jpg')

            if os.path.exists(banner_path):
                await update.message.reply_photo(
                    photo=open(banner_path, 'rb'),
                    caption=welcome_text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await update.message.reply_text(
                    text=welcome_text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

        except Exception as e:
            await update.message.reply_text(
                "🚀 Welcome to English Teacher Bot!\n\n"
                "Let's start learning English!",
                parse_mode="Markdown"
            )
        finally:
            db.close()

    @staticmethod
    async def handle_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        try:
            if query.data == "add_word":
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="✏️ *Add New Word*\n\n"
                         "Send me the word in format:\n"
                         "`/add_word <english_word> <translation> [synonym] [example]`\n\n"
                         "*Example:*\n"
                         "`/add_word apple jabłko fruit \"An apple a day keeps the doctor away\"`",
                    parse_mode="Markdown"
                )
            elif query.data == "list_words":
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Use /my_words to list your vocabulary"
                )
            elif query.data == "start_practice":
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Use /practice to start a practice session"
                )
            elif query.data == "set_schedule":
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="Use /setschedule <minutes> to set practice reminders"
                )
        except Exception as e:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Error: {str(e)}"
            )

    @staticmethod
    def register_handlers(application):
        application.add_handler(CommandHandler("start", BaseHandlers.start))
        application.add_handler(CallbackQueryHandler(
            BaseHandlers.handle_main_menu,
            pattern="^(add_word|list_words|start_practice|set_schedule)$"
        ))