from database.session import SessionLocal
from database.models import Word, User


def add_word_to_db(user_id: int, word: str, translation: str):

    db = SessionLocal()

    user = db.query(User).filter(User.telegram_id == user_id).first()
    if not user:
        user = User(telegram_id=user_id, first_name="Unknown")
        db.add(user)
        db.commit()
        db.refresh(user)

    new_word = Word(user_id=user.id, word=word, translation=translation)
    db.add(new_word)
    db.commit()
    db.close()
