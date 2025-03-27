from database.models import User

class UserRepository:
    def __init__(self, db):
        self.db = db

    def get_or_create(self, telegram_user):
        user = self.db.query(User).filter(User.telegram_id == telegram_user.id).first()
        if not user:
            user = User(
                telegram_id=telegram_user.id,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                username=telegram_user.username,
                language_code=getattr(telegram_user, 'language_code', 'en')
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def get(self, user_id):
        return self.db.query(User).filter(User.id == user_id).first()