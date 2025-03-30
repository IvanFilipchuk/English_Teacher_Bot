import random
from datetime import datetime
from database.session import get_db
from database.repositories import WordRepository, UserSettingsRepository
from database.models import PracticeSession
from bot.services.ai_service import AIService
import logging

logger = logging.getLogger(__name__)

class PracticeService:
    def __init__(self):
        self.ai_service = AIService()
        self.daily_limit = 50

    async def evaluate_sentence(self, user_id: int, word_id: int, sentence: str) -> dict:
        db = next(get_db())
        try:
            if self._exceeded_daily_limit(user_id):
                return {
                    "is_correct": False,
                    "feedback": "Daily limit reached (50/day)",
                    "correction": sentence
                }

            word = WordRepository(db).get_word_by_id(word_id)
            if not word:
                return None

            result = await self.ai_service.check_sentence(word.word, sentence)

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

            return result
        except Exception as e:
            logger.error("Evaluation failed: %s", str(e))
            return {
                "is_correct": False,
                "feedback": "Evaluation error",
                "correction": sentence
            }
        finally:
            db.close()

    def _exceeded_daily_limit(self, user_id: int) -> bool:
        db = next(get_db())
        try:
            today = datetime.utcnow().date()
            count = db.query(PracticeSession)\
                .filter(
                    PracticeSession.user_id == user_id,
                    PracticeSession.created_at >= today
                )\
                .count()
            return count >= self.daily_limit
        finally:
            db.close()

    def get_random_word(self, user_id):
        db = next(get_db())
        try:
            words = WordRepository(db).get_user_words(user_id)
            if not words:
                return None

            recent_sessions = db.query(PracticeSession.word_id) \
                .filter(PracticeSession.user_id == user_id) \
                .order_by(PracticeSession.created_at.desc()) \
                .limit(5) \
                .all()

            recent_word_ids = {session.word_id for session in recent_sessions}

            available_words = [word for word in words if word.id not in recent_word_ids]

            if available_words:
                return random.choice(available_words)
            else:
                return random.choice(words)
        finally:
            db.close()