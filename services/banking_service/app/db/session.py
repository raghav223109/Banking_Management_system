from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# engine = create_engine(settings.DATABASE_URL, echo=True)
# SQLAlchemy handles the postgresql dialect via psycopg2.

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    max_overflow=10,
    pool_size=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
