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

    def __repr__(self):
        return f"<Word(id={self.id}, word='{self.word}', translation='{self.translation}')>"