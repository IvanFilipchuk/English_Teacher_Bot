from sqlalchemy import func, and_
from database.models import Word


class WordRepository:
    def __init__(self, db):
        self.db = db

    def add_word(self, user_id, word_data):
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
        return word

    def get_user_words(self, user_id):
        return self.db.query(Word).filter(Word.user_id == user_id).order_by(Word.word).all()

    def get_word_by_id(self, word_id, user_id=None):
        query = self.db.query(Word).filter(Word.id == word_id)
        if user_id:
            query = query.filter(Word.user_id == user_id)
        return query.first()

    def get_random_word(self, user_id):
        return self.db.query(Word).filter(Word.user_id == user_id).order_by(func.random()).first()

    def update_word(self, word_id, user_id, update_data):
        word = self.get_word_by_id(word_id, user_id)
        if not word:
            return None

        for key, value in update_data.items():
            setattr(word, key, value)

        self.db.commit()
        self.db.refresh(word)
        return word

    def delete_word(self, word_id, user_id):
        word = self.get_word_by_id(word_id, user_id)
        if word:
            self.db.delete(word)
            self.db.commit()
            return True
        return False