import datetime

from sqlalchemy.orm import Session
from database.models import UserSettings
from typing import List


class UserSettingsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_settings(self, user_id: int) -> UserSettings:
        """Get or create settings for user"""
        settings = self.db.query(UserSettings) \
            .filter(UserSettings.user_id == user_id) \
            .first()

        if not settings:
            settings = UserSettings(
                user_id=user_id,
                practice_interval=0,
                notifications_enabled=True
            )
            self.db.add(settings)
            self.db.commit()
            self.db.refresh(settings)

        return settings

    def get_by_user_id(self, user_id: int) -> UserSettings:
        """Get settings by user ID"""
        return self.db.query(UserSettings) \
            .filter(UserSettings.user_id == user_id) \
            .first()

    def get_active_reminders(self) -> List[UserSettings]:
        """Get all users with active reminders"""
        return self.db.query(UserSettings) \
            .filter(
            UserSettings.practice_interval > 0,
            UserSettings.notifications_enabled == True
        ) \
            .all()

    def update_practice_interval(self, user_id: int, interval: int) -> UserSettings:
        """Update practice interval"""
        settings = self.get_or_create_settings(user_id)
        settings.practice_interval = interval
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def toggle_notifications(self, user_id: int, enable: bool) -> UserSettings:
        """Enable/disable notifications"""
        settings = self.get_or_create_settings(user_id)
        settings.notifications_enabled = enable
        self.db.commit()
        self.db.refresh(settings)
        return settings

    def update_last_practice(self, user_id: int) -> UserSettings:
        """Update last practice timestamp"""
        settings = self.get_or_create_settings(user_id)
        settings.last_practice_time = datetime.utcnow()
        self.db.commit()
        self.db.refresh(settings)
        return settings