"""Statistics collector for per-frame events."""

import time
import uuid
from sqlmodel import select
from .db import get_session, Match, Event

_current_match_id: str | None = None
_frame_counter = 0

def start_new_match(agent_name: str):
    """Start tracking a new match."""
    global _current_match_id, _frame_counter
    _current_match_id = str(uuid.uuid4())
    _frame_counter = 0
    with get_session() as s:
        s.add(Match(id=_current_match_id, start_ts=time.time(), agent=agent_name))
        s.commit()

def end_current_match():
    """End the current match and update final stats."""
    global _current_match_id
    if not _current_match_id:
        return
    
    with get_session() as s:
        stmt = select(Match).where(Match.id == _current_match_id)
        m = s.exec(stmt).first()
        if m:
            m.end_ts = time.time()
            # Calculate final stats from events
            events_stmt = select(Event).where(Event.match_id == _current_match_id)
            events = s.exec(events_stmt).all()
            
            if events:
                m.total_score = max(e.lines_cleared for e in events) * 100  # Simple scoring
                m.total_lines = max(e.lines_cleared for e in events)
                m.max_combo = max(e.combo for e in events)
                m.max_b2b = sum(1 for e in events if e.b2b)
            
            s.add(m)
            s.commit()
    
    _current_match_id = None

def record_event(frame: int,
                 piece: str,
                 orientation: int,
                 lines_cleared: int,
                 combo: int,
                 b2b: bool,
                 tspin: bool,
                 latency_ms: float):
    """Record a single frame event."""
    if not _current_match_id:
        return
    
    with get_session() as s:
        s.add(Event(
            match_id=_current_match_id,
            frame=frame,
            ts=time.time(),
            piece=piece,
            orientation=orientation,
            lines_cleared=lines_cleared,
            combo=combo,
            b2b=b2b,
            tspin=tspin,
            latency_ms=latency_ms
        ))
        s.commit()

def get_current_match_id() -> str | None:
    """Get the current match ID."""
    return _current_match_id
