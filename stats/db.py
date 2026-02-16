"""SQLite database schema for statistics tracking."""

from sqlmodel import SQLModel, Field, create_engine, Session, select
from pathlib import Path
from typing import Optional
import uuid

DB_PATH = Path("stats.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

class Match(SQLModel, table=True):
    id: str = Field(primary_key=True)   # uuid4 string
    start_ts: float
    end_ts: Optional[float] = None
    agent: str
    total_score: int = 0
    total_lines: int = 0
    max_combo: int = 0
    max_b2b: int = 0

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    match_id: str = Field(foreign_key="match.id")
    frame: int
    ts: float
    piece: str
    orientation: int
    lines_cleared: int
    combo: int
    b2b: bool
    tspin: bool
    latency_ms: float

def init_db():
    """Initialize the database tables."""
    SQLModel.metadata.create_all(engine)

def get_session() -> Session:
    """Get a database session."""
    return Session(engine)
