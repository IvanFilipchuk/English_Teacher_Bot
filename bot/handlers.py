from services.word_service import add_word_to_db
from telegram import Update
from telegram.ext import CallbackContext
from sqlalchemy.orm import Session
from database.session import get_db
from database.models import User, Word

async def start(update: Update, context: CallbackContext) -> None:

    await update.message.reply_text("Hello! I am your English learning bot! 🚀")

async def add_word_handler(update: Update, context: CallbackContext) -> None:

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add_word <word> <translation>")
        return

    word = context.args[0]
    translation = " ".join(context.args[1:])
    user_id = update.message.from_user.id

    add_word_to_db(user_id, word, translation)
    await update.message.reply_text(f"✅ Word '{word}' added with translation '{translation}'!")


async def my_words_handler(update: Update, context: CallbackContext) -> None:
    telegram_id = update.message.from_user.id
    db: Session = next(get_db())

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        await update.message.reply_text("You are not registered in the system.")
        return

    words = db.query(Word).filter(Word.user_id == user.id).all()
    if not words:
        await update.message.reply_text("Your word list is empty.")
        return

    max_word_length = max(len(word.word) for word in words) if words else 4
    max_translation_length = max(len(word.translation) for word in words) if words else 11

    table_header = f"{'ID':<4} | {'WORD':<{max_word_length}} | {'TRANSLATION':<{max_translation_length}}\n" + "-" * (
                10 + max_word_length + max_translation_length)

    word_list = "\n".join(
        [f"{word.id:<4} | {word.word:<{max_word_length}} | {word.translation:<{max_translation_length}}" for word in
         words])

    message = f"Here are your saved words:\n```\n{table_header}\n{word_list}\n```"

    await update.message.reply_text(message, parse_mode="MarkdownV2")



async def edit_word_handler(update: Update, context: CallbackContext) -> None:

    telegram_id = update.message.from_user.id
    db: Session = next(get_db())

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        await update.message.reply_text("You are not registered in the system.")
        return

    if len(context.args) < 3:
        await update.message.reply_text("Usage: /edit_word <id> <new_word> <new_translation>")
        return

    try:
        word_id = int(context.args[0])
        new_word = context.args[1]
        new_translation = context.args[2]
    except ValueError:
        await update.message.reply_text("Invalid ID format. Please enter a number.")
        return

    word = db.query(Word).filter(Word.id == word_id, Word.user_id == user.id).first()
    if not word:
        await update.message.reply_text("Word not found in your list.")
        return

    word.word = new_word
    word.translation = new_translation
    db.commit()

    await update.message.reply_text(f"✅ Word updated: {new_word} - {new_translation}")

async def delete_word_handler(update: Update, context: CallbackContext) -> None:

    telegram_id = update.message.from_user.id
    db: Session = next(get_db())

    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        await update.message.reply_text("You are not registered in the system.")
        return

    if len(context.args) < 1:
        await update.message.reply_text("Usage: /delete_word <id>")
        return

    try:
        word_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("Invalid ID format. Please enter a number.")
        return

    word = db.query(Word).filter(Word.id == word_id, Word.user_id == user.id).first()
    if not word:
        await update.message.reply_text("Word not found in your list.")
        return

    db.delete(word)
    db.commit()

    await update.message.reply_text(f"🗑️ Word deleted: {word.word} - {word.translation}")
