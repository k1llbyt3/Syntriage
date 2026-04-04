from sqlmodel import SQLModel, create_engine, Session
from .config import settings

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

def get_db():
    with Session(engine) as session:
        yield session
