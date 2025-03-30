import logging
from sqlalchemy import func
from database.models import Word

logger = logging.getLogger(__name__)

class WordRepository:
    def __init__(self, db):
        self.db = db

    def add_word(self, user_id, word_data):
        try:
            word = Word(
                user_id=user_id,
                word=word_data['word'],
                translation=word_data['translation'],
                synonym=word_data.get('synonym'),
                example_usage=word_data.get('example_usage')
            )
            self.db.add(word)
            self.db.commit()
            self.db.refresh(word)
            logger.info(f"Word added for user {user_id}: {word.word}")
            return word
        except Exception as e:
            logger.error(f"Error adding word for user {user_id}: {str(e)}")
            self.db.rollback()

    def get_user_words(self, user_id):
        try:
            words = self.db.query(Word).filter(Word.user_id == user_id).order_by(Word.word).all()
            logger.info(f"Retrieved {len(words)} words for user {user_id}")
            return words
        except Exception as e:
            logger.error(f"Error retrieving words for user {user_id}: {str(e)}")
            return []


    def get_word_by_id(self, word_id, user_id=None):
        try:
            query = self.db.query(Word).filter(Word.id == word_id)
            if user_id is not None:
                query = query.filter(Word.user_id == user_id)
            word = query.first()
            if word:
                logger.info(f"Retrieved word with id {word_id} for user {user_id}")
            else:
                logger.warning(f"Word with id {word_id} not found for user {user_id}")
            return word
        except Exception as e:
            logger.error(f"Error retrieving word with id {word_id} for user {user_id}: {str(e)}")
            return None

    def get_random_word(self, user_id):
        try:
            word = self.db.query(Word).filter(Word.user_id == user_id).order_by(func.random()).first()
            if word:
                logger.info(f"Random word retrieved for user {user_id}: {word.word}")
            else:
                logger.warning(f"No words found for user {user_id}")
            return word
        except Exception as e:
            logger.error(f"Error retrieving random word for user {user_id}: {str(e)}")
            return None

    def update_word(self, word_id, user_id, update_data):
        try:
            word = self.get_word_by_id(word_id, user_id)
            if not word:
                logger.warning(f"Word with id {word_id} not found for user {user_id}")
                return None

            for key, value in update_data.items():
                setattr(word, key, value)
            self.db.commit()
            self.db.refresh(word)
            logger.info(f"Word with id {word_id} updated for user {user_id}")
            return word
        except Exception as e:
            logger.error(f"Error updating word with id {word_id} for user {user_id}: {str(e)}")
            self.db.rollback()

    def delete_word(self, word_id, user_id):
        try:
            word = self.get_word_by_id(word_id, user_id)
            if word:
                self.db.delete(word)
                self.db.commit()
                logger.info(f"Word with id {word_id} deleted for user {user_id}")
                return True
            else:
                logger.warning(f"Word with id {word_id} not found for user {user_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting word with id {word_id} for user {user_id}: {str(e)}")
            self.db.rollback()
            return False