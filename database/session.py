from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config.config import Config

# Tworzymy połączenie do PostgreSQL
engine = create_engine(Config.SQLALCHEMY_DATABASE_URL)

# Sesja do obsługi zapytań do bazy
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Klasa bazowa dla modeli
Base = declarative_base()

# Funkcja pomocnicza do uzyskania sesji
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
