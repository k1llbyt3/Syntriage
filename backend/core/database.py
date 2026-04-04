from sqlmodel import SQLModel, create_engine, Session
from .config import settings

DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session
