from huggingface_hub import InferenceClient
from config.config import Config
import re
from database.session import get_db
from database.repositories import UserRepository, WordRepository
from datetime import datetime


class PracticeService:
    def __init__(self):
        try:
            self.client = InferenceClient(
                model=Config.MODEL_NAME,
                token=Config.HF_API_TOKEN
            )
        except Exception as e:
            print(f"Failed to initialize AI client: {str(e)}")
            self.client = None

    async def check_sentence(self, telegram_user, word_id: int, sentence: str) -> dict:
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(telegram_user)
            word = WordRepository(db).get_word_by_id(word_id)

            if not word or word.user_id != user.id:
                return {"error": "Word not found"}

            if not self.client:
                return {
                    "error": "AI service unavailable",
                    "is_correct": False,
                    "feedback": "Service temporarily unavailable",
                    "word": word.word,
                    "correction": ""
                }

            prompt = (
                f"Correct this sentence using the word '{word.word}': '{sentence}'. "
                f"Return only the corrected version or the original if already correct."
            )

            response = self.client.text_generation(
                prompt,
                max_new_tokens=50,
                temperature=0.5,
                stream=False
            ).strip()

            corrected = re.sub(r'^"|"$', '', response.strip())
            is_correct = corrected.lower() == sentence.lower()

            return {
                "is_correct": is_correct,
                "feedback": "The sentence is correct" if is_correct
                else f"Suggested correction: {corrected}",
                "word": word.word,
                "correction": corrected if not is_correct else ""
            }

        except Exception as e:
            return {
                "error": f"Analysis error: {str(e)}",
                "is_correct": False,
                "feedback": "Could not analyze your sentence",
                "word": word.word if word else "",
                "correction": ""
            }
        finally:
            db.close()

    def get_random_word(self, telegram_user):
        db = next(get_db())
        try:
            user = UserRepository(db).get_or_create(telegram_user)
            word = WordRepository(db).get_random_word(user.id)
            if word:
                word.last_practiced = datetime.utcnow()
                db.commit()
            return word
        finally:
            db.close()