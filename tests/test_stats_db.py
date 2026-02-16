"""Tests for statistics database functionality."""

import pytest
import tempfile
from pathlib import Path
from sqlmodel import select
from stats.db import init_db, get_session, Match, Event
from stats.collector import start_new_match, record_event, end_current_match


def test_match_event_cycle(tmp_path):
    """Test complete match and event recording cycle."""
    # Temporarily change the DB path
    from stats import db
    original_path = db.DB_PATH
    db.DB_PATH = tmp_path / "test_stats.db"
    
    try:
        # Initialize database
        init_db()
        
        # Start a new match
        start_new_match("simple")
        
        # Record some events
        for i in range(5):
            record_event(
                frame=i,
                piece="T",
                orientation=0,
                lines_cleared=i,
                combo=i,
                b2b=False,
                tspin=False,
                latency_ms=10.0
            )
        
        # End the match
        end_current_match()
        
        # Verify data was saved
        with get_session() as s:
            # Check match
            matches = s.exec(select(Match)).all()
            assert len(matches) == 1
            
            match = matches[0]
            assert match.agent == "simple"
            assert match.start_ts > 0
            assert match.end_ts is not None
            assert match.total_lines == 4  # Max lines_cleared
            assert match.max_combo == 4  # Max combo
            
            # Check events
            events = s.exec(select(Event)).all()
            assert len(events) == 5
            
            for i, event in enumerate(events):
                assert event.frame == i
                assert event.piece == "T"
                assert event.combo == i
                assert event.latency_ms == 10.0
                
    finally:
        # Restore original path
        db.DB_PATH = original_path


def test_multiple_matches(tmp_path):
    """Test recording multiple matches."""
    from stats import db
    original_path = db.DB_PATH
    db.DB_PATH = tmp_path / "test_multi_stats.db"
    
    try:
        init_db()
        
        # First match
        start_new_match("dellacherie")
        record_event(frame=0, piece="T", orientation=0, lines_cleared=1, combo=0, b2b=False, tspin=False, latency_ms=5.0)
        end_current_match()
        
        # Second match
        start_new_match("simple")
        record_event(frame=0, piece="I", orientation=0, lines_cleared=2, combo=1, b2b=True, tspin=False, latency_ms=8.0)
        end_current_match()
        
        # Verify both matches exist
        with get_session() as s:
            matches = s.exec(select(Match)).all()
            assert len(matches) == 2
            assert matches[0].agent == "dellacherie"
            assert matches[1].agent == "simple"
            
            events = s.exec(select(Event)).all()
            assert len(events) == 2
            
    finally:
        db.DB_PATH = original_path


def test_empty_database(tmp_path):
    """Test database initialization with empty state."""
    from stats import db
    original_path = db.DB_PATH
    db.DB_PATH = tmp_path / "test_empty.db"
    
    try:
        init_db()
        
        # Should have no matches initially
        with get_session() as s:
            matches = s.exec(select(Match)).all()
            assert len(matches) == 0
            
            events = s.exec(select(Event)).all()
            assert len(events) == 0
            
    finally:
        db.DB_PATH = original_path


def test_event_without_match(tmp_path):
    """Test that recording events without a match doesn't crash."""
    from stats import db
    original_path = db.DB_PATH
    db.DB_PATH = tmp_path / "test_no_match.db"
    
    try:
        init_db()
        
        # Try to record event without starting a match
        record_event(frame=0, piece="T", orientation=0, lines_cleared=0, combo=0, b2b=False, tspin=False, latency_ms=5.0)
        
        # Should not have saved any data
        with get_session() as s:
            events = s.exec(select(Event)).all()
            assert len(events) == 0
            
    finally:
        db.DB_PATH = original_path
