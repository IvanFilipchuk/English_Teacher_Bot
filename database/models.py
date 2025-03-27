from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from .session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100))
    username = Column(String(100))
    language_code = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, onupdate=datetime.utcnow)

    words = relationship("Word", back_populates="user")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    practice_sessions = relationship("PracticeSession", back_populates="user")
class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word = Column(String(100), nullable=False)
    translation = Column(String(100), nullable=False)
    synonym = Column(String(100))
    example_usage = Column(Text)
    added_at = Column(DateTime, default=datetime.utcnow)
    last_practiced = Column(DateTime)

    user = relationship("User", back_populates="words")
    practice_sessions = relationship("PracticeSession", back_populates="word")
    def __repr__(self):
        return f"<Word(id={self.id}, word='{self.word}', translation='{self.translation}')>"


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    practice_interval = Column(Integer, default=60)  # w minutach
    last_practice_time = Column(DateTime)
    notifications_enabled = Column(Boolean, default=True)

    user = relationship("User", back_populates="settings")

class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    word_id = Column(Integer, ForeignKey("words.id"))
    user_sentence = Column(Text)
    ai_feedback = Column(Text)
    is_correct = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="practice_sessions")
    word = relationship("Word", back_populates="practice_sessions")