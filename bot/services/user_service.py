from sqlalchemy.orm import Session
from database.repositories.user_repo import UserRepository

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_by_username(self, username):
        return self.user_repo.get_by_username(username)

    def get_or_create(self, telegram_user):
        return self.user_repo.get_or_create(telegram_user)