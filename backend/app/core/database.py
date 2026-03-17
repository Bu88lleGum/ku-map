from sqlmodel import create_engine, Session
from sqlalchemy import text
from typing import Generator

DATABASE_URL = "postgresql+psycopg://postgres:qwerty@localhost:5434/kumap"

engine = create_engine(DATABASE_URL)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        conn.commit()

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session