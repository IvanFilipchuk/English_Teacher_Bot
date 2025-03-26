from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from bot.services.dictionary import DictionaryService
from database.session import get_db


class DictionaryHandlers:
    @staticmethod
    async def add_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return

        if len(context.args) < 2:
            await update.message.reply_text(
                "📝 *How to add a word:*\n\n"
                "`/addword <english_word> <translation> [synonym] [example]`\n\n"
                "✨ *Example:*\n"
                "`/addword apple jabłko fruit \"An apple a day keeps the doctor away\"`",
                parse_mode="Markdown"
            )
            return

        word_data = {
            'word': context.args[0],
            'translation': context.args[1],
            'synonym': context.args[2] if len(context.args) > 2 else None,
            'example_usage': ' '.join(context.args[3:]) if len(context.args) > 3 else None
        }

        db = next(get_db())
        try:
            service = DictionaryService(db)
            word = service.add_word(update.effective_user, word_data)

            response = (
                "✅ *Word added successfully!*\n\n"
                f"• *Word:* `{word.word}`\n"
                f"• *Translation:* `{word.translation}`\n"
                f"• *Synonym:* `{word.synonym or 'None'}`\n"
                f"• *Example:* `{word.example_usage or 'None'}`\n\n"
                "🔄 You can edit it with /edit command"
            )
            await update.message.reply_text(response, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ *Error:* {str(e)}", parse_mode="Markdown")
        finally:
            db.close()

    @staticmethod
    async def list_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return

        db = next(get_db())
        try:
            service = DictionaryService(db)
            words = service.get_user_words(update.effective_user)

            if not words:
                await update.message.reply_text(
                    "📭 *Your word list is empty*\n\n"
                    "Add your first word with /addword command",
                    parse_mode="Markdown"
                )
                return

            response = "📚 *Your Vocabulary*\n\n"
            for word in words:
                response += f"🔹 #{word.id} *{word.word}* - {word.translation}\n"

            response += "\nℹ️ Use `/word <id>` to see details\nExample: `/word 1`"
            await update.message.reply_text(response, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ *Error:* {str(e)}", parse_mode="Markdown")
        finally:
            db.close()

    @staticmethod
    async def show_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return

        if not context.args:
            await update.message.reply_text(
                "ℹ️ *Usage:* `/word <word_id>`\nExample: `/word 1`",
                parse_mode="Markdown"
            )
            return

        db = next(get_db())
        try:
            word_id = int(context.args[0])
            service = DictionaryService(db)
            word = service.get_word_details(update.effective_user, word_id)

            if not word:
                await update.message.reply_text(
                    "❌ *Word not found*\n\n"
                    "Make sure the ID is correct and the word belongs to you",
                    parse_mode="Markdown"
                )
                return

            keyboard = [
                [
                    InlineKeyboardButton("✏️ Edit", callback_data=f"edit_word_{word.id}"),
                    InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_word_{word.id}")
                ]
            ]

            response = (
                "📖 *Word Details*\n\n"
                f"• *ID:* `{word.id}`\n"
                f"• *Word:* `{word.word}`\n"
                f"• *Translation:* `{word.translation}`\n"
                f"• *Synonym:* `{word.synonym or 'None'}`\n\n"
                f"*Example Usage:*\n`{word.example_usage or 'No example available'}`\n\n"
                f"*Added:* {word.added_at.strftime('%Y-%m-%d')}"
            )

            await update.message.reply_text(
                response,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except ValueError:
            await update.message.reply_text(
                "❌ *Invalid ID*\n\n"
                "Please provide a valid word ID (number)",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ *Error:* {str(e)}", parse_mode="Markdown")
        finally:
            db.close()

    @staticmethod
    async def edit_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return

        if len(context.args) < 3:
            await update.message.reply_text(
                "✏️ *How to edit a word:*\n\n"
                "`/edit <word_id> <field> <new_value>`\n\n"
                "✨ *Available fields:* `word`, `translation`, `synonym`, `example`\n\n"
                "*Example:*\n"
                "`/edit 1 example \"I love eating apples every morning\"`",
                parse_mode="Markdown"
            )
            return

        db = None
        try:
            word_id = int(context.args[0])
            field = context.args[1].lower()
            new_value = ' '.join(context.args[2:])

            valid_fields = {
                'word': 'word',
                'translation': 'translation',
                'synonym': 'synonym',
                'example': 'example_usage'
            }

            if field not in valid_fields:
                await update.message.reply_text(
                    "❌ *Invalid field*\n\n"
                    "Available fields: word, translation, synonym, example",
                    parse_mode="Markdown"
                )
                return

            db = next(get_db())
            service = DictionaryService(db)

            update_data = {valid_fields[field]: new_value}
            word = service.update_word(update.effective_user, word_id, update_data)

            if not word:
                await update.message.reply_text(
                    "❌ *Word not found or doesn't belong to you*",
                    parse_mode="Markdown"
                )
                return

            await update.message.reply_text(
                f"✅ *Word #{word_id} updated successfully!*\n\n"
                f"🔹 *{field.capitalize()}* changed to: `{new_value}`",
                parse_mode="Markdown"
            )
        except ValueError:
            await update.message.reply_text(
                "❌ *Invalid ID*\n\n"
                "Please provide a valid word ID (number)",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ *Error:* {str(e)}", parse_mode="Markdown")
        finally:
            if db:
                db.close()

    @staticmethod
    async def delete_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message:
            return

        if not context.args:
            await update.message.reply_text(
                "🗑️ *How to delete a word:*\n\n"
                "`/delete <word_id>`\n\n"
                "*Example:* `/delete 1`",
                parse_mode="Markdown"
            )
            return

        db = None
        try:
            word_id = int(context.args[0])
            db = next(get_db())
            service = DictionaryService(db)

            if service.delete_word(update.effective_user, word_id):
                await update.message.reply_text(
                    f"✅ *Word #{word_id} deleted successfully!*",
                    parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    "❌ *Word not found or doesn't belong to you*",
                    parse_mode="Markdown"
                )
        except ValueError:
            await update.message.reply_text(
                "❌ *Invalid ID*\n\n"
                "Please provide a valid word ID (number)",
                parse_mode="Markdown"
            )
        except Exception as e:
            await update.message.reply_text(f"❌ *Error:* {str(e)}", parse_mode="Markdown")
        finally:
            if db:
                db.close()

    @staticmethod
    async def handle_word_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        if query.data.startswith('edit_word_'):
            word_id = int(query.data.split('_')[2])
            await query.edit_message_text(
                f"✏️ Editing word #{word_id}\n\n"
                "Send me the edit command:\n"
                f"`/edit {word_id} <field> <new_value>`\n\n"
                "Available fields: word, translation, synonym, example",
                parse_mode="Markdown"
            )
        elif query.data.startswith('delete_word_'):
            word_id = int(query.data.split('_')[2])
            await query.edit_message_text(
                f"🗑️ Deleting word #{word_id}\n\n"
                "Are you sure? This cannot be undone!\n\n"
                f"Type `/delete {word_id}` to confirm",
                parse_mode="Markdown"
            )

    @staticmethod
    def register_handlers(application):
        application.add_handler(CommandHandler("add_word", DictionaryHandlers.add_word))
        application.add_handler(CommandHandler("my_words", DictionaryHandlers.list_words))
        application.add_handler(CommandHandler("word", DictionaryHandlers.show_word))
        application.add_handler(CommandHandler("edit", DictionaryHandlers.edit_word))
        application.add_handler(CommandHandler("delete", DictionaryHandlers.delete_word))
        application.add_handler(CallbackQueryHandler(
            DictionaryHandlers.handle_word_callbacks,
            pattern="^(edit_word_|delete_word_)"
        ))