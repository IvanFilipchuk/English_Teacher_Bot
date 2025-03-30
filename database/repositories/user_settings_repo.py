import datetime
from sqlalchemy.orm import Session
from database.models import UserSettings
from typing import List
import logging

logger = logging.getLogger(__name__)

class UserSettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_settings(self, user_id: int) -> UserSettings:
        settings = self.db.query(UserSettings).filter(UserSettings.user_id == user_id).first()

        if not settings:
            settings = UserSettings(
                user_id=user_id,
                practice_interval=0,
                notifications_enabled=True,
                last_word_id=None
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)
            logger.info(f"Created new settings for user {user_id}")

        return settings

    def update_last_word(self, user_id: int, word_id: int | None) -> None:
        settings = self.get_or_create_settings(user_id)
        logger.info(f"Updating last_word_id for user {user_id} to {word_id}")
        settings.last_word_id = word_id
        self.db.commit()
        self.db.refresh(settings)
        logger.info(f"Successfully updated last_word_id for user {user_id}: {settings.last_word_id}")

    def get_last_word_id(self, user_id: int) -> int | None:
        settings = self.get_or_create_settings(user_id)
        logger.info(f"Fetching last_word_id for user {user_id}: {settings.last_word_id}")
        return settings.last_word_id