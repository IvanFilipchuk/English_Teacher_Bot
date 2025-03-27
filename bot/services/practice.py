from datetime import datetime, timedelta
from database.session import get_db
from database.repositories import (
    UserRepository,
    WordRepository,
    UserSettingsRepository
)
from bot.services.ai_service import AIService
from database.models import PracticeSession


class PracticeService:
    def __init__(self):
        self.ai_service = AIService()

    def get_practice_settings(self, user_id):
        """Get user's practice settings"""
        db = next(get_db())
        try:
            settings = UserSettingsRepository(db).get_by_user_id(user_id)
            return {
                'interval': settings.practice_interval if settings else 0,
                'last_practiced': settings.last_practice_time if settings else None
            }
        finally:
            db.close()

    def update_practice_settings(self, user_id, interval_minutes):
        """Update user's practice interval"""
        db = next(get_db())
        try:
            settings = UserSettingsRepository(db).update_practice_interval(
                user_id, interval_minutes
            )
            return settings
        finally:
            db.close()

    def get_random_word(self, user_id):
        """Get random word for practice"""
        db = next(get_db())
        try:
            return WordRepository(db).get_random_word(user_id)
        finally:
            db.close()

    async def evaluate_sentence(self, user_id, word_id, sentence):
        """Evaluate user's sentence using AI"""
        db = next(get_db())
        try:
            word = WordRepository(db).get_word_by_id(word_id)
            if not word:
                return None

            result = await self.ai_service.check_sentence(word.word, sentence)

            # Record practice session
            session = PracticeSession(
                user_id=user_id,
                word_id=word_id,
                user_sentence=sentence,
                ai_feedback=result['feedback'],
                is_correct=result['is_correct'],
                created_at=datetime.utcnow()
            )
            db.add(session)
            db.commit()

            # Update last practiced time
            settings_repo = UserSettingsRepository(db)
            settings = settings_repo.get_by_user_id(user_id)
            if settings:
                settings.last_practice_time = datetime.utcnow()
                db.commit()

            return result
        finally:
            db.close()

    def get_practice_history(self, user_id, limit=10):
        """Get user's practice history"""
        db = next(get_db())
        try:
            return db.query(PracticeSession) \
                .filter(PracticeSession.user_id == user_id) \
                .order_by(PracticeSession.created_at.desc()) \
                .limit(limit) \
                .all()
        finally:
            db.close()