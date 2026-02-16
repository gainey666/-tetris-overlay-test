"""Settings persistence using TinyDB."""

from tinydb import TinyDB, Query
from pathlib import Path
from .settings import Settings

DB_PATH = Path("settings.json")

def _db():
    """Get TinyDB instance."""
    return TinyDB(DB_PATH)

def load() -> Settings:
    """Load settings from disk, creating defaults if needed."""
    if not DB_PATH.exists():
        # Write defaults
        default_settings = Settings()
        save(default_settings)
        return default_settings
    
    db = _db()
    data = db.all()
    if not data:
        # Empty database, return defaults
        default_settings = Settings()
        save(default_settings)
        return default_settings
    
    # Take first (and only) document
    return Settings.from_dict(data[0])

def save(settings: Settings) -> None:
    """Save settings to disk."""
    db = _db()
    db.truncate()  # Keep only one document
    db.insert(settings.to_dict())
