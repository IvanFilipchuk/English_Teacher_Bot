from sqlalchemy import Update
from telegram.ext import CommandHandler, ContextTypes

from bot.services.teacher_service import TeacherService
from database.repositories import WordRepository
from database.repositories.teacher_repo import TeacherRepository
from database.repositories.user_repo import UserRepository
from database.session import get_db

class TeacherHandlers:
    @staticmethod
    async def add_teacher(update, context):
        if not context.args:
            await update.message.reply_text(
                "📚 *How to add a teacher:*\n"
                "`/add_teacher <teacher_username>`\n"
                "*Example:* `/add_teacher john_doe`",
                parse_mode="Markdown"
            )
            return

        teacher_username = context.args[0].lstrip("@")
        db = next(get_db())
        try:
            service = TeacherService(db)
            student = UserRepository(db).get_or_create(update.effective_user)
            teacher = await service.add_teacher(student.id, teacher_username)

            if not teacher:
                await update.message.reply_text("❌ Teacher not found or you cannot add yourself as a teacher.")
                return

            await update.message.reply_text(f"✅ Teacher @{teacher_username} added successfully!")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            db.close()

    @staticmethod
    async def view_student_words(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text(
                "📚 *How to view student's words:*\n"
                "`/view_student_words <student_username>`\n"
                "*Example:* `/view_student_words john_doe`",
                parse_mode="Markdown"
            )
            return

        student_username = context.args[0].lstrip("@")
        db = next(get_db())
        try:
            teacher = UserRepository(db).get_or_create(update.effective_user)
            student = UserRepository(db).get_by_username(student_username)

            if not student:
                await update.message.reply_text("❌ Student not found.")
                return

            relation = TeacherRepository(db).get_teacher_students(teacher.id)
            if student.id not in [rel.student_id for rel in relation]:
                await update.message.reply_text("❌ You are not a teacher of this student.")
                return

            words = WordRepository(db).get_user_words(student.id)
            if not words:
                await update.message.reply_text(f"📭 *{student_username}'s word list is empty*", parse_mode="Markdown")
                return

            response_lines = [f"📚 *{student_username}'s Vocabulary*"]
            for word in words:
                response_lines.append(f"🔹 #{word.id} *{word.word}* - {word.translation}")
            response_lines.append("\nℹ️ Use `/word <id>` to see details\nExample: `/word 1`")

            max_message_length = 4096
            chunks = []
            current_chunk = ""
            for line in response_lines:
                if len(current_chunk) + len(line) + 1 <= max_message_length:
                    current_chunk += line + "\n"
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = line + "\n"
            if current_chunk:
                chunks.append(current_chunk.strip())

            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode="Markdown")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
        finally:
            db.close()

    @staticmethod
    def register_handlers(application):
        application.add_handler(CommandHandler("add_teacher", TeacherHandlers.add_teacher))
        application.add_handler(CommandHandler("view_student_words", TeacherHandlers.view_student_words))